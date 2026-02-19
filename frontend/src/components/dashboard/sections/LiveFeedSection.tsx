/**
 * Live Feed Section
 */

import { Activity } from "lucide-react";
import { SectionHeader } from "@/components/shared";
import { LoadingState } from "@/components/shared/LoadingState";
import { LiveMentionList } from "@/components/mentions/LiveMentionList";

interface LiveFeedSectionProps {
    summary: any;
    mentions: any[];
    isLoading: boolean;
}

export function LiveFeedSection({ summary, mentions, isLoading }: LiveFeedSectionProps) {
    return (
        <section>
            <SectionHeader
                icon={Activity}
                title="Live Feed"
                subtitle="Real-time mentions and briefing"
            />

            <div className="grid gap-4 lg:grid-cols-3">
                {/* Live Mentions */}
                <div className="lg:col-span-2 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        Live Mentions
                    </h3>
                    {isLoading && <LoadingState message="Loading mentions..." />}
                    {!isLoading && mentions && <LiveMentionList mentions={mentions} />}
                </div>

                {/* Latest Briefing */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col h-[380px]">
                    <h3 className="text-sm font-semibold text-white mb-3">Latest Briefing</h3>
                    <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                        <p className="text-sm leading-relaxed text-zinc-400">
                            {summary?.summary ?? "No summary generated yet."}
                        </p>
                    </div>

                    <div className="mt-4 pt-4 border-t border-zinc-800/50">
                        <h4 className="text-xs font-medium text-zinc-500 mb-2">Trending Topics</h4>
                        <div className="flex flex-wrap gap-2">
                            {(summary?.dominantTopics ?? []).slice(0, 5).map((topic: string) => (
                                <span key={topic} className="text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded-lg border border-blue-500/20">
                                    {topic}
                                </span>
                            ))}
                            {!summary?.dominantTopics?.length && (
                                <span className="text-xs text-zinc-600 italic">Topics appear after analysis</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
