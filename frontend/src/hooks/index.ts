/**
 * Hooks Index
 * 
 * Main barrel file for backward compatibility.
 * Re-exports all hooks from subdirectories.
 * 
 * New code should import from specific modules:
 * import { useBrands } from "@/hooks/brands";
 * import { useCompetitorComparison } from "@/hooks/stats";
 */

// Core utilities
export * from "./core";

// Brand hooks
export * from "./brands";

// Stats hooks
export * from "./stats";

// Keep legacy exports for wake-up service
export { useWakeUpService } from "./useWakeUpService";
