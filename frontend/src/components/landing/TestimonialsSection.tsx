import { motion } from "framer-motion";

const testimonials = [
    {
        quote: "Avichal caught a potential PR crisis 3 hours before it went viral. That early warning saved us millions in damage control.",
        author: "Sarah Chen",
        role: "Head of Communications",
        company: "TechCorp Industries",
        avatar: "SC",
    },
    {
        quote: "The AI sentiment analysis is incredibly accurate. It even detects sarcasm which was causing false positives with our previous tool.",
        author: "Marcus Rodriguez",
        role: "Brand Manager",
        company: "GrowthCo",
        avatar: "MR",
    },
    {
        quote: "Integration took 10 minutes. Now our entire team gets Slack alerts for any mention above 1000 engagements. Game changer.",
        author: "Emily Watson",
        role: "Social Media Director",
        company: "MediaOne Agency",
        avatar: "EW",
    },
];

export function TestimonialsSection() {
    return (
        <section className="relative py-32 bg-slate-900 overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-1/2 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2" />
            <div className="absolute top-1/2 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -translate-y-1/2" />

            <div className="relative max-w-7xl mx-auto px-6">
                {/* Section header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Loved by Brand Teams
                    </h2>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                        Join hundreds of companies protecting their reputation with Avichal.
                    </p>
                </motion.div>

                {/* Testimonials grid */}
                <div className="grid md:grid-cols-3 gap-8">
                    {testimonials.map((testimonial, index) => (
                        <motion.div
                            key={testimonial.author}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="relative p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50"
                        >
                            {/* Quote icon */}
                            <svg className="w-10 h-10 text-purple-500/30 mb-6" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                            </svg>

                            {/* Quote */}
                            <p className="text-slate-300 text-lg leading-relaxed mb-8">
                                "{testimonial.quote}"
                            </p>

                            {/* Author */}
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
                                    {testimonial.avatar}
                                </div>
                                <div>
                                    <div className="font-semibold text-white">{testimonial.author}</div>
                                    <div className="text-sm text-slate-400">
                                        {testimonial.role}, {testimonial.company}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
