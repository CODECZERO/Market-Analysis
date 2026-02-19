/**
 * Smart Brand Matching Service
 * 
 * Provides intelligent matching of mentions to brands using:
 * - Exact matching
 * - Fuzzy matching (Levenshtein distance for typo detection)
 * - Keyword/alias matching
 * - Industry context disambiguation
 * - Exclusion filtering (false positive reduction)
 */
import { distance } from 'fastest-levenshtein';
import type { TrackedBrand } from '../../brands/types/brand.js';
import { logger } from '../../../utils/logger.js';

export type MatchType = 'exact' | 'fuzzy' | 'typo' | 'keyword' | 'context' | 'none';

export interface MatchResult {
    isMatch: boolean;
    confidence: number;  // 0-1
    matchType: MatchType;
    matchedTerm?: string;
    reason?: string;
}

// Industry-specific context keywords for disambiguation
const INDUSTRY_CONTEXTS: Record<string, string[]> = {
    'tech': ['software', 'app', 'cloud', 'developer', 'api', 'startup', 'ai', 'machine learning', 'saas', 'platform', 'code', 'programming'],
    'ecommerce': ['shop', 'buy', 'order', 'delivery', 'shipping', 'cart', 'checkout', 'price', 'discount', 'sale'],
    'finance': ['bank', 'loan', 'credit', 'invest', 'stock', 'trading', 'payment', 'money', 'wallet', 'crypto'],
    'food': ['restaurant', 'menu', 'order', 'delivery', 'taste', 'food', 'meal', 'recipe', 'cooking', 'eat'],
    'automotive': ['car', 'vehicle', 'drive', 'motor', 'engine', 'ev', 'electric', 'tesla', 'ford', 'toyota'],
    'healthcare': ['health', 'medical', 'doctor', 'hospital', 'patient', 'treatment', 'medicine', 'pharmacy'],
    'gaming': ['game', 'gaming', 'esports', 'console', 'pc', 'xbox', 'playstation', 'steam', 'twitch'],
    'social': ['social', 'network', 'friends', 'followers', 'post', 'share', 'like', 'comment', 'feed'],
};

export class SmartMatcherService {
    private matchCache = new Map<string, MatchResult>();
    private cacheHits = 0;
    private cacheMisses = 0;

    /**
     * Check if mention text matches brand with intelligent matching
     */
    match(text: string, brand: TrackedBrand): MatchResult {
        const textLower = text.toLowerCase();
        const brandName = brand.name.toLowerCase();

        // Cache key for performance (useful when same text checked against multiple brands)
        const cacheKey = `${textLower.substring(0, 100)}:${brand.id}`;
        const cached = this.matchCache.get(cacheKey);
        if (cached) {
            this.cacheHits++;
            return cached;
        }
        this.cacheMisses++;

        const result = this.performMatch(textLower, brandName, brand);

        // Cache result (limit cache size)
        if (this.matchCache.size > 10000) {
            // Clear oldest entries (simple FIFO)
            const firstKey = this.matchCache.keys().next().value;
            if (firstKey) this.matchCache.delete(firstKey);
        }
        this.matchCache.set(cacheKey, result);

        return result;
    }

    private performMatch(textLower: string, brandName: string, brand: TrackedBrand): MatchResult {
        const config = brand.matchConfig || {};

        // 0. CHECK EXCLUSIONS FIRST (fast fail for false positives)
        if (this.hasExclusionHit(textLower, config.excludeKeywords)) {
            return {
                isMatch: false,
                confidence: 0,
                matchType: 'none',
                reason: 'Excluded by negative keyword'
            };
        }

        // 1. EXACT BRAND NAME MATCH (highest confidence)
        if (this.hasExactMatch(textLower, brandName)) {
            return {
                isMatch: true,
                confidence: 1.0,
                matchType: 'exact',
                matchedTerm: brandName
            };
        }

        // 2. ALIAS/KEYWORD MATCH
        const allKeywords = this.buildKeywordList(brand);

        for (const keyword of allKeywords) {
            if (this.hasExactMatch(textLower, keyword)) {
                return {
                    isMatch: true,
                    confidence: 0.95,
                    matchType: 'keyword',
                    matchedTerm: keyword
                };
            }
        }

        // 3. MISSPELLING MATCH (user-defined typos)
        const misspellings = config.misspellings || [];
        for (const typo of misspellings) {
            if (textLower.includes(typo.toLowerCase())) {
                return {
                    isMatch: true,
                    confidence: 0.9,
                    matchType: 'typo',
                    matchedTerm: typo,
                    reason: `Known misspelling: "${typo}"`
                };
            }
        }

        // 4. FUZZY MATCH (typo detection via Levenshtein)
        const threshold = config.fuzzyThreshold ?? 0.8;
        const fuzzyResult = this.fuzzyMatch(textLower, brandName, allKeywords, threshold);
        if (fuzzyResult.isMatch) {
            return fuzzyResult;
        }

        // 5. CONTEXT DISAMBIGUATION (if industry provided)
        if (config.industry) {
            const contextResult = this.contextMatch(textLower, brandName, config.industry);
            if (contextResult.isMatch) {
                return contextResult;
            }
        }

        return { isMatch: false, confidence: 0, matchType: 'none' };
    }

    /**
     * Check for exact word boundary match (not substring)
     * "Apple" should match "I love Apple" but not "Pineapple"
     */
    private hasExactMatch(text: string, term: string): boolean {
        // Simple includes check for performance
        if (!text.includes(term)) {
            return false;
        }

        // Word boundary check using regex
        const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`\\b${escapedTerm}\\b`, 'i');
        return regex.test(text);
    }

    /**
     * Build comprehensive keyword list from brand config
     */
    private buildKeywordList(brand: TrackedBrand): string[] {
        const config = brand.matchConfig || {};
        return [
            ...(brand.aliases || []),
            ...(brand.keywords || []),
            ...(config.products || [])
        ].map(k => k.toLowerCase()).filter(Boolean);
    }

    /**
     * Fuzzy matching using Levenshtein distance
     */
    private fuzzyMatch(
        text: string,
        brandName: string,
        keywords: string[],
        threshold: number
    ): MatchResult {
        // Extract words from text (3+ characters to avoid matching "a", "is", etc.)
        const words = text.split(/\s+/).filter(w => w.length >= 3);

        for (const word of words) {
            // Skip very short words
            if (word.length < 3) continue;

            // Check brand name
            if (brandName.length >= 3) {
                const similarity = this.calculateSimilarity(word, brandName);

                if (similarity >= threshold) {
                    return {
                        isMatch: true,
                        confidence: similarity,
                        matchType: 'typo',
                        matchedTerm: word,
                        reason: `Typo of "${brandName}" (${(similarity * 100).toFixed(0)}% similar)`
                    };
                }
            }

            // Check keywords
            for (const keyword of keywords) {
                if (keyword.length < 3) continue;

                const kwSimilarity = this.calculateSimilarity(word, keyword);

                if (kwSimilarity >= threshold) {
                    return {
                        isMatch: true,
                        confidence: kwSimilarity * 0.9, // Slightly lower confidence for keyword match
                        matchType: 'fuzzy',
                        matchedTerm: word,
                        reason: `Fuzzy match to "${keyword}" (${(kwSimilarity * 100).toFixed(0)}% similar)`
                    };
                }
            }
        }

        return { isMatch: false, confidence: 0, matchType: 'fuzzy' };
    }

    /**
     * Calculate similarity score using Levenshtein distance
     * Returns value between 0 (no match) and 1 (exact match)
     */
    private calculateSimilarity(word1: string, word2: string): number {
        const dist = distance(word1, word2);
        const maxLen = Math.max(word1.length, word2.length);
        return 1 - (dist / maxLen);
    }

    /**
     * Context-based matching using industry signals
     */
    private contextMatch(text: string, brandName: string, industry: string): MatchResult {
        const industryLower = industry.toLowerCase();
        const contextKeywords = INDUSTRY_CONTEXTS[industryLower] || [];

        if (contextKeywords.length === 0) {
            return { isMatch: false, confidence: 0, matchType: 'context' };
        }

        // Check if text has industry context
        const hasContext = contextKeywords.some(kw => text.includes(kw));

        // Check for partial brand mention (first 3+ characters)
        const brandPrefix = brandName.length >= 3 ? brandName.substring(0, Math.min(4, brandName.length)) : brandName;
        const hasBrandHint = text.includes(brandPrefix);

        if (hasContext && hasBrandHint) {
            return {
                isMatch: true,
                confidence: 0.7,
                matchType: 'context',
                reason: `Industry context match (${industry})`
            };
        }

        return { isMatch: false, confidence: 0, matchType: 'context' };
    }

    /**
     * Check if text contains any exclusion keywords (for false positive filtering)
     */
    private hasExclusionHit(text: string, exclusions?: string[]): boolean {
        if (!exclusions || exclusions.length === 0) {
            return false;
        }
        return exclusions.some(ex => text.includes(ex.toLowerCase()));
    }

    /**
     * Get cache statistics for monitoring
     */
    getCacheStats(): { hits: number; misses: number; size: number } {
        return {
            hits: this.cacheHits,
            misses: this.cacheMisses,
            size: this.matchCache.size
        };
    }

    /**
     * Clear the cache (useful for testing or memory management)
     */
    clearCache(): void {
        this.matchCache.clear();
        this.cacheHits = 0;
        this.cacheMisses = 0;
    }
}
