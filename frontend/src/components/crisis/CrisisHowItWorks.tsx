/**
 * Crisis How It Works Component
 * 
 * Explanatory section for the crisis monitor
 */

import { motion } from "framer-motion";
import { Zap, Activity, Shield } from "lucide-react";

export function CrisisHowItWorks() {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="border-t border-zinc-800/50 pt-6"
        >
            <div className="grid sm:grid-cols-3 gap-6">
                <div className="group">
                    <div className="flex items-center gap-2.5 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
                            <Zap className="w-4 h-4 text-blue-500" />
                        </div>
                        <h3 className="text-sm font-semibold text-white">Velocity Detection</h3>
                    </div>
                    <p className="text-xs text-zinc-500 leading-relaxed pl-[42px]">
                        Algorithms analyze mention rate vs baseline. Accelerated growth triggers alerts.
                    </p>
                </div>
                <div className="group">
                    <div className="flex items-center gap-2.5 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center group-hover:bg-amber-500/20 transition-colors">
                            <Activity className="w-4 h-4 text-amber-500" />
                        </div>
                        <h3 className="text-sm font-semibold text-white">Sentiment Analysis</h3>
                    </div>
                    <p className="text-xs text-zinc-500 leading-relaxed pl-[42px]">
                        NLP models weigh emotional intensity. High negative sentiment flags immediately.
                    </p>
                </div>
                <div className="group">
                    <div className="flex items-center gap-2.5 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center group-hover:bg-red-500/20 transition-colors">
                            <Shield className="w-4 h-4 text-red-500" />
                        </div>
                        <h3 className="text-sm font-semibold text-white">Viral Prediction</h3>
                    </div>
                    <p className="text-xs text-zinc-500 leading-relaxed pl-[42px]">
                        Pattern matching predicts if topics will explode within 4 hours.
                    </p>
                </div>
            </div>
        </motion.div>
    );
}
