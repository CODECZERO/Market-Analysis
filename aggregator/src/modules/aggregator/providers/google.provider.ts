import { HttpClient } from "../../../utils/http-client.js";
import { env } from "../../../config/env.js";
import type { TrackedBrand } from "../../brands/types/brand.js";
import type { MentionProvider } from "../types/provider.js";
import type { RawMention } from "../types/mention.js";

/**
 * Google Custom Search API Response
 * https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
 */
interface GoogleSearchResponse {
    items?: Array<{
        title?: string;
        link?: string;
        snippet?: string;
        displayLink?: string;
        pagemap?: {
            metatags?: Array<{
                "og:site_name"?: string;
                "og:type"?: string;
                "article:published_time"?: string;
            }>;
        };
    }>;
    searchInformation?: {
        totalResults?: string;
    };
}

/**
 * Google Search Provider
 * Uses Google Custom Search JSON API
 * Requires GOOGLE_API_KEY and GOOGLE_CX environment variables
 * Free tier: 100 queries/day
 */
export class GoogleSearchProvider implements MentionProvider {
    readonly platform = "news" as const; // Categorized as news since it fetches web results

    private readonly client: HttpClient;
    private readonly apiUrl = "https://www.googleapis.com/customsearch/v1";

    constructor(client: HttpClient) {
        this.client = client;
    }

    isEnabled(_brand: TrackedBrand): boolean {
        return Boolean(env.google?.apiKey && env.google?.searchEngineId);
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        if (!env.google) {
            return [];
        }

        const terms = [brand.name, ...(brand.aliases ?? [])]
            .map((value) => value.trim())
            .filter(Boolean);

        const searchQuery = terms.join(" OR ");

        try {
            const response = await this.client.get<GoogleSearchResponse>(this.apiUrl, {
                params: {
                    key: env.google.apiKey,
                    cx: env.google.searchEngineId,
                    q: searchQuery,
                    num: 10, // Top 10 results
                    dateRestrict: "d1", // Last 24 hours
                    sort: "date", // Most recent first
                },
            });

            const items = response.data.items ?? [];

            return items
                .filter((item) => Boolean(item?.link && item?.title))
                .map<RawMention>((item, index) => {
                    // Try to extract publish date from pagemap metatags
                    const publishTime = item.pagemap?.metatags?.[0]?.["article:published_time"];
                    const timestamp = publishTime
                        ? new Date(publishTime).getTime()
                        : Date.now() - index * 60000; // Fallback: offset by 1 min per result

                    return {
                        id: `google_${Buffer.from(item.link!).toString("base64").slice(0, 20)}`,
                        timestamp,
                        text: `${item.title}\n${item.snippet || ""}`,
                        author: item.displayLink || "web",
                        url: item.link!,
                        raw: item,
                        platform: "news", // Web results categorized as news
                    };
                });
        } catch (error) {
            console.warn(`[Google] Search failed for "${searchQuery}":`, error);
            return [];
        }
    }
}
