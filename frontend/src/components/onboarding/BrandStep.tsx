/**
 * Brand Step Component
 * 
 * First step of onboarding - brand name input
 */

import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface BrandStepProps {
    brandName: string;
    setBrandName: (value: string) => void;
}

export function BrandStep({ brandName, setBrandName }: BrandStepProps) {
    return (
        <motion.div
            key="brand"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">What are we tracking?</h2>
                <p className="text-zinc-400">Enter your brand, product, or company name.</p>
            </div>
            <div className="space-y-2">
                <Label className="text-zinc-300">Brand Name</Label>
                <Input
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    placeholder="e.g. Acme Corp"
                    className="bg-zinc-800 border-zinc-700 text-lg h-12"
                    autoFocus
                />
            </div>
        </motion.div>
    );
}
