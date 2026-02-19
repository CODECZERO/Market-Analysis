import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { formatDistanceToNow, format } from "date-fns";
import { ArrowLeft, ExternalLink, MessageSquare, Heart, RefreshCw, Share2, AlertCircle, Terminal, Twitter, Globe } from "lucide-react";

import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useLiveMentions } from "@/hooks/useBrands";
import { motion } from "framer-motion";

export default function LiveMentionDetailPage() {
  const navigate = useNavigate();
  const { brandId = "", mentionId = "" } = useParams();
  const [showRaw, setShowRaw] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const {
    data: mentions = [],
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useLiveMentions(brandId);

  const mention = useMemo(() => mentions.find((item) => item.id === mentionId) ?? null, [mentions, mentionId]);

  if (isLoading) {
    return <LoadingState message="Loading mention details..." />;
  }

  if (isError) {
    return (
      <div className="flex h-[50vh] flex-col items-center justify-center p-6 text-center">
        <div className="rounded-full bg-red-500/10 p-4 mb-4">
          <AlertCircle className="w-8 h-8 text-red-500" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Failed to load mention</h3>
        <p className="text-zinc-400 mb-6">{error?.message ?? "An unexpected error occurred."}</p>
        <Button onClick={() => refetch()} disabled={isFetching} variant="outline" className="border-zinc-700">
          Try Again
        </Button>
      </div>
    );
  }

  if (!mention) {
    return (
      <div className="flex h-[50vh] flex-col items-center justify-center p-6 text-center">
        <div className="rounded-full bg-zinc-800/50 p-4 mb-4">
          <MessageSquare className="w-8 h-8 text-zinc-500" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Mention not found</h3>
        <p className="text-zinc-400 mb-6">It may have expired or been filtered out of the live feed.</p>
        <Button onClick={() => navigate(`/brands/${brandId}/live`)} variant="secondary">
          Back to Live Feed
        </Button>
      </div>
    );
  }

  // --- Derived Data & Helpers ---

  const authorHandle = mention.metadata?.author || "anonymous";
  const authorName = authorHandle.replace('@', '');
  const postUrl = mention.metadata?.url || mention.url;

  const sentimentConfig = (() => {
    switch (mention.sentiment) {
      case "positive": return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "Positive" };
      case "negative": return { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20", label: "Negative" };
      default: return { color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20", label: "Neutral" };
    }
  })();

  const PlatformIcon = (() => {
    const s = mention.source.toLowerCase();
    if (s.includes("twitter") || s.includes("x")) return Twitter;
    if (s.includes("reddit")) return AlertCircle;
    return Globe;
  })();

  const prettyRaw = (() => {
    try {
      return JSON.stringify(mention, null, 2);
    } catch {
      return "Error parsing raw data";
    }
  })();

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20">
      {/* Header Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          className="text-zinc-400 hover:text-white pl-0 gap-2"
          onClick={() => navigate(`/brands/${brandId}/live`)}
        >
          <ArrowLeft className="w-4 h-4" />
          Back to feed
        </Button>
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500">Live Status:</span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
            <span className="text-[10px] font-medium text-emerald-400">Captured</span>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content Column */}
        <div className="lg:col-span-2 space-y-6">

          {/* The Social Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden bg-[#0a0a0b] border border-zinc-800 rounded-2xl shadow-2xl"
          >
            {/* Decoration Gradient */}
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 opacity-50" />

            <div className="p-6 md:p-8 space-y-6">
              {/* Author Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="w-14 h-14 border-2 border-zinc-800 shadow-md">
                    <AvatarImage src={`https://unavatar.io/${authorName}`} />
                    <AvatarFallback className="bg-zinc-800 text-zinc-400">{authorName.substring(0, 2).toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-lg font-bold text-white leading-none mb-1">{authorName}</h3>
                    <div className="flex items-center gap-2 text-sm text-zinc-500">
                      <span>@{authorHandle}</span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(mention.createdAt), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>
                <div className="p-2 bg-zinc-900 rounded-xl border border-zinc-800 text-zinc-400">
                  <PlatformIcon className="w-5 h-5" />
                </div>
              </div>

              {/* Content Body */}
              {(() => {
                // Check if text is truncated (contains [+XXX chars])
                const truncatedMatch = mention.text.match(/\[\+(\d+)\s*chars?\]/);
                const isTruncated = truncatedMatch !== null;
                const charCount = truncatedMatch ? parseInt(truncatedMatch[1], 10) : 0;

                // Get the full text from metadata if available (with type safety)
                const meta = mention.metadata as Record<string, unknown> | undefined;
                const getMetaString = (key: string): string | null => {
                  const val = meta?.[key];
                  return typeof val === 'string' ? val : null;
                };
                const fullText = getMetaString('fullText') || getMetaString('rawText') || getMetaString('content');
                const hasFullText = fullText && fullText !== mention.text && fullText.length > mention.text.length;
                const displayText = expanded && hasFullText ? fullText : mention.text;

                return (
                  <div className="space-y-4">
                    <div className="text-lg md:text-xl text-zinc-200 leading-relaxed font-normal whitespace-pre-wrap">
                      {/* Simple link highlighting */}
                      {displayText.split(' ').map((word: string, i: number) => {
                        if (word.startsWith('http')) return <span key={i} className="text-blue-400 hover:underline cursor-pointer">{word} </span>;
                        if (word.startsWith('#')) return <span key={i} className="text-blue-400">{word} </span>;
                        if (word.startsWith('@')) return <span key={i} className="text-blue-400">{word} </span>;
                        return <span key={i}>{word + ' '}</span>;
                      })}
                    </div>

                    {/* Load More / View Source for truncated content */}
                    {isTruncated && !expanded && (
                      hasFullText ? (
                        <button
                          onClick={() => setExpanded(true)}
                          className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-blue-400 text-sm font-medium transition-all"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Load More ({charCount.toLocaleString()} more characters)
                        </button>
                      ) : postUrl ? (
                        <a
                          href={postUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-blue-400 text-sm font-medium transition-all"
                        >
                          <ExternalLink className="w-4 h-4" />
                          Read Full Article (+{charCount.toLocaleString()} chars)
                        </a>
                      ) : (
                        <div className="text-sm text-zinc-500 italic">
                          +{charCount.toLocaleString()} more characters (full text not available)
                        </div>
                      )
                    )}

                    {expanded && hasFullText && (
                      <button
                        onClick={() => setExpanded(false)}
                        className="flex items-center gap-2 px-4 py-2 bg-zinc-800/50 hover:bg-zinc-700/50 border border-zinc-700/30 rounded-lg text-zinc-400 text-sm font-medium transition-all"
                      >
                        Show Less
                      </button>
                    )}
                  </div>
                );
              })()}

              {/* Meta Footer */}
              <div className="pt-6 border-t border-zinc-800/50 flex flex-wrap gap-4 justify-between items-center text-sm text-zinc-500">
                <div className="flex gap-6">
                  <div className="flex items-center gap-2 hover:text-zinc-300 cursor-pointer transition-colors">
                    <MessageSquare className="w-4 h-4" />
                    <span>Reply</span>
                  </div>
                  <div className="flex items-center gap-2 hover:text-red-400 cursor-pointer transition-colors">
                    <Heart className="w-4 h-4" />
                    <span>Like</span>
                  </div>
                  <div className="flex items-center gap-2 hover:text-green-400 cursor-pointer transition-colors">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </div>
                </div>
                <div className="text-xs">
                  {format(new Date(mention.createdAt), "PPpp")}
                </div>
              </div>
            </div>

            {/* Integration Bar */}
            <div className="bg-zinc-900/50 px-6 py-3 border-t border-zinc-800 flex justify-between items-center">
              <div className="flex gap-3">
                <Badge variant="outline" className={`border-0 ${sentimentConfig.bg} ${sentimentConfig.color}`}>
                  {sentimentConfig.label}
                </Badge>
                <Badge variant="outline" className="border-zinc-700 text-zinc-400">
                  {mention.source}
                </Badge>
              </div>
              {postUrl && (
                <a
                  href={postUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Open Original <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </motion.div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          {/* AI Analysis Card */}
          <Card className="bg-transparent border-zinc-800">
            <CardContent className="p-5 space-y-4">
              <h3 className="font-semibold text-white flex items-center gap-2">
                Analysis
              </h3>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 text-sm text-zinc-400 leading-relaxed">
                  <p>
                    <strong className="text-zinc-300">Sentiment:</strong> Detected as {mention.sentiment} based on keywords in the text.
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 text-sm text-zinc-400 leading-relaxed">
                  <p>
                    <strong className="text-zinc-300">Impact:</strong> Likely to have low immediate impact but worth monitoring for organic engagement.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Developer/Raw Data Toggle */}
          <div className="border-t border-zinc-800 pt-6">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-between text-zinc-500 hover:text-zinc-300"
              onClick={() => setShowRaw(!showRaw)}
            >
              <span className="flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                Developer Data
              </span>
              <span className="text-xs">{showRaw ? "Hide" : "Show"}</span>
            </Button>

            {showRaw && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                className="mt-4"
              >
                <pre className="p-4 rounded-xl bg-black border border-zinc-800 text-[10px] text-zinc-500 font-mono overflow-auto max-h-80 custom-scrollbar">
                  {prettyRaw}
                </pre>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

