/**
 * Money Header Component
 */

import { motion } from "framer-motion";

export function MoneyHeader() {
    return (
        <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-xl bg-gradient-to-r from-emerald-900/20 to-teal-900/20 border border-emerald-500/10 p-4 md:p-6"
        >
            <div className="relative z-10 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 shrink-0">
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div>
                    <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">Money Mode</h1>
                    <p className="text-xs md:text-sm text-zinc-400 mt-0.5 max-w-md">
                        AI-powered commercial intent detection that identifies hot leads from social conversations.
                    </p>
                </div>
            </div>
            {/* Decorative background elements */}
            <div className="absolute top-0 right-0 -mt-16 -mr-16 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl opacity-30" />
        </motion.div>
    );
}
