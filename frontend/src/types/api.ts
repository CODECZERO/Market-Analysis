/**
 * Smart matching configuration for accurate brand detection
 */
export interface BrandMatchConfig {
  // Fuzzy matching tolerance (0-1, higher = more lenient, default 0.8)
  fuzzyThreshold?: number;

  // Common misspellings to always match
  misspellings?: string[];

  // Industry/context for disambiguation (tech, ecommerce, finance, food, automotive, healthcare, gaming, social)
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

export interface CreateBrandRequest {
  brandName: string;
  keywords: string[];
  aliases?: string[];
  matchConfig?: BrandMatchConfig;
}

export interface CreateBrandResponse {
  name: string;
  slug: string;
}

export interface BrandRecord {
  name: string;
  slug: string;
  createdAt?: string;
  updatedAt?: string;
  keywords?: string[];
  aliases?: string[];
  matchConfig?: BrandMatchConfig;
}


export type BrandListResponse = BrandRecord[];
export type BrandDetailResponse = BrandRecord;

export interface MentionMetadata {
  author?: string;
  url?: string;
  [key: string]: unknown;
}

export interface Mention {
  id: string;
  brand: string;
  source: string;
  text: string;
  timestamp: number;
  createdAt: string;
  sentiment: "positive" | "neutral" | "negative";
  url?: string;
  metadata?: MentionMetadata;
}

export type LiveMentionsResponse = Mention[];

export interface SentimentBreakdown {
  positive: number;
  neutral: number;
  negative: number;
  score: number;
}

export interface ClusterSummary {
  id: string;
  label: string;
  mentions: number;
  spike?: boolean;
}

export interface BrandSummaryResponse {
  brand: string;
  generatedAt: string;
  totalChunks: number;
  totalMentions: number;
  sentiment: SentimentBreakdown;
  dominantTopics: string[];

  // Business Intelligence Fields
  feature_requests?: string[];
  pain_points?: string[];
  churn_risks?: string[];
  recommended_actions?: string[];
  avgLeadScore?: number;

  clusters: ClusterSummary[];
  spikeDetected: boolean;
  summary: string;
  chunkSummaries: string[];
  healthScore?: number;
}

export interface SpikeSample {
  timestamp: string;
  spikeScore: number;
  mentionCount: number;
  threshold: number;
}

export interface BrandSpikesResponse {
  timeline: SpikeSample[];
  last24hCount: number;
  brand?: string;
  redisLatencySeconds?: number;
}

export interface SentimentTrendPoint {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
}

export interface BrandAnalyticsResponse {
  sentimentTrend: SentimentTrendPoint[];
  spikeTimeline: SpikeSample[];
  topics: { term: string; weight: number }[];
}

export interface DeleteBrandResponse {
  success: boolean;
}


// Money Mode / Leads Types
export interface Lead {
  id: string;
  mentionId: string;
  salesIntentScore: number;
  intentType: string;
  confidence: number;
  painPoint: string | null;
  leadScore: number;
  status: string;
  generatedPitch: string | null;
  sourcePlatform: string | null;
  sourceText: string | null;
  sourceAuthor: string | null;
  createdAt: string;
}

export interface LeadStats {
  totalLeads: number;
  newLeads: number;
  qualifiedLeads: number;
  convertedLeads: number;
  avgLeadScore: number;
}

export interface LeadsListResponse {
  leads: Lead[];
  total: number;
  page: number;
  totalPages: number;
}

// Market Gap / Competitor Types
export interface Competitor {
  id: string;
  name: string;
  slug: string;
  brandId?: string; // Added
  website?: string; // Added
  keywords?: string[]; // Added
  enabled?: boolean; // Changed from is_active to match backend
  createdAt?: string; // Added
  metrics?: { // Added
    sentimentScore: number;
    mentionCount: number;
  };
  totalComplaints?: number;
  avgPainLevel?: number;
  shareOfVoice?: number;
  sentimentScore?: number; // kept for compatibility
  color?: string;
  weaknesses?: string[];
  strengths?: string[];
}

export interface WeaknessAnalysis {
  competitorId: string;
  competitorName: string;
  totalComplaints: number;
  categoryBreakdown: {
    category: string;
    count: number;
    percentage: number;
    avgPainLevel: number;
    topIssues: string[];
  }[];
  opportunities: string[];
}

export interface CompetitorsListResponse {
  competitors: Competitor[];
}

// Entity Types
export interface Entity {
  name: string;
  count: number;
}

export interface EntityData {
  people: Entity[];
  companies: Entity[];
  products: Entity[];
}

export interface Suggestion {
  suggestion: string;
  count: number;
}

export interface SuggestionsResponse {
  suggestions: Suggestion[];
}

// Trend Prediction Types
export interface TrendPrediction {
  trend: "improving" | "declining" | "stable";
  percentChange: number;
  prediction: string;
  confidence: number;
}

// Influencer Types
export interface Influencer {
  id: string;
  brand: string;
  source: string;
  text: string;
  timestamp: number;
  createdAt: string;
  sentiment: "positive" | "neutral" | "negative";
  metadata?: {
    author?: string;
    url?: string;
    followers?: number;
  };
  author_followers: number;
  influence_score: number;
}

export interface InfluencersResponse {
  influencers: Influencer[];
  brand: string;
  redisLatencySeconds: number;
}

export interface ComparisonData {
  shareOfVoice: { name: string; value: number; color: string }[];
  sentimentComparison: { name: string; positive: number; neutral: number; negative: number }[];
}

export interface LaunchPrediction {
  is_launch: boolean;
  product_name: string;
  success_score: number;
  reason: string;
  brand: string;
  is_competitor: boolean;
  reception: {
    hype_signals: string[];
    skepticism_signals: string[];
    overall: string;
  };
  hype_signals: string[];
  skepticism_signals: string[];
  overall: string;
}

export interface LaunchesResponse {
  myLaunch: LaunchPrediction | null;
  competitorLaunch: LaunchPrediction | null;
}

// Stats & Comparison Types
export interface MarketShareItem {
  name: string;
  value: number;
  color: string;
  sentimentCounts?: {
    positive: number;
    neutral: number;
    negative: number;
  };
}

export interface CompetitorComparisonResponse {
  market_share: MarketShareItem[];
  sales_leads: {
    me: number;
    competitor: number;
  };
  sentiment: {
    me: number;
    competitor: number;
  };
  timeframe: string;
  generated_at: string;
}

export interface MarketShareTrendResponse {
  trend: Array<{ date: string; me: number; competitor: number }>;
  days: number;
}

export interface StatsSummaryResponse {
  total_mentions_24h: number;
  my_mentions_24h: number;
  market_share_percent: number;
  hot_leads: number;
  competitor_leads: number;
  my_sentiment: number;
  competitor_sentiment: number;
  sentiment_advantage: number;
  generated_at: string;
}
