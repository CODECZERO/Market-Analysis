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

export class DuckDuckGoProvider implements MentionProvider {
    readonly platform = "news" as const; // Categorize as news/web

    private readonly client: HttpClient;
    private readonly baseUrl = "https://html.duckduckgo.com/html/";

    constructor(client: HttpClient) {
        this.client = client;
    }

    isEnabled(_brand: TrackedBrand): boolean {
        // Always enabled as a fallback/primary web search
        return true;
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        const term = brand.name.trim();
        if (!term) return [];

        try {
            // DDG HTML endpoint expects form data
            const params = new URLSearchParams();
            params.append("q", term);

            const response = await this.client.post<string>(this.baseUrl, params, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                },
                responseType: "text" // Important to get HTML string
            });

            const $ = load(response.data);
            const results: DDGResult[] = [];

            $(".result").each((_, element) => {
                const title = $(element).find(".result__title .result__a").text().trim();
                const link = $(element).find(".result__title .result__a").attr("href");
                const snippet = $(element).find(".result__snippet").text().trim();

                if (title && link && snippet) {
                    // DDG links are often relative or redirects, simple scrape gives absolute usually? 
                    // In html.duckduckgo, links are usually direct or simple redirects.
                    // Let's trust the scraper gets the href.
                    results.push({ title, link, snippet });
                }
            });

            return results.map<RawMention>((item, index) => ({
                id: `ddg_${Buffer.from(item.link).toString("base64").slice(0, 20)}`,
                timestamp: Date.now() - index * 60000, // Estimate time
                text: `${item.title}\n${item.snippet}`,
                author: new URL(item.link).hostname,
                url: item.link,
                raw: item,
                platform: "news",
            }));

        } catch (error) {
            console.warn(`[DuckDuckGo] Search failed for "${term}":`, error);
            return [];
        }
    }
}
