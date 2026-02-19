/**
 * Add Competitor Modal
 * 
 * Form modal for adding a new competitor
 */

import { motion, AnimatePresence } from "framer-motion";
import { X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface AddCompetitorModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string, keywords: string) => void;
    isCreating: boolean;
    name: string;
    setName: (name: string) => void;
    keywords: string;
    setKeywords: (keywords: string) => void;
}

export function AddCompetitorModal({
    isOpen,
    onClose,
    onSubmit,
    isCreating,
    name,
    setName,
    keywords,
    setKeywords,
}: AddCompetitorModalProps) {
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(name, keywords);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="bg-zinc-900/90 border border-zinc-700/50 backdrop-blur-xl rounded-2xl p-6 w-full max-w-md shadow-2xl relative"
                    >
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 text-zinc-500 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <h2 className="text-xl font-semibold text-white mb-6">Add New Competitor</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Competitor Name</label>
                                <Input
                                    type="text"
                                    required
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="e.g., Acme Corp"
                                    className="bg-zinc-950/50 border-zinc-800 focus:border-purple-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Keywords (comma-separated)</label>
                                <Input
                                    type="text"
                                    value={keywords}
                                    onChange={(e) => setKeywords(e.target.value)}
                                    placeholder="e.g., acme, acme corp, acmecorp"
                                    className="bg-zinc-950/50 border-zinc-800 focus:border-purple-500"
                                />
                                <p className="text-xs text-zinc-500 mt-1">Keywords used to track competitor mentions</p>
                            </div>

                            <div className="flex justify-end gap-3 mt-8">
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={onClose}
                                    className="text-zinc-400 hover:text-white"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    disabled={isCreating}
                                    className="bg-purple-600 hover:bg-purple-500 text-white min-w-[100px]"
                                >
                                    {isCreating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add Competitor"}
                                </Button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
