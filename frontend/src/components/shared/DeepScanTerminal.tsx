import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Terminal, CheckCircle2, Loader2, ShieldCheck, Globe, BrainCircuit } from "lucide-react";

interface LogEntry {
    id: string;
    message: string;
    status: "pending" | "success" | "processing";
    timestamp: string;
}

export function DeepScanTerminal({ onComplete }: { onComplete?: () => void }) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const steps = [
        "Initializing neural extraction protocol...",
        "Connecting to secure aggregated feed...",
        "Bypassing biological bot detection...",
        "Scraping SERP top 10 results...",
        "Decrypting textual content layers...",
        "Running sentiment vector analysis...",
        "Clustering semantic topics...",
        "Generating strategic opportunities matrix...",
        "Finalizing intelligence report..."
    ];

    useEffect(() => {
        let stepIndex = 0;

        const addLog = (message: string, status: LogEntry["status"] = "processing") => {
            setLogs(prev => {
                const newLogs = [...prev];
                // Mark previous as success
                if (newLogs.length > 0 && newLogs[newLogs.length - 1].status === "processing") {
                    newLogs[newLogs.length - 1].status = "success";
                }
                return [
                    ...newLogs,
                    {
                        id: Math.random().toString(36),
                        message,
                        status,
                        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit", fractionalSecondDigits: 3 })
                    }
                ];
            });
        };

        const interval = setInterval(() => {
            if (stepIndex >= steps.length) {
                // Final success mark
                setLogs(prev => {
                    const newLogs = [...prev];
                    if (newLogs.length > 0) newLogs[newLogs.length - 1].status = "success";
                    return newLogs;
                });
                clearInterval(interval);
                setTimeout(() => onComplete?.(), 1000);
                return;
            }

            addLog(steps[stepIndex]);
            stepIndex++;

            if (scrollRef.current) {
                scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }
        }, 800); // Speed of logs

        return () => clearInterval(interval);
    }, []);

    // Auto scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-3xl mx-auto"
        >
            <div className="bg-[#0c0c0e] border border-zinc-800 rounded-lg overflow-hidden font-mono shadow-2xl">
                {/* Terminal Header */}
                <div className="bg-zinc-900/50 px-4 py-2 border-b border-zinc-800 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-zinc-400" />
                        <span className="text-xs text-zinc-400">ARGOS_INTELLIGENCE_CORE_V4.0</span>
                    </div>
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                        <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                        <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                    </div>
                </div>

                {/* Terminal Body */}
                <div ref={scrollRef} className="h-[400px] overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                    {logs.map((log) => (
                        <div key={log.id} className="flex items-start gap-3 text-sm">
                            <span className="text-zinc-600 shrink-0">[{log.timestamp}]</span>
                            <div className="flex items-center gap-2">
                                {log.status === "processing" && <Loader2 className="w-3 h-3 text-blue-500 animate-spin" />}
                                {log.status === "success" && <CheckCircle2 className="w-3 h-3 text-emerald-500" />}
                                <span className={log.status === "processing" ? "text-blue-400" : "text-zinc-300"}>
                                    {log.message}
                                </span>
                            </div>
                        </div>
                    ))}

                    {logs.length > 0 && logs[logs.length - 1].status === "processing" && (
                        <div className="pl-[100px] text-blue-500/50 text-xs animate-pulse">
                            _ processing
                        </div>
                    )}
                </div>

                {/* Status Footer */}
                <div className="bg-zinc-950 px-4 py-2 border-t border-zinc-900 flex items-center justify-between text-xs">
                    <div className="flex gap-4">
                        <span className="flex items-center gap-1.5 text-zinc-500">
                            <ShieldCheck className="w-3 h-3 text-emerald-500" />
                            SECURE_CONNECTION
                        </span>
                        <span className="flex items-center gap-1.5 text-zinc-500">
                            <Globe className="w-3 h-3 text-blue-500" />
                            NETWORK_ACTIVE
                        </span>
                        <span className="flex items-center gap-1.5 text-zinc-500">
                            <BrainCircuit className="w-3 h-3 text-purple-500" />
                            NEURAL_ENGINE_ONLINE
                        </span>
                    </div>
                    <div className="text-zinc-600">
                        MEM_USAGE: 34MB | CPU: 12%
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
