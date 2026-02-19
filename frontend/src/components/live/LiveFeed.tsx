/**
 * Live Feed Component
 */

import { motion } from "framer-motion";
import { RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/shared/LoadingState";
import { LiveMentionList } from "@/components/mentions/LiveMentionList"; // Assuming this exists as imported in original file
import type { Mention } from "@/types/api"; // Assuming type

interface LiveFeedProps {
    mentions: Mention[];
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
    isFetching: boolean;
    onRetry: () => void;
}

export function LiveFeed({
    mentions,
    isLoading,
    isError,
    error,
    isFetching,
    onRetry
}: LiveFeedProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            <Card className="border-zinc-800 bg-zinc-900/50">
                <CardHeader className="border-b border-zinc-800">
                    <CardTitle className="text-lg font-semibold flex items-center justify-between">
                        <span className="flex items-center gap-2">
                            <span>Live</span>
                            Recent Mentions
                        </span>
                        {isFetching && (
                            <span className="text-xs text-zinc-500 flex items-center gap-2">
                                <RefreshCw className="h-3 w-3 animate-spin" />
                                Updating...
                            </span>
                        )}
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading && mentions.length === 0 && (
                        <div className="p-8">
                            <LoadingState message="Loading live mentions..." />
                        </div>
                    )}

                    {isError && (
                        <div className="p-6 text-center">
                            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/10 mb-4">
                                <span className="text-2xl">!</span>
                            </div>
                            <p className="text-sm text-red-400 mb-4">
                                {error?.message ?? "Failed to load mentions"}
                            </p>
                            <Button
                                variant="outline"
                                size="sm"
                                className="border-zinc-700"
                                onClick={onRetry}
                            >
                                Try Again
                            </Button>
                        </div>
                    )}

                    {!isLoading && !isError && mentions.length === 0 && (
                        <div className="p-12 text-center">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-800 mb-4">
                                <span className="text-3xl">Empty</span>
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">No mentions yet</h3>
                            <p className="text-sm text-zinc-400 max-w-sm mx-auto">
                                Mentions will appear here as they are detected. Check back soon!
                            </p>
                        </div>
                    )}

                    {!isLoading && !isError && mentions.length > 0 && (
                        <LiveMentionList mentions={mentions} grouped />
                    )}
                </CardContent>
            </Card>
        </motion.div>
    );
}
