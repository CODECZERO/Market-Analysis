/**
 * Live Stats Component
 */

import { motion } from "framer-motion";
import { MessageSquare, Radio, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface LiveStatsProps {
    mentionCount: number;
}

export function LiveStats({ mentionCount }: LiveStatsProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid gap-4 sm:grid-cols-3"
        >
            <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-blue-950/20">
                <CardContent className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                        <MessageSquare className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-white">{mentionCount}</p>
                        <p className="text-xs text-zinc-500">Total Mentions</p>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-emerald-950/20">
                <CardContent className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                        <Radio className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-white">Live</p>
                        <p className="text-xs text-zinc-500">Status</p>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-amber-950/20">
                <CardContent className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                        <Clock className="h-5 w-5 text-amber-400" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-white">10s</p>
                        <p className="text-xs text-zinc-500">Refresh Rate</p>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
