/**
 * Deep Scan View Component
 */

import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";
import { DeepScanTerminal } from "@/components/shared/DeepScanTerminal";

interface DeepScanViewProps {
    loading: boolean;
    error: string | null;
    minTimeElapsed: boolean;
    onComplete: () => void;
    brandId: string;
}

export function DeepScanView({ loading, error, minTimeElapsed, onComplete, brandId }: DeepScanViewProps) {
    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[600px]">
                <div className="text-center">
                    <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4 border border-red-500/20">
                        <ShieldAlert className="w-8 h-8 text-red-500" />
                    </div>
                    <h2 className="text-xl font-semibold text-white mb-2">Scan Failed</h2>
                    <p className="text-red-400">{error}</p>
                    <Link
                        to={`/brands/${brandId}/dashboard`}
                        className="inline-block mt-6 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm text-zinc-300 transition-colors"
                    >
                        Return to Base
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[600px] flex items-center justify-center p-6">
            <DeepScanTerminal onComplete={onComplete} />
        </div>
    );
}
