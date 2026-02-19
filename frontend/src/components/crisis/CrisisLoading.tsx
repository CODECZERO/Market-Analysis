/**
 * Crisis Loading State
 */

export function CrisisLoading() {
    return (
        <div className="grid lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4">
                <div className="rounded-2xl bg-zinc-900/30 border border-zinc-800/50 p-6 h-96 animate-pulse" />
            </div>
            <div className="lg:col-span-8 space-y-6">
                <div className="rounded-2xl bg-zinc-900/30 border border-zinc-800/50 p-6 h-64 animate-pulse" />
                <div className="rounded-2xl bg-zinc-900/30 border border-zinc-800/50 p-6 h-48 animate-pulse" />
            </div>
        </div>
    );
}
