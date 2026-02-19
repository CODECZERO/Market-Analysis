import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { ExternalLink, Twitter, Globe, MessageSquare, AlertCircle, Hash, User } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { SENTIMENT_COLORS } from "@/lib/utils";
import { type LiveMentionsResponse, type Mention } from "@/types/api";

interface LiveMentionListProps {
  mentions: LiveMentionsResponse;
  grouped?: boolean;
  brandId?: string;
}

export function LiveMentionList({ mentions, grouped = false, brandId }: LiveMentionListProps) {
  const [sentimentFilter, setSentimentFilter] = useState<"all" | "positive" | "neutral" | "negative">("all");
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [visibleCount, setVisibleCount] = useState(10);
  const navigate = useNavigate();
  const { brandId: routeBrandId = "" } = useParams();
  const resolvedBrandId = brandId ?? routeBrandId;

  const handleSelectMention = useCallback(
    (mention: Mention) => {
      if (!resolvedBrandId) return;
      navigate(`/brands/${resolvedBrandId}/live/${mention.id}`);
    },
    [navigate, resolvedBrandId],
  );

  useEffect(() => {
    setVisibleCount(10);
  }, [sentimentFilter, sourceFilter, mentions]);

  const availableSources = useMemo(() => {
    const unique = new Set<string>();
    mentions.forEach((mention) => unique.add(mention.source));
    return Array.from(unique);
  }, [mentions]);

  const filteredMentions = useMemo(() => {
    return mentions.filter((mention) => {
      const sentimentMatches = sentimentFilter === "all" || mention.sentiment === sentimentFilter;
      const sourceMatches = sourceFilter === "all" || mention.source === sourceFilter;
      return sentimentMatches && sourceMatches;
    });
  }, [mentions, sentimentFilter, sourceFilter]);

  const visibleMentions = filteredMentions.slice(0, visibleCount);
  const noMentions = visibleMentions.length === 0;

  if (!mentions.length) {
    return (
      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardContent className="flex h-40 items-center justify-center text-sm text-zinc-500">
          No live mentions fetched yet.
        </CardContent>
      </Card>
    );
  }

  const FilterControls = (
    <div className="mb-4 flex flex-wrap items-center gap-3 bg-zinc-900/50 p-3 rounded-xl border border-zinc-800/50">
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">Sentiment</span>
        <div className="flex gap-1">
          {(["all", "positive", "neutral", "negative"] as const).map((option) => {
            const isActive = sentimentFilter === option;
            const colors = {
              all: "bg-zinc-800 text-zinc-400 hover:text-white",
              positive: "bg-emerald-500/20 text-emerald-400 border-emerald-500/20",
              neutral: "bg-blue-500/20 text-blue-400 border-blue-500/20",
              negative: "bg-red-500/20 text-red-400 border-red-500/20"
            };

            return (
              <button
                key={option}
                onClick={() => setSentimentFilter(option)}
                className={`
                    px-2.5 py-1 rounded-md text-xs font-medium transition-all border
                    ${isActive
                    ? (option === 'all' ? "bg-zinc-700 text-white border-zinc-600" : colors[option])
                    : "bg-transparent border-transparent text-zinc-500 hover:bg-zinc-800"}
                `}
              >
                {option === "all" ? "All" : option.charAt(0).toUpperCase() + option.slice(1)}
              </button>
            );
          })}
        </div>
      </div>

      <div className="h-4 w-px bg-zinc-800" />

      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">Source</span>
        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          className="bg-zinc-800 border-zinc-700 text-zinc-300 text-xs rounded-md px-2 py-1 focus:ring-1 focus:ring-blue-500 outline-none"
        >
          <option value="all">All Sources</option>
          {availableSources.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
    </div>
  );

  return (
    <Card className="border-0 bg-transparent shadow-none">
      <CardContent className="p-0">
        {FilterControls}
        {noMentions ? (
          <div className="flex h-40 items-center justify-center text-sm text-zinc-500 border border-zinc-800 rounded-xl bg-zinc-900/50">
            No mentions match the selected filters.
          </div>
        ) : (
          <div className="max-h-[600px] overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent pr-2">
            <div className="space-y-3">
              {visibleMentions.map((mention) => (
                <SocialMentionCard
                  key={mention.id}
                  mention={mention}
                  onClick={() => handleSelectMention(mention)}
                />
              ))}

              {filteredMentions.length > visibleMentions.length && (
                <div className="pt-2 flex justify-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setVisibleCount(c => c + 10)}
                    className="text-zinc-500 hover:text-white"
                  >
                    Load more mentions
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Helper to format HTML content into readable text
function formatMentionContent(html: string) {
  if (!html) return "";

  // Pre-process formatting tags to simple newlines/markers
  // This ensures we don't lose structure when stripping tags
  const processed = html
    .replace(/<p[^>]*>/gi, "\n")
    .replace(/<\/p>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<div[^>]*>/gi, "\n")
    .replace(/<\/div>/gi, "")
    .replace(/<li[^>]*>/gi, "\n• ");

  // Use DOMParser to safely decode entities and strip remaining tags
  const parser = new DOMParser();
  const doc = parser.parseFromString(processed, "text/html");
  return (doc.body.textContent || "").trim();
}

// =============================================================================
// SOCIAL MENTION CARD
// =============================================================================

function SocialMentionCard({ mention, onClick }: { mention: Mention; onClick: () => void }) {
  // Platform Icon Logic
  const PlatformIcon = useMemo(() => {
    const s = mention.source.toLowerCase();
    if (s.includes("twitter") || s.includes("x")) return Twitter;
    if (s.includes("reddit")) return AlertCircle;
    return Globe;
  }, [mention.source]);

  // Format metadata safely
  const authorHandle = mention.metadata?.author || "anonymous";
  const authorName = authorHandle.replace('@', ''); // Simple logic, can be improved
  const postUrl = mention.metadata?.url || mention.url;

  // Sentiment Logic
  const sentimentConfig = useMemo(() => {
    switch (mention.sentiment) {
      case "positive": return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" };
      case "negative": return { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20" };
      default: return { color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" };
    }
  }, [mention.sentiment]);

  return (
    <div
      onClick={onClick}
      className="group relative bg-zinc-900/40 hover:bg-zinc-900/80 border border-zinc-800/50 hover:border-zinc-700 rounded-xl p-4 transition-all duration-200 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        {/* Avatar & Content Column */}
        <div className="flex gap-4 w-full">
          {/* Avatar */}
          <Avatar className="w-10 h-10 border border-zinc-800 shadow-sm mt-1">
            <AvatarImage src={`https://unavatar.io/${authorName}`} />
            <AvatarFallback className="bg-zinc-800 text-zinc-400 text-xs">
              {authorName.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Header Line */}
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="font-semibold text-zinc-200 truncate text-sm">
                  {authorName}
                </span>
                <span className="text-zinc-500 text-xs truncate">
                  @{authorHandle}
                </span>
                <span className="text-zinc-600 text-[10px] flex-shrink-0">•</span>
                <span className="text-zinc-500 text-xs whitespace-nowrap">
                  {formatDistanceToNow(new Date(mention.createdAt), { addSuffix: true })}
                </span>
              </div>

              {/* Header Time */}
              <span className="text-zinc-500 text-xs whitespace-nowrap ml-auto">
                {formatDistanceToNow(new Date(mention.createdAt), { addSuffix: true })}
              </span>
            </div>

            {/* Text Content */}
            <div className="text-sm text-zinc-300 leading-relaxed mb-3 whitespace-pre-wrap font-normal">
              {formatMentionContent(mention.text)}
            </div>

            {/* Footer Metadata */}
            <div className="flex items-center justify-between pt-2 border-t border-zinc-800/30">
              <div className="flex items-center gap-3">
                {/* Sentiment Badge */}
                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-medium border ${sentimentConfig.bg} ${sentimentConfig.color} ${sentimentConfig.border}`}>
                  <div className={`w-1 h-1 rounded-full bg-current`} />
                  {(mention.sentiment || "neutral").toUpperCase()}
                </div>

                {/* Quick Stats (Fake for UI demo, replace with real metadata if available) */}
                <div className="flex items-center gap-1 text-zinc-500 text-xs">
                  <MessageSquare className="w-3 h-3" />
                  <span>Reply</span>
                </div>
              </div>

              {postUrl && (
                <a
                  href={postUrl}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1 text-[10px] font-medium text-zinc-500 hover:text-blue-400 transition-colors"
                >
                  View Original <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>

            {/* Source Label (Added per user request) */}
            <div className="absolute top-4 right-4 flex items-center gap-1.5 px-2 py-1 rounded-md bg-zinc-800/80 border border-zinc-700/50 backdrop-blur-sm">
              <PlatformIcon className="w-3 h-3 text-zinc-400" />
              <span className="text-[10px] font-medium text-zinc-300 capitalize">{mention.source}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
