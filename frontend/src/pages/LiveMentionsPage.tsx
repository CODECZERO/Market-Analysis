/**
 * Live Mentions Page
 * 
 * Real-time monitoring of brand mentions with filters.
 * Refactored to use extracted SRP-compliant components.
 */

import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

import { useLivePage } from "@/hooks/live";
import {
  LiveHeader,
  FilterPanel,
  LiveStats,
  LiveFeed,
} from "@/components/live";

export default function LiveMentionsPage() {
  const {
    brandId,
    mentions,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
    filters
  } = useLivePage();

  const hasActiveFilters = Boolean(filters.fromDate || filters.toDate);

  return (
    <div className="space-y-6 pb-24">
      {/* Back Link */}
      <Link
        to={`/brands/${brandId}/dashboard`}
        className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <LiveHeader
        showFilters={filters.show}
        onToggleFilters={filters.toggle}
        onRefresh={() => refetch()}
        isFetching={isFetching}
        hasActiveFilters={hasActiveFilters}
      />

      {/* Filter Panel */}
      {filters.show && (
        <FilterPanel
          filters={filters}
          onApply={() => refetch()}
        />
      )}

      {/* Stats Bar */}
      <LiveStats mentionCount={mentions.length} />

      {/* Mentions List */}
      <LiveFeed
        mentions={mentions}
        isLoading={isLoading}
        isError={isError}
        error={error}
        isFetching={isFetching}
        onRetry={() => refetch()}
      />
    </div>
  );
}
