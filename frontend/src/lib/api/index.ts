/**
 * API Module Index
 * 
 * Barrel file that re-exports all API functions for backward compatibility.
 * New code should import from specific modules:
 * 
 * import { getBrands } from "@/lib/api/brands.api";
 * import { getLiveMentions } from "@/lib/api/mentions.api";
 */

// Base client
export { api, isWaitingResponse, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "./client";

// Domain APIs
export * from "./brands.api";
export * from "./mentions.api";
export * from "./competitors.api";
export * from "./leads.api";
export * from "./analytics.api";
