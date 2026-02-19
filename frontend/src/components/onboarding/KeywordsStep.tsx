/**
 * Keywords Step Component
 * 
 * Second step of onboarding - keyword input
 */

import { motion } from "framer-motion";
import { Label } from "@/components/ui/label";
import { KeywordInput } from "@/components/shared/KeywordInput";

interface KeywordsStepProps {
    keywords: string[];
    setKeywords: (value: string[]) => void;
}

export function KeywordsStep({ keywords, setKeywords }: KeywordsStepProps) {
    return (
        <motion.div
            key="keywords"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Refine your search</h2>
                <p className="text-zinc-400">Add variations, hashtags, or specific products.</p>
            </div>
            <div className="space-y-2">
                <Label className="text-zinc-300">Keywords</Label>
                <KeywordInput
                    value={keywords}
                    onChange={setKeywords}
                    placeholder="Type and press Enter..."
                />
            </div>
        </motion.div>
    );
}
