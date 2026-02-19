import { env } from "../../../config/env.js";
import { logger } from "../../../utils/logger.js";
import type { MentionProvider } from "../types/provider.js";
import type { RawMention } from "../types/mention.js";
import type { TrackedBrand } from "../../brands/types/brand.js";

export class XProvider implements MentionProvider {
  readonly platform = "x" as const;

  isEnabled(_brand: TrackedBrand): boolean {
    return Boolean(env.x.apiKey);
  }

  async fetchMentions(brand: TrackedBrand): Promise<RawMention[]> {
    if (!this.isEnabled(brand)) {
      return [];
    }

    // TODO: Implement real X API call here when key is present
    // For now, return empty to avoid mocking as per user request
    return [];
  }
}
