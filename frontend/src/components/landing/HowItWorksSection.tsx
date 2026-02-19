import { motion } from "framer-motion";

const steps = [
    {
        number: "01",
        title: "Tell us your brand",
        description: "Enter your brand name and a few keywords. Takes 30 seconds. No technical setup needed.",
    },
    {
        number: "02",
        title: "We start watching",
        description: "Our AI begins scanning Reddit, Twitter, news sites, and more. You get your first mentions within minutes.",
    },
    {
        number: "03",
        title: "You stay informed",
        description: "Get instant alerts when something important happens. Respond to opportunities and threats in real-time.",
    },
];

const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.2 } },
};

const stepVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
};

export function HowItWorksSection() {
    return (
        <section id="how-it-works" className="relative py-24 bg-[#111113]">
            <div className="max-w-6xl mx-auto px-6">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-semibold text-white mb-4">
                        Up and running in under a minute
                    </h2>
                    <p className="text-lg text-zinc-400 max-w-xl mx-auto">
                        No complex integrations. No API keys. Just enter your brand and start monitoring.
                    </p>
                </motion.div>

                {/* Steps */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                    className="grid md:grid-cols-3 gap-8"
                >
                    {steps.map((step, index) => (
                        <motion.div key={step.number} variants={stepVariants} className="relative">
                            {index < steps.length - 1 && (
                                <motion.div
                                    initial={{ scaleX: 0 }}
                                    whileInView={{ scaleX: 1 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.5 + index * 0.2, duration: 0.6 }}
                                    className="hidden md:block absolute top-8 left-[calc(50%+40px)] w-[calc(100%-80px)] h-px bg-zinc-800 origin-left"
                                />
                            )}
                            <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.2 }} className="text-center">
                                <motion.div
                                    whileHover={{ scale: 1.05, borderColor: "rgb(59, 130, 246)" }}
                                    transition={{ duration: 0.2 }}
                                    className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-900 border border-zinc-800 mb-6 transition-colors"
                                >
                                    <span className="text-xl font-semibold text-blue-500">{step.number}</span>
                                </motion.div>
                                <h3 className="text-lg font-medium text-white mb-2">{step.title}</h3>
                                <p className="text-sm text-zinc-400 leading-relaxed max-w-xs mx-auto">{step.description}</p>
                            </motion.div>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
