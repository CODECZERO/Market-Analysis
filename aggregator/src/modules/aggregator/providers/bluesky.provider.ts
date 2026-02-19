import { HttpClient } from "../../../utils/http-client.js";
import type { TrackedBrand } from "../../brands/types/brand.js";
import type { MentionProvider } from "../types/provider.js";
import type { RawMention } from "../types/mention.js";

/**
 * Bluesky AT Protocol API Response Types
 */
interface BlueskySearchResponse {
    posts?: BlueskyPostData[];
    cursor?: string;
}

interface BlueskyPostData {
    uri?: string;
    cid?: string;
    author?: {
        did?: string;
        handle?: string;
        displayName?: string;
    };
    record?: {
        text?: string;
        createdAt?: string;
        reply?: {
            parent?: { uri?: string };
        };
        embed?: {
            $type?: string;
            external?: { uri?: string };
        };
    };
    likeCount?: number;
    repostCount?: number;
}

/**
 * Bluesky Provider
 * Uses the public Bluesky AT Protocol search API
 * No API key required - public endpoint
 * Rate limit: Reasonable use (~100 requests/minute)
 */
export class BlueskyProvider implements MentionProvider {
    readonly platform = "bluesky" as const;

    private readonly client: HttpClient;
    private readonly apiBase = "https://public.api.bsky.app/xrpc";

    constructor(client: HttpClient) {
        this.client = client;
    }

    isEnabled(_brand: TrackedBrand): boolean {
        // Always enabled - no API key required
        return true;
    }

    async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
        const terms = [brand.name, ...(brand.aliases ?? [])]
            .map((value) => value.trim())
            .filter(Boolean);

        const allMentions: RawMention[] = [];

        for (const term of terms) {
            try {
                const mentions = await this.searchPosts(term);
                allMentions.push(...mentions);

                // Rate limiting between searches
                await this.sleep(500);
            } catch (error) {
                console.warn(`[Bluesky] Search failed for "${term}":`, error);
            }
        }

        // Deduplicate by ID
        const seen = new Set<string>();
        return allMentions.filter((m) => {
            if (seen.has(m.id)) return false;
            seen.add(m.id);
            return true;
        });
    }

    private async searchPosts(query: string, limit: number = 50): Promise<RawMention[]> {
        const url = `${this.apiBase}/app.bsky.feed.searchPosts`;

        try {
            const response = await this.client.get<BlueskySearchResponse>(url, {
                params: {
                    q: query,
                    limit: Math.min(limit, 100),
                },
                headers: {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                }
            });

            const posts = response.data.posts ?? [];
            return posts
                .filter((post) => Boolean(post?.uri && post?.record?.text))
                .map<RawMention>((post) => this.transformToMention(post));
        } catch (error) {
            console.warn(`[Bluesky] API error for "${query}":`, error);
            return [];
        }
    }

    private transformToMention(post: BlueskyPostData): RawMention {
        const record = post.record ?? {};
        const author = post.author ?? {};

        // Parse timestamp
        let timestamp = Date.now();
        if (record.createdAt) {
            try {
                timestamp = new Date(record.createdAt).getTime();
            } catch {
                // Keep default
            }
        }

        // Generate stable ID from URI
        const id = `bluesky_${Buffer.from(post.uri ?? "").toString("base64").slice(0, 20)}`;

        // Build profile URL
        const postId = post.uri?.split("/").pop() ?? "";
        const profileUrl = author.handle
            ? `https://bsky.app/profile/${author.handle}/post/${postId}`
            : post.uri ?? "";

        return {
            id,
            timestamp,
            text: record.text ?? "",
            author: author.handle ? `@${author.handle}` : "unknown",
            url: profileUrl,
            raw: post,
            platform: "bluesky",
        };
    }

    private sleep(ms: number): Promise<void> {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
}
