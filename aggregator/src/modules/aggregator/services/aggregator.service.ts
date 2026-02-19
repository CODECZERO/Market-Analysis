import { randomUUID } from "node:crypto";
import { env } from "../../../config/env.js";
import { logger } from "../../../utils/logger.js";
import type { MentionProvider } from "../types/provider.js";
import type { MentionPlatform, NormalizedMention } from "../types/mention.js";
import { MentionNormalizerService } from "./normalizer.service.js";
import { MentionValidatorService } from "./validator.service.js";
import { MentionDeduplicationService } from "./deduplication.service.js";
import { RedisWriterService } from "./redis-writer.service.js";
import { SmartMatcherService } from "./smart-matcher.service.js";
import type { TrackedBrand } from "../../brands/types/brand.js";
import { BrandService } from "../../brands/services/brand.service.js";
import { MetricsService } from "../../metrics/metrics.service.js";

export type AggregatorTrigger = "scheduler" | "manual";

export interface AggregationSummary {
  brand: string;
  platform: MentionPlatform;
  fetchedCount: number;
  storedCount: number;
  invalidCount: number;
  duplicateCount: number;
  truncatedCount: number;
  fetchDurationMs: number;
  redisDurationMs: number;
  error?: string;
}

function buildSyntheticMention(brand: string, platform: MentionPlatform): NormalizedMention {
  return {
    id: `synthetic-${randomUUID()}`,
    brand,
    text: `${brand} update pending for ${platform}.`,
    timestamp: Date.now(),
    source: platform,
    metadata: {
      author: "system",
      url: "https://dashboard.local/synthetic",
      raw: {
        reason: "synthetic",
      },
      synthetic: true,
    },
  } satisfies NormalizedMention;
}

export interface AggregatorStatus {
  isRunning: boolean;
  lastRunAt?: string;
  lastRunDurationMs?: number;
  lastError?: string;
  lastSummaries: AggregationSummary[];
}

interface Subscriber {
  brand: TrackedBrand;
  isCompetitor: boolean;
  competitorInfo?: { id: string; name: string };
}

interface FetchTarget {
  keyword: string;
  keywords?: string[];
  subscribers: Subscriber[];
}

export class AggregatorService {
  private readonly status: AggregatorStatus = {
    isRunning: false,
    lastSummaries: [],
  };
  private trackedBrandsSnapshot = new Set<string>();

  constructor(
    private readonly brandService: BrandService,
    private readonly providers: MentionProvider[],
    private readonly normalizer: MentionNormalizerService,
    private readonly validator: MentionValidatorService,
    private readonly redisWriter: RedisWriterService,
    private readonly metrics: MetricsService,
    private readonly smartMatcher: SmartMatcherService,
  ) { }

  getStatus(): AggregatorStatus {
    return {
      ...this.status,
      lastSummaries: this.status.lastSummaries.map((summary) => ({ ...summary })),
    };
  }

  async triggerManualRun(): Promise<boolean> {
    if (this.status.isRunning) {
      return false;
    }

    await this.runCycle("manual");
    return true;
  }

  async runCycle(trigger: AggregatorTrigger = "scheduler"): Promise<void> {
    if (this.status.isRunning) {
      logger.warn({ trigger }, "Aggregator cycle already in progress");
      return;
    }

    this.status.isRunning = true;
    this.status.lastError = undefined;

    const cycleStart = Date.now();
    const cpuStart = process.cpuUsage();
    const summaries: AggregationSummary[] = [];
    // Buffer to hold mentions for fair scheduling: BrandName -> { brand: TrackedBrand; mentions: NormalizedMention[] }
    const brandBuffers = new Map<string, { brand: TrackedBrand; mentions: NormalizedMention[] }>();

    logger.info({ trigger }, "Aggregator cycle started");

    try {
      const brandFetchStart = Date.now();
      const brands = await this.brandService.getTrackedBrands();
      this.metrics.observeDbLatency("brands.findAll", Date.now() - brandFetchStart);

      const normalizedBrandNames = brands.map((brand) => brand.name.trim()).filter(Boolean);
      logger.debug({ trigger, brands: normalizedBrandNames }, "Loaded tracked brands");
      this.metrics.setBrandsTracked(brands.length);

      if (brands.length === 0) {
        if (this.trackedBrandsSnapshot.size > 0) {
          for (const previous of this.trackedBrandsSnapshot) {
            await this.redisWriter.purgeBrandData(previous);
          }
          this.trackedBrandsSnapshot.clear();
        }
        logger.warn({ trigger }, "No brands available. Aggregator cycle skipped.");
        return;
      }

      const currentBrandSet = new Set(normalizedBrandNames.map((name) => name.toLowerCase()));
      for (const previous of this.trackedBrandsSnapshot) {
        if (!currentBrandSet.has(previous)) {
          await this.redisWriter.purgeBrandData(previous);
        }
      }

      // Initialize buffers for all brands (so they exist even if no mentions found)
      for (const brand of brands) {
        if (!brandBuffers.has(brand.name)) {
          brandBuffers.set(brand.name, { brand, mentions: [] });
        }
        // Register in Redis
        try {
          const slug = await this.redisWriter.registerBrand(brand);
          logger.debug({ trigger, brand: brand.name, slug }, "Registered brand in Redis");
        } catch (error) {
          logger.error({ trigger, brand: brand.name, error }, "Failed to register brand in Redis");
        }
      }

      // --- PHASE 1: TARGET-CENTRIC FETCHING ---
      // 1. Collect all unique targets (User Brands + Competitors)
      const uniqueTargets = this.collectUniqueTargets(brands);
      logger.info({ count: uniqueTargets.length }, "Identified unique fetch targets");

      // 2. Fetch & Distribute
      for (const target of uniqueTargets) {
        await this.processTarget(target, trigger, summaries, brandBuffers);
      }

      // --- PHASE 2: FAIR DISPATCH ---
      await this.dispatchMentionsFairly(brandBuffers);

      const cycleDurationMs = Date.now() - cycleStart;
      const cpuUsage = process.cpuUsage(cpuStart);
      const memoryUsage = process.memoryUsage();

      logger.info({
        trigger,
        brands: brands.length,
        uniqueTargets: uniqueTargets.length,
        cycleDurationMs,
        cpuUsage,
        memoryUsage,
      }, "Aggregator cycle completed");
      this.trackedBrandsSnapshot = currentBrandSet;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      this.status.lastError = message;
      logger.error({ trigger, error }, "Aggregator cycle failed");
    } finally {
      this.status.lastSummaries = summaries.map((summary) => ({ ...summary }));
      this.status.lastRunAt = new Date().toISOString();
      this.status.lastRunDurationMs = Date.now() - cycleStart;
      this.status.isRunning = false;
    }
  }

  private async dispatchMentionsFairly(
    brandBuffers: Map<string, { brand: TrackedBrand; mentions: NormalizedMention[] }>
  ): Promise<void> {
    const BATCH_SIZE = 30; // Process 30 mentions from a brand, then switch
    let hasMentions = true;

    logger.info("Starting fair dispatch of mentions to worker queue");

    while (hasMentions) {
      hasMentions = false;

      for (const [brandName, data] of brandBuffers) {
        if (data.mentions.length === 0) {
          continue;
        }

        hasMentions = true;

        // Take a batch
        const batch = data.mentions.splice(0, BATCH_SIZE);

        try {
          await this.redisWriter.enqueueMentionChunks(data.brand, batch);
          logger.debug({ brand: brandName, batchSize: batch.length }, "Dispatched fair batch to worker");
        } catch (error) {
          logger.error({ brand: brandName, error }, "Failed to dispatch fair batch");
        }
      }
    }
  }

  // Collects unique fetch targets from all tracked brands and their competitors
  private collectUniqueTargets(brands: TrackedBrand[]): FetchTarget[] {
    const targetMap = new Map<string, FetchTarget>();

    for (const brand of brands) {
      // 1. The Main Brand Target
      const brandKey = brand.name.toLowerCase().trim();

      if (!targetMap.has(brandKey)) {
        targetMap.set(brandKey, {
          keyword: brand.name,
          subscribers: []
        });
      }
      targetMap.get(brandKey)!.subscribers.push({
        brand: brand,
        isCompetitor: false
      });

      // 2. Competitor Targets
      if (brand.competitors && brand.competitors.length > 0) {
        for (const comp of brand.competitors) {
          const compKey = comp.name.toLowerCase().trim();
          if (!targetMap.has(compKey)) {
            targetMap.set(compKey, {
              keyword: comp.name,
              keywords: comp.keywords, // Use competitor's specific keywords
              subscribers: []
            });
          }
          // Check if this subscriber is already added for this target (e.g. tracking same competitor twice locally?)
          // Usually rare, but subscriber is unique by brand ID essentially.
          targetMap.get(compKey)!.subscribers.push({
            brand: brand, // The SUBSCRIBER is the main brand
            isCompetitor: true,
            competitorInfo: {
              id: comp.id,
              name: comp.name
            }
          });
        }
      }
    }

    return Array.from(targetMap.values());
  }

  private async processTarget(
    target: FetchTarget,
    trigger: AggregatorTrigger,
    summaries: AggregationSummary[],
    brandBuffers: Map<string, { brand: TrackedBrand; mentions: NormalizedMention[] }>
  ): Promise<void> {
    const deduplicator = new MentionDeduplicationService();

    // Construct a temporary "Brand" config for the fetcher to use
    // Using the target keyword as the name.
    const fetchConfig: TrackedBrand = {
      id: "target-" + target.keyword.replace(/\s+/g, '-').toLowerCase(),
      name: target.keyword,
      keywords: target.keywords || [],
      aliases: [],
      rssFeeds: [],
      competitors: []
    };

    for (const provider of this.providers) {
      try {
        // Check if provider is enabled for ANY of the subscribers?
        // For now, we assume if the provider is active in general, we use it.
        // Ideally validation check: if (!target.subscribers.some(s => provider.isEnabled(s.brand))) continue;

        // FETCH ONCE
        const { summary, newMentions } = await this.processProvider(
          fetchConfig,
          provider,
          trigger,
          deduplicator,
          // We don't override brand name yet, we distribute clones later
        );

        // DISTRIBUTE RESULTS
        if (newMentions.length > 0) {
          for (const subscriber of target.subscribers) {
            // Verify provider enabled for this subscriber
            if (!provider.isEnabled(subscriber.brand)) continue;

            const mentionsForSubscriber = newMentions.map(m => {
              // Clone to avoid mutation between subscribers
              const clone = { ...m };
              // Contextualize for subscriber
              clone.brand = subscriber.brand.name;

              // Add Metadata
              clone.metadata = { ...clone.metadata };
              if (subscriber.isCompetitor && subscriber.competitorInfo) {
                clone.metadata.isCompetitor = true;
                clone.metadata.competitorId = subscriber.competitorInfo.id;
                clone.metadata.competitorName = subscriber.competitorInfo.name;
              }
              return clone;
            });

            // Add to Buffer
            if (brandBuffers.has(subscriber.brand.name)) {
              brandBuffers.get(subscriber.brand.name)!.mentions.push(...mentionsForSubscriber);
            }

            // Add partial summary
            summaries.push({
              brand: subscriber.brand.name,
              platform: provider.platform,
              fetchedCount: summary.fetchedCount, // Count is shared
              storedCount: summary.storedCount, // Shared
              invalidCount: summary.invalidCount,
              duplicateCount: summary.duplicateCount,
              truncatedCount: summary.truncatedCount,
              fetchDurationMs: summary.fetchDurationMs,
              redisDurationMs: summary.redisDurationMs
            });
          }
        }
      } catch (error) {
        logger.error({ target: target.keyword, provider: provider.platform, error }, "Failed to process target");
      }
    }
  }


  private async processProvider(
    brand: TrackedBrand,
    provider: MentionProvider,
    trigger: AggregatorTrigger,
    deduplicator: MentionDeduplicationService,
    extraOptions?: { overrideBrandName?: string; metadata?: Record<string, any> }
  ): Promise<{ summary: AggregationSummary; newMentions: NormalizedMention[] }> {
    const fetchStart = Date.now();
    const stopFetchTimer = this.metrics.startFetchTimer(provider.platform, brand.name);
    let normalizedMentions: NormalizedMention[] = [];
    let redisDurationMs = 0;
    let fetchTimerStopped = false;

    try {
      const rawMentions = await provider.fetchMentions(brand);
      const fetchDurationMs = Date.now() - fetchStart;
      stopFetchTimer();
      fetchTimerStopped = true;

      const cappedMentions = (rawMentions.length === 0)
        ? []
        : rawMentions.slice(0, env.aggregator.maxFetchLimit);
      const truncatedCount = rawMentions.length - cappedMentions.length;

      if (truncatedCount > 0) {
        logger.warn({ brand: brand.name, platform: provider.platform, truncatedCount }, "Provider results truncated to max fetch limit");
      }

      const stopNormalizationTimer = this.metrics.startNormalizationTimer(provider.platform, brand.name);
      try {
        const targetBrandName = extraOptions?.overrideBrandName || brand.name;
        normalizedMentions = cappedMentions.map((mention) => {
          const normalized = this.normalizer.normalize(mention, targetBrandName);
          if (extraOptions?.metadata) {
            normalized.metadata = { ...normalized.metadata, ...extraOptions.metadata };
          }
          return normalized;
        });
      } finally {
        stopNormalizationTimer();
      }

      const { valid, invalid } = this.validator.filterValid(normalizedMentions);
      if (invalid.length > 0) {
        this.metrics.recordInvalidMentions(brand.name, invalid.length, "schema");
      }

      const stopDedupTimer = this.metrics.startDedupTimer(brand.name);
      let uniqueMentions: NormalizedMention[] = [];
      let duplicateCount = 0;
      try {
        const dedupResult = deduplicator.deduplicate(valid);
        uniqueMentions = dedupResult.unique;
        duplicateCount = dedupResult.duplicates.length;
      } finally {
        stopDedupTimer();
      }

      if (duplicateCount > 0) {
        this.metrics.recordDuplicateMentions(brand.name, duplicateCount);
      }

      let mentionsToStore = uniqueMentions;

      // --- SMART MATCHING (replaces simple keyword filtering) ---
      // Uses fuzzy matching, typo detection, and context disambiguation
      const originalCount = mentionsToStore.length;
      mentionsToStore = mentionsToStore.filter(mention => {
        const result = this.smartMatcher.match(mention.text, brand);
        if (result.isMatch) {
          // Add match metadata for analytics and debugging
          mention.metadata = {
            ...mention.metadata,
            matchConfidence: result.confidence,
            matchType: result.matchType,
            matchedTerm: result.matchedTerm,
            matchReason: result.reason,
          };
        }
        // Only include matches with confidence >= 0.7
        return result.isMatch && result.confidence >= 0.7;
      });

      const filteredCount = originalCount - mentionsToStore.length;
      if (filteredCount > 0) {
        logger.info({
          brand: brand.name,
          platform: provider.platform,
          filteredCount,
          cacheStats: this.smartMatcher.getCacheStats(),
        }, `Smart matching filtered ${filteredCount}/${originalCount} mentions`);
      }

      const stopRedisTimer = this.metrics.startRedisWriteTimer(brand.name);
      const redisStart = Date.now();
      const storedCount = await this.redisWriter.writeMentions(mentionsToStore);
      redisDurationMs = Date.now() - redisStart;
      stopRedisTimer();

      this.metrics.incrementMentions(provider.platform, brand.name, storedCount);

      logger.info({
        brand: brand.name,
        platform: provider.platform,
        trigger,
        count: storedCount,
        invalid: invalid.length,
        duplicates: duplicateCount,
        truncated: truncatedCount,
        fetchDurationMs,
        redisWriteDurationMs: redisDurationMs,
      }, "Stored mentions in Redis");

      // REMOVED DIRECT ENQUEUEING HERE - returning mentions instead
      // const chunkLogStart = Date.now();
      // const { chunkCount, slug, queueKey, chunkSize } = await this.redisWriter.enqueueMentionChunks(brand, mentionsToStore);
      // ... (logging moved to dispatchMentionsFairly or implicit via actions)

      return {
        summary: {
          brand: brand.name,
          platform: provider.platform,
          fetchedCount: rawMentions.length,
          storedCount,
          invalidCount: invalid.length,
          duplicateCount,
          truncatedCount,
          fetchDurationMs,
          redisDurationMs,
        },
        newMentions: mentionsToStore, // Return the ready-to-process mentions
      };
    } catch (error) {
      const fetchDurationMs = Date.now() - fetchStart;
      if (!fetchTimerStopped) {
        stopFetchTimer();
      }

      const message = error instanceof Error ? error.message : "Unknown error";
      logger.warn({
        brand: brand.name,
        platform: provider.platform,
        trigger,
        error,
        fetchDurationMs,
      }, "Failed to fetch mentions from provider");

      return {
        summary: {
          brand: brand.name,
          platform: provider.platform,
          fetchedCount: 0,
          storedCount: 0,
          invalidCount: 0,
          duplicateCount: 0,
          truncatedCount: 0,
          fetchDurationMs,
          redisDurationMs,
          error: message,
        },
        newMentions: [],
      };
    }
  }
}
