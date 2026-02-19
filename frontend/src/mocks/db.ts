import { nanoid } from "nanoid";

import {
  BrandRecord,
  BrandAnalyticsResponse,
  BrandDetailResponse,
  BrandListResponse,
  BrandSpikesResponse,
  BrandSummaryResponse,
  CreateBrandRequest,
  CreateBrandResponse,
  DeleteBrandResponse,
  LiveMentionsResponse,
  Mention,
} from "@/types/api";

const initialBrands: BrandListResponse = [];

let brands: BrandListResponse = [...initialBrands];

const mentions: Record<string, Mention[]> = {};

const summaries: Record<string, BrandSummaryResponse> = {};

const spikes: Record<string, BrandSpikesResponse> = {};

const analytics: Record<string, BrandAnalyticsResponse> = {};

export function resetMocks() {
  brands = [...initialBrands];
}

export function mockCreateBrand(payload: CreateBrandRequest): Promise<CreateBrandResponse> {
  const brandId = `brand_${nanoid(6)}`;
  const slug = payload.brandName.toLowerCase().replace(/\s+/g, "-");
  const brand: BrandRecord = {
    name: payload.brandName,
    slug: slug,
    keywords: payload.keywords,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  brands = [brand, ...brands];
  return Promise.resolve({ name: brand.name, slug: brand.slug });
}

export function mockGetBrands(): Promise<BrandListResponse> {
  return Promise.resolve(brands);
}

export function mockGetBrand(brandId: string): Promise<BrandDetailResponse> {
  // Assuming brandId passed here is actually the slug or we simulate it
  const brand = brands.find((item) => item.slug === brandId || item.name === brandId);
  if (!brand) {
    return Promise.reject(new Error("Brand not found"));
  }
  return Promise.resolve(brand);
}

export function mockDeleteBrand(brandId: string): Promise<DeleteBrandResponse> {
  brands = brands.filter((item) => item.slug !== brandId);
  return Promise.resolve({ success: true });
}

export function mockGetLiveMentions(brandId: string): Promise<LiveMentionsResponse> {
  return Promise.resolve(mentions[brandId] ?? []);
}

export function mockGetBrandSummary(brandId: string): Promise<BrandSummaryResponse> {
  const summary = summaries[brandId] ?? {
    sentimentSummary: "",
    topics: [],
    spikeScore: 0,
    spikeDetected: false,
  };
  return Promise.resolve(summary);
}

export function mockGetBrandSpikes(brandId: string): Promise<BrandSpikesResponse> {
  return Promise.resolve(
    spikes[brandId] ?? {
      timeline: [],
      last24hCount: 0,
    }
  );
}

export function mockGetBrandAnalytics(brandId: string): Promise<BrandAnalyticsResponse> {
  return Promise.resolve(
    analytics[brandId] ?? {
      sentimentTrend: [],
      spikeTimeline: [],
      topics: [],
    }
  );
}
