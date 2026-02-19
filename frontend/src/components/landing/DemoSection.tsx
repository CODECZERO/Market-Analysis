import { motion } from "framer-motion";

// Platform icons with actual logos
const platforms = [
    {
        name: "Reddit",
        color: "#FF4500",
        logo: (
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z" />
            </svg>
        )
    },
    {
        name: "Twitter",
        color: "#FFFFFF",
        logo: (
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
        )
    },
    {
        name: "Hacker News",
        color: "#FF6600",
        logo: (
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                <path d="M0 0v24h24V0H0zm12.8 14.4v5.2h-1.6v-5.2L7.8 7.6h1.8l2.4 4.8 2.4-4.8h1.8l-3.4 6.8z" />
            </svg>
        )
    },
    {
        name: "YouTube",
        color: "#FF0000",
        logo: (
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
        )
    },
    {
        name: "News",
        color: "#10B981",
        logo: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
        )
    },
    {
        name: "RSS",
        color: "#F97316",
        logo: (
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                <path d="M6.18 15.64a2.18 2.18 0 0 1 2.18 2.18C8.36 19 7.38 20 6.18 20 5 20 4 19 4 17.82a2.18 2.18 0 0 1 2.18-2.18zM4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44zm0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1z" />
            </svg>
        )
    },
];

const listItemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0 },
};

export function DemoSection() {
    return (
        <section className="relative py-24 bg-[#0a0a0b] overflow-hidden">
            <div className="absolute top-1/2 right-0 w-[600px] h-[400px] bg-blue-500/5 rounded-full blur-[100px] -translate-y-1/2" />

            <div className="max-w-6xl mx-auto px-6">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Left - Content */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-zinc-800 bg-zinc-900/50 text-sm text-zinc-400 mb-6"
                        >
                            <motion.span animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 2, repeat: Infinity }} className="w-1.5 h-1.5 rounded-full bg-green-500" />
                            <span>Real-time monitoring</span>
                        </motion.div>

                        <h2 className="text-3xl md:text-4xl font-semibold text-white mb-4">
                            Everything in one place
                        </h2>

                        <p className="text-lg text-zinc-400 mb-8 leading-relaxed">
                            Stop jumping between tabs. See every mention, understand every sentiment,
                            and catch every trend from a single, beautiful dashboard.
                        </p>

                        {/* Why use it */}
                        <motion.div
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            transition={{ staggerChildren: 0.1 }}
                            className="space-y-4 mb-8"
                        >
                            {[
                                { title: "Catch what you'd miss", desc: "We scan the entire internet so you don't have to." },
                                { title: "Know the sentiment instantly", desc: "AI tells you if it's good or bad before you read it." },
                                { title: "Be the first to know", desc: "Get alerts in seconds, not days. Respond when it matters." },
                                { title: "Focus on what matters", desc: "Filter noise and see only what needs your attention." },
                            ].map((item, i) => (
                                <motion.div
                                    key={item.title}
                                    variants={listItemVariants}
                                    transition={{ duration: 0.4, delay: i * 0.1 }}
                                    whileHover={{ x: 4 }}
                                    className="flex gap-3 cursor-default"
                                >
                                    <motion.div
                                        whileHover={{ scale: 1.2 }}
                                        className="w-5 h-5 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-0.5"
                                    >
                                        <svg className="w-3 h-3 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                        </svg>
                                    </motion.div>
                                    <div>
                                        <p className="text-white font-medium">{item.title}</p>
                                        <p className="text-sm text-zinc-500">{item.desc}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </motion.div>

                        {/* Platforms */}
                        <div className="flex flex-wrap items-center gap-4">
                            <span className="text-sm text-zinc-500">We monitor:</span>
                            <div className="flex flex-wrap gap-2">
                                {platforms.map((platform, i) => (
                                    <motion.div
                                        key={platform.name}
                                        initial={{ opacity: 0, scale: 0 }}
                                        whileInView={{ opacity: 1, scale: 1 }}
                                        viewport={{ once: true }}
                                        transition={{ delay: 0.5 + i * 0.08, type: "spring", stiffness: 300 }}
                                        whileHover={{ scale: 1.15, y: -3, rotate: 5 }}
                                        className="w-9 h-9 rounded-lg flex items-center justify-center cursor-pointer"
                                        style={{ backgroundColor: `${platform.color}20`, color: platform.color }}
                                        title={platform.name}
                                    >
                                        {platform.logo}
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </motion.div>

                    {/* Right - Dashboard preview */}
                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="relative"
                    >
                        {/* Floating icons */}
                        {[platforms[0], platforms[2], platforms[3], platforms[5]].map((platform, i) => (
                            <motion.div
                                key={platform.name}
                                initial={{ opacity: 0, scale: 0 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
                                transition={{
                                    y: { duration: 3 + i * 0.5, repeat: Infinity, ease: "easeInOut" },
                                    rotate: { duration: 4 + i * 0.5, repeat: Infinity, ease: "easeInOut" },
                                    opacity: { delay: 0.8 + i * 0.1 },
                                    scale: { delay: 0.8 + i * 0.1, type: "spring" }
                                }}
                                className="absolute w-10 h-10 rounded-xl flex items-center justify-center shadow-lg z-20"
                                style={{ backgroundColor: platform.color, color: "white", top: i === 0 ? "5%" : i === 1 ? "70%" : i === 2 ? "20%" : "80%", left: i === 0 ? "0%" : i === 1 ? "0%" : i === 2 ? "90%" : "88%" }}
                            >
                                {platform.logo}
                            </motion.div>
                        ))}

                        {/* Dashboard */}
                        <motion.div
                            whileHover={{ y: -6, scale: 1.01 }}
                            transition={{ type: "spring", stiffness: 300 }}
                            className="relative rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden shadow-2xl shadow-black/50"
                        >
                            <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800 bg-zinc-900">
                                <div className="w-3 h-3 rounded-full bg-zinc-700" />
                                <div className="w-3 h-3 rounded-full bg-zinc-700" />
                                <div className="w-3 h-3 rounded-full bg-zinc-700" />
                                <span className="ml-3 text-xs text-zinc-500">Your Dashboard</span>
                            </div>

                            <div className="p-6 space-y-4">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.4 }}
                                    className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50"
                                >
                                    <div className="flex items-center justify-between mb-3">
                                        <span className="text-sm text-zinc-400">Brand Health</span>
                                        <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ duration: 2, repeat: Infinity }} className="text-xs text-green-500 flex items-center gap-1">
                                            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                                            Healthy
                                        </motion.span>
                                    </div>
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-4xl font-semibold text-white">87</span>
                                        <span className="text-sm text-zinc-500">/ 100</span>
                                    </div>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.5 }}
                                    className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50"
                                >
                                    <span className="text-sm text-zinc-400 block mb-3">How people feel</span>
                                    <div className="space-y-2">
                                        {[{ label: "Positive", value: 65, color: "bg-green-500" }, { label: "Neutral", value: 25, color: "bg-zinc-500" }, { label: "Negative", value: 10, color: "bg-red-500" }].map((item, i) => (
                                            <div key={item.label} className="flex items-center gap-3">
                                                <span className="text-xs text-zinc-500 w-16">{item.label}</span>
                                                <div className="flex-1 h-2 rounded-full bg-zinc-700 overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        whileInView={{ width: `${item.value}%` }}
                                                        viewport={{ once: true }}
                                                        transition={{ delay: 0.7 + i * 0.15, duration: 1, ease: "easeOut" }}
                                                        className={`h-full rounded-full ${item.color}`}
                                                    />
                                                </div>
                                                <span className="text-xs text-zinc-400 w-8">{item.value}%</span>
                                            </div>
                                        ))}
                                    </div>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.6 }}
                                    className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50"
                                >
                                    <span className="text-sm text-zinc-400 block mb-3">Just now</span>
                                    <div className="flex items-start gap-3">
                                        <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 2, repeat: Infinity }} className="w-8 h-8 rounded-full bg-[#FF4500]/20 flex items-center justify-center flex-shrink-0 text-[#FF4500]">
                                            {platforms[0].logo}
                                        </motion.div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm text-zinc-300">"Just discovered this tool. Absolute game changer for our team."</p>
                                            <p className="text-xs text-zinc-500 mt-1">r/startups · 1 min ago</p>
                                        </div>
                                        <span className="px-2 py-1 text-xs rounded bg-green-500/10 text-green-500 flex-shrink-0">Positive</span>
                                    </div>
                                </motion.div>
                            </div>
                        </motion.div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
