import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClusterSummary } from "@/types/api";
import { parseLabelOrJson } from "@/utils/textParsing";

interface TopicWordCloudProps {
  topics: { term: string; weight: number }[];
  clusters?: ClusterSummary[];
}

export function TopicWordCloud({ topics, clusters }: TopicWordCloudProps) {
  const hasTopics = topics.length > 0;
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredTopics = useMemo(() => {
    if (!searchQuery.trim()) return topics;
    return topics.filter((topic) => {
      const { label } = parseLabelOrJson(topic.term);
      return label.toLowerCase().includes(searchQuery.toLowerCase());
    });
  }, [topics, searchQuery]);

  const clusterLookup = useMemo(() => {
    if (!clusters) {
      return new Map<string, ClusterSummary>();
    }

    const map = new Map<string, ClusterSummary>();
    clusters.forEach((cluster) => {
      map.set(normalizeLabel(cluster.label), cluster);
    });
    return map;
  }, [clusters]);

  const selectedTopic = useMemo(() => {
    if (!selectedTerm) {
      return null;
    }
    return topics.find((topic) => normalizeLabel(topic.term) === selectedTerm) ?? null;
  }, [selectedTerm, topics]);

  const selectedCluster = useMemo(() => {
    if (!selectedTopic) {
      return null;
    }
    return clusterLookup.get(normalizeLabel(selectedTopic.term)) ?? null;
  }, [clusterLookup, selectedTopic]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-semibold">Topic clusters</CardTitle>
        <div className="relative w-40">
          <Search className="absolute left-2 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search topics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 text-xs bg-zinc-900/50 border-zinc-800"
          />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex h-64 flex-wrap items-start justify-center gap-3 overflow-auto">
          {hasTopics ? (
            filteredTopics.length > 0 ? (
              filteredTopics.map((topic) => {
                const { label, isJson } = parseLabelOrJson(topic.term);
                const normalizedTerm = normalizeLabel(topic.term); // Keep original term for selection logic if needed, or use label? 
                // Actually, let's use the label for display and selection consistency if it was JSON.
                // But the selection logic compares against passed topics. 
                // Let's keep selection logic simple: use the original term for ID, but display the parsed label.

                const isSelected = normalizedTerm === selectedTerm;
                const fontSize = Math.max(topic.weight * 42, 14);
                const displayLabel = truncateTopic(label);

                return (
                  <button
                    key={`${topic.term}-${fontSize}`}
                    type="button"
                    onClick={() => setSelectedTerm((prev) => (prev === normalizedTerm ? null : normalizedTerm))}
                    className={`max-w-xs truncate rounded-full px-3 py-1 text-primary transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${isSelected ? "bg-primary text-primary-foreground" : "bg-primary/10 hover:bg-primary/20"
                      }`}
                    style={{ fontSize: `${fontSize}px`, lineHeight: 1.3 }}
                    title={label}
                  >
                    {displayLabel}
                  </button>
                );
              })
            ) : (
              <div className="flex h-full w-full flex-col items-center justify-center text-muted-foreground">
                <Search className="h-8 w-8 opacity-20 mb-2" />
                <span className="text-xs">No topics match "{searchQuery}"</span>
              </div>
            )
          ) : (
            <span className="text-sm text-muted-foreground">No topic clusters generated yet.</span>
          )}
        </div>

        {selectedTopic && (
          <div className="rounded-md border border-border bg-muted/40 p-4 text-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-semibold text-foreground">{selectedTopic.term}</h4>
                <p className="text-xs text-muted-foreground">
                  Relative weight: {formatWeight(selectedTopic.weight)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedTerm(null)}
                className="text-xs font-medium text-primary hover:underline"
              >
                Clear
              </button>
            </div>

            {selectedCluster ? (
              <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
                <li>
                  <strong>Mentions:</strong> {selectedCluster.mentions}
                </li>
                <li>
                  <strong>Spike detected:</strong> {selectedCluster.spike ? "Yes" : "No"}
                </li>
              </ul>
            ) : (
              <p className="mt-3 text-xs text-muted-foreground">No detailed cluster summary available.</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function truncateTopic(text: string, maxLength = 60): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 1)}…`;
}

function normalizeLabel(text: string): string {
  return text.trim().toLowerCase();
}

function formatWeight(weight: number): string {
  if (!Number.isFinite(weight)) {
    return "n/a";
  }
  if (weight > 1) {
    return weight.toFixed(2);
  }
  return `${(weight * 100).toFixed(1)}%`;
}

function parseTopicTerm(text: string): { label: string; isJson: boolean } {
  if (!text.trim().startsWith("{")) {
    return { label: text, isJson: false };
  }
  try {
    const parsed = JSON.parse(text);
    // Try to find a meaningful label from common keys
    const candidates = [
      parsed.topic,
      parsed.category,
      parsed.mention_type,
      parsed.context,
      parsed.label,
      parsed.name
    ];

    // Find the first non-empty string candidate
    const validLabel = candidates.find(c => typeof c === 'string' && c.trim().length > 0);

    if (validLabel) {
      return { label: validLabel, isJson: true };
    }

    return { label: text, isJson: false };
  } catch (e) {
    return { label: text, isJson: false };
  }
}

