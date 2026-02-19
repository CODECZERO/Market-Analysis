/**
 * Connect Sources Step Component
 * 
 * Final step of onboarding - data source toggle
 */

import { motion } from "framer-motion";

interface Sources {
    reddit: boolean;
    hackernews: boolean;
    google: boolean;
}

interface ConnectStepProps {
    sources: Sources;
    setSources: React.Dispatch<React.SetStateAction<Sources>>;
}

export function ConnectStep({ sources, setSources }: ConnectStepProps) {
    return (
        <motion.div
            key="connect"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Connect Data Sources</h2>
                <p className="text-zinc-400">Where should we listen for mentions?</p>
            </div>

            <div className="space-y-3">
                {Object.entries(sources).map(([key, enabled]) => (
                    <div key={key} className="flex items-center justify-between p-4 bg-zinc-800/50 rounded-lg border border-zinc-800">
                        <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${enabled ? 'bg-green-500' : 'bg-zinc-600'}`} />
                            <span className="capitalize text-zinc-200 font-medium">{key}</span>
                        </div>
                        <div
                            onClick={() => setSources(prev => ({ ...prev, [key]: !prev[key as keyof Sources] }))}
                            className={`
                                w-12 h-6 rounded-full p-1 cursor-pointer transition-colors
                                ${enabled ? 'bg-blue-600' : 'bg-zinc-700'}
                            `}
                        >
                            <motion.div
                                className="w-4 h-4 rounded-full bg-white shadow-sm"
                                animate={{ x: enabled ? 24 : 0 }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </motion.div>
    );
}
