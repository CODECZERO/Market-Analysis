/**
 * Smart matching configuration for accurate brand detection
 */
export interface BrandMatchConfig {
  // Fuzzy matching tolerance (0-1, higher = more lenient, default 0.8)
  fuzzyThreshold?: number;

  // Common misspellings to always match
  misspellings?: string[];

  // Industry/context for disambiguation (tech, ecommerce, finance, food, automotive)
  industry?: string;

  // Negative keywords to EXCLUDE (filter false positives)
  excludeKeywords?: string[];

  // External context sources
  linkedinUrl?: string;
  websiteUrl?: string;
  twitterHandle?: string;

  // Product/service names for context
  products?: string[];
}

export interface TrackedBrand {
  id: string;
  name: string;
  aliases?: string[];
  rssFeeds?: string[];
  keywords?: string[];
  competitors?: {
    id: string;
    name: string;
    keywords: string[];
  }[];

  // NEW: Smart matching configuration
  matchConfig?: BrandMatchConfig;
}
