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

export class SocialWebProvider implements MentionProvider {
    readonly platform = "web" as const;

    private readonly client: HttpClient;
    private readonly baseUrl = "https://html.duckduckgo.com/html/";

    // Social sites to target
    private readonly sites = [
        "instagram.com",
        "facebook.com",
        "tiktok.com",
        "linkedin.com",
        "twitter.com",
        "x.com"
    ];

    constructor(client: HttpClient) {
        this.client = client;
    }

    isEnabled(_brand: TrackedBrand): boolean {
        return true;
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        const brandTerm = brand.name.trim();
        if (!brandTerm) return [];

        // Construct site search query: "Brand Name" site:instagram.com OR site:facebook.com ...
        const siteQueries = this.sites.map(site => `site:${site}`).join(" OR ");
        const term = `"${brandTerm}" (${siteQueries})`;

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
                // Try to identify platform from URL for more granular display if supported
                let platform = "web";
                if (item.link.includes("instagram.com")) platform = "instagram";
                else if (item.link.includes("facebook.com")) platform = "facebook";
                else if (item.link.includes("tiktok.com")) platform = "tiktok";
                else if (item.link.includes("linkedin.com")) platform = "linkedin";
                else if (item.link.includes("twitter.com") || item.link.includes("x.com")) platform = "twitter";

                // If the specific platform isn't in backend types properly yet, fallback to "web" logic in frontend?
                // But we added them to types/mention.ts so casting is safe backend-wise.
                // The issue is whether Frontend supports them.

                return {
                    id: `social_ddg_${Buffer.from(item.link).toString("base64").slice(0, 20)}`,
                    timestamp: Date.now() - index * 60000,
                    text: `${item.title}\n${item.snippet}`,
                    author: new URL(item.link).hostname,
                    url: item.link,
                    raw: item,
                    platform: platform as any,
                };
            });

        } catch (error) {
            console.warn(`[SocialWeb] Search failed for "${term}":`, error);
            return [];
        }
    }
}
