import { load } from "cheerio";
import { HttpClient } from "../../../utils/http-client.js";
import type { TrackedBrand } from "../../brands/types/brand.js";
import type { MentionProvider } from "../types/provider.js";
import type { RawMention } from "../types/mention.js";

interface DDGResult {
    title: string;
    link: string;
    snippet: string;
}

export class YoutubeSearchProvider implements MentionProvider {
    readonly platform = "youtube" as const;

    private readonly client: HttpClient;
    private readonly baseUrl = "https://html.duckduckgo.com/html/";

    constructor(client: HttpClient) {
        this.client = client;
    }

    isEnabled(_brand: TrackedBrand): boolean {
        // Free to everyone
        return true;
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        const brandTerm = brand.name.trim();
        if (!brandTerm) return [];

        const term = `site:youtube.com "${brandTerm}"`;

        try {
            const params = new URLSearchParams();
            params.append("q", term);

            const response = await this.client.post<string>(this.baseUrl, params, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                },
                responseType: "text"
            });

            const $ = load(response.data);
            const results: DDGResult[] = [];

            $(".result").each((_, element) => {
                const title = $(element).find(".result__title .result__a").text().trim();
                const link = $(element).find(".result__title .result__a").attr("href");
                const snippet = $(element).find(".result__snippet").text().trim();

                if (title && link && snippet) {
                    results.push({ title, link, snippet });
                }
            });

            return results.map<RawMention>((item, index) => {
                // Extract video ID if possible for thumbnail?
                // For now just basic mention
                return {
                    id: `yt_ddg_${Buffer.from(item.link).toString("base64").slice(0, 20)}`,
                    timestamp: Date.now() - index * 60000,
                    text: `${item.title}\n${item.snippet}`,
                    author: new URL(item.link).hostname, // usually www.youtube.com
                    url: item.link,
                    raw: item,
                    platform: "youtube",
                };
            });

        } catch (error) {
            console.warn(`[YoutubeSearch] Search failed for "${term}":`, error);
            return [];
        }
    }
}
