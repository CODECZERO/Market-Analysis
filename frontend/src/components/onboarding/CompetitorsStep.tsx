/**
 * Competitors Step Component
 * 
 * Fourth step of onboarding - competitor input
 */

import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface CompetitorsStepProps {
    competitors: string[];
    setCompetitors: (value: string[]) => void;
    newCompetitor: string;
    setNewCompetitor: (value: string) => void;
    onAddCompetitor: (e?: React.FormEvent) => void;
}

export function CompetitorsStep({
    competitors,
    setCompetitors,
    newCompetitor,
    setNewCompetitor,
    onAddCompetitor,
}: CompetitorsStepProps) {
    return (
        <motion.div
            key="competitors"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Who are your rivals?</h2>
                <p className="text-zinc-400">We'll track them to find gaps and opportunities.</p>
            </div>

            <form onSubmit={onAddCompetitor} className="flex gap-2">
                <Input
                    value={newCompetitor}
                    onChange={(e) => setNewCompetitor(e.target.value)}
                    placeholder="Add competitor URL or name"
                    className="bg-zinc-800 border-zinc-700"
                />
                <Button type="submit" variant="secondary" disabled={!newCompetitor.trim()}>
                    Add
                </Button>
            </form>

            <div className="flex flex-wrap gap-2 min-h-[100px] content-start">
                {competitors.map((comp, idx) => (
                    <span key={idx} className="bg-zinc-800 text-zinc-200 px-3 py-1 rounded-full text-sm border border-zinc-700 flex items-center gap-2">
                        {comp}
                        <button
                            onClick={() => setCompetitors(competitors.filter((_, i) => i !== idx))}
                            className="hover:text-red-400"
                        >
                            ×
                        </button>
                    </span>
                ))}
                {competitors.length === 0 && (
                    <div className="w-full text-center text-zinc-600 py-4 italic">
                        No competitors added yet. You can skip this.
                    </div>
                )}
            </div>
        </motion.div>
    );
}
