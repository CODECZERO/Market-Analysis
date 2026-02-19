export type MentionPlatform = "reddit" | "x" | "news" | "rss" | "hn" | "youtube" | "appstore" | "bluesky" | "web" | "instagram" | "facebook" | "tiktok" | "linkedin" | "twitter";

export type UrgencyLevel = "high" | "medium" | "low";
export type SentimentLabel = "positive" | "neutral" | "negative";

export interface Emotions {
  joy: number;
  anger: number;
  fear: number;
  sadness: number;
  surprise: number;
  disgust: number;
}

export interface EnhancedAnalysis {
  sentimentScore: number;      // -1.0 to +1.0
  sentimentLabel: SentimentLabel;
  emotions: Emotions;
  isSarcastic: boolean;
  urgency: UrgencyLevel;
  topics: string[];
  language: string;
}

export interface MentionMetadata {
  author: string;
  url: string;
  raw: unknown;
  [key: string]: unknown;
}

export interface NormalizedMention {
  id: string;
  brand: string;
  text: string;
  timestamp: number;
  source: MentionPlatform;
  metadata: MentionMetadata;
  // Enhanced analysis (populated after processing)
  enhancedAnalysis?: EnhancedAnalysis;
}

export interface RawMention {
  id: string;
  timestamp: string | number;
  text: string;
  author: string;
  url: string;
  raw: unknown;
  platform: MentionPlatform;
  score?: number;  // Upvote count for influence scoring
}

