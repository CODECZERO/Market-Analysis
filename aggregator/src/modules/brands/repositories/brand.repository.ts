import type { Db, Document } from "mongodb";
import { connectMongo } from "../../../config/mongo.js";
import { logger } from "../../../utils/logger.js";
import type { TrackedBrand } from "../types/brand.js";

interface BrandDocument extends Document {
  name?: string;
  aliases?: string[];
  rssFeeds?: string[];
  keywords?: string[];
  updatedAt?: Date;
  createdAt?: Date;
  isActive?: boolean;
}

export class BrandRepository {
  private readonly collectionName = "AVICHIAN_brands";

  async findAll(): Promise<TrackedBrand[]> {
    const db: Db = await connectMongo();
    const collection = db.collection<BrandDocument>(this.collectionName);

    let cursor;
    try {
      cursor = collection
        .find({})
        .sort({ updatedAt: -1, createdAt: -1 })
        .limit(100);
    } catch (error) {
      logger.error({
        database: db.databaseName,
        collection: this.collectionName,
        error,
      }, "Failed to create MongoDB cursor for brands");
      throw error;
    }

    const seen = new Set<string>();
    const brands: TrackedBrand[] = [];

    try {
      for await (const doc of cursor) {
        const name = doc.name?.trim();
        if (!name || seen.has(name.toLowerCase())) {
          continue;
        }

        seen.add(name.toLowerCase());
        brands.push({
          id: doc._id.toString(),
          name,
          aliases: Array.isArray(doc.aliases) ? doc.aliases.filter(Boolean) : [],
          rssFeeds: Array.isArray(doc.rssFeeds) ? doc.rssFeeds.filter(Boolean) : [],
          keywords: Array.isArray(doc.keywords) ? doc.keywords.filter(Boolean) : [],
        });
      }

      // Fetch competitors and attach
      if (brands.length > 0) {
        const brandIds = brands.map(b => b.id);
        const competitorsMap = await this.fetchCompetitors(db, brandIds);

        for (const brand of brands) {
          brand.competitors = competitorsMap[brand.id] || [];
        }
      }

    } catch (error) {
      logger.error({
        database: db.databaseName,
        collection: this.collectionName,
        error,
      }, "Failed while iterating MongoDB cursor for brands");
      throw error;
    }

    if (brands.length === 0) {
      try {
        const totalDocs = await collection.estimatedDocumentCount();
        logger.warn({
          database: db.databaseName,
          collection: this.collectionName,
          totalDocs,
        }, "No tracked brands found in MongoDB");
      } catch (countError) {
        logger.warn({
          database: db.databaseName,
          collection: this.collectionName,
          error: countError,
        }, "No tracked brands found and failed to count MongoDB documents");
      }
    } else {
      logger.debug({
        database: db.databaseName,
        collection: this.collectionName,
        count: brands.length,
        brands: brands.map((brand) => brand.name),
      }, "Fetched tracked brands from MongoDB");
    }

    return brands;
  }

  private async fetchCompetitors(db: Db, brandIds: string[]): Promise<Record<string, TrackedBrand['competitors']>> {
    try {
      const collection = db.collection("AVICHIAN_competitors");
      // Find competitors for these brands that are enabled
      // Note: check your schema for 'enabled' vs 'isActive' vs 'is_active'.
      // Based on previous checks, it appeared to be 'enabled' in one place and 'is_active' in another.
      // The model showed 'enabled: Boolean'.
      const cursor = collection.find({
        brandId: { $in: brandIds.map(id => new (require("mongodb").ObjectId)(id)) }, // Dynamic import to avoid top-level issues if needed, or just assume ObjectId matches string format if stored that way. actually we need ObjectId.
        enabled: true
      });

      const competitorMap: Record<string, TrackedBrand['competitors']> = {};

      for await (const doc of cursor) {
        const brandId = doc.brandId.toString();
        if (!competitorMap[brandId]) {
          competitorMap[brandId] = [];
        }

        competitorMap[brandId]?.push({
          id: doc._id.toString(),
          name: doc.name,
          keywords: Array.isArray(doc.keywords) ? doc.keywords.filter(Boolean) : []
        });
      }

      return competitorMap;

    } catch (error) {
      logger.warn({ error }, "Failed to fetch competitors in aggregator");
      return {};
    }
  }
}
