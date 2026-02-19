/**
 * Legacy API Module
 * 
 * @deprecated This file is kept for backward compatibility.
 * New code should import from "@/lib/api" or specific modules:
 * 
 * import { getBrands } from "@/lib/api/brands.api";
 * import { getLiveMentions } from "@/lib/api/mentions.api";
 * import { api } from "@/lib/api/client";
 */

// Re-export everything from the new modular structure
export * from "./api/index";
