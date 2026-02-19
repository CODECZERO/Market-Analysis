import { HttpClient } from "../../../utils/http-client.js";
import { env } from "../../../config/env.js";
import type { TrackedBrand } from "../../brands/types/brand.js";
import type { MentionProvider } from "../types/provider.js";
import type { RawMention } from "../types/mention.js";

/**
 * Hacker News Search Response from Algolia API
 * https://hn.algolia.com/api
 */
interface HNSearchResponse {
    hits?: Array<{
        objectID?: string;
        created_at?: string;
        created_at_i?: number;
        title?: string;
        story_title?: string;
        url?: string;
        story_url?: string;
        author?: string;
        comment_text?: string;
        story_text?: string;
        _tags?: string[];
    }>;
    nbHits?: number;
}

/**
 * Hacker News Provider
 * Uses the free Algolia-powered HN Search API
 */
export class HackerNewsProvider implements MentionProvider {
    readonly platform = "hn" as const;

    private readonly client: HttpClient;
    private readonly apiUrl: string;

    constructor(client: HttpClient) {
        this.client = client;
        this.apiUrl = env.hn?.apiUrl || "https://hn.algolia.com/api/v1/search_by_date";
    }

    isEnabled(_brand: TrackedBrand): boolean {
        // Always enabled - free API, no auth needed
        return true;
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        const terms = [brand.name, ...(brand.aliases ?? [])]
            .map((value) => value.trim())
            .filter(Boolean);

        // Search for each term and combine results
        const allMentions: RawMention[] = [];

        for (const term of terms.slice(0, 3)) { // Limit to 3 terms
            try {
                const response = await this.client.get<HNSearchResponse>(this.apiUrl, {
                    params: {
                        query: term,
                        tags: "(story,comment)", // Both stories and comments
                        hitsPerPage: 20,
                        numericFilters: `created_at_i>${Math.floor(Date.now() / 1000 - 3600)}`, // Last hour
                    },
                    headers: {
                        "User-Agent": "brandtracker-aggregator/1.0",
                    },
                });

                const hits = response.data.hits ?? [];

                const mentions = hits
                    .filter((hit) => Boolean(hit?.objectID && hit?.created_at_i))
                    .map<RawMention>((hit) => ({
                        id: `hn_${hit.objectID}`,
                        timestamp: (hit.created_at_i ?? 0) * 1000,
                        text: hit.comment_text || hit.story_text || hit.title || hit.story_title || "",
                        author: hit.author ?? "unknown",
                        url: hit.url || hit.story_url || `https://news.ycombinator.com/item?id=${hit.objectID}`,
                        raw: hit,
                        platform: "hn",
                    }));

                allMentions.push(...mentions);
            } catch (error) {
                // Log but don't fail - continue with other terms
                console.warn(`[HN] Failed to fetch for term "${term}":`, error);
            }
        }

        // Dedupe by ID
        const seen = new Set<string>();
        return allMentions.filter((m) => {
            if (seen.has(m.id)) return false;
            seen.add(m.id);
            return true;
        });
    }
}
