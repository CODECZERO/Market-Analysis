export const queryKeys = {
  brands: () => ["brands"] as const,
  brand: (brandId: string) => ["brand", brandId] as const,
  brandSummary: (brandId: string) => ["brand", brandId, "summary"] as const,
  brandSpikes: (brandId: string) => ["brand", brandId, "spikes"] as const,
  liveMentions: (brandId: string) => ["brand", brandId, "live"] as const,
  analytics: (brandId: string) => ["brand", brandId, "analytics"] as const,
  entities: (brandId: string) => ["brand", brandId, "entities"] as const,
  suggestions: (brandId: string) => ["brand", brandId, "suggestions"] as const,
  trends: (brandId: string) => ["brand", brandId, "trends"] as const,
  influencers: (brandId: string) => ["brand", brandId, "influencers"] as const,
};
