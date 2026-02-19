import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const plans = [
    {
        name: "Starter",
        price: { monthly: 49, annual: 39 },
        description: "Perfect for small businesses and startups",
        features: [
            "1 Brand",
            "5,000 mentions/month",
            "3 Team members",
            "Email alerts",
            "7-day data retention",
            "Basic sentiment analysis",
        ],
        cta: "Start Free Trial",
        popular: false,
    },
    {
        name: "Professional",
        price: { monthly: 149, annual: 119 },
        description: "For growing teams that need more power",
        features: [
            "5 Brands",
            "50,000 mentions/month",
            "10 Team members",
            "Email + Slack + Discord",
            "30-day data retention",
            "Advanced AI (emotions, sarcasm)",
            "Crisis detection",
            "Custom alerts",
            "API access",
        ],
        cta: "Start Free Trial",
        popular: true,
    },
    {
        name: "Enterprise",
        price: { monthly: 499, annual: 399 },
        description: "For large organizations with complex needs",
        features: [
            "Unlimited Brands",
            "Unlimited mentions",
            "Unlimited Team members",
            "All notification channels",
            "1-year data retention",
            "Full AI suite",
            "Dedicated support",
            "Custom integrations",
            "SLA guarantee",
            "SSO / SAML",
        ],
        cta: "Contact Sales",
        popular: false,
    },
];

export function PricingSection() {
    const [isAnnual, setIsAnnual] = useState(true);

    return (
        <section className="relative py-32 bg-slate-950">
            {/* Background accent */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-purple-500/10 rounded-full blur-3xl" />

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
                        Simple, Transparent Pricing
                    </h2>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
                        Start free. Scale as you grow. No hidden fees.
                    </p>

                    {/* Billing toggle */}
                    <div className="inline-flex items-center gap-4 p-1.5 rounded-xl bg-slate-800 border border-slate-700">
                        <button
                            onClick={() => setIsAnnual(false)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!isAnnual ? "bg-white text-slate-900" : "text-slate-400 hover:text-white"
                                }`}
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setIsAnnual(true)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${isAnnual ? "bg-white text-slate-900" : "text-slate-400 hover:text-white"
                                }`}
                        >
                            Annual
                            <span className="ml-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded-full">
                                Save 20%
                            </span>
                        </button>
                    </div>
                </motion.div>

                {/* Pricing cards */}
                <div className="grid md:grid-cols-3 gap-8 lg:gap-6">
                    {plans.map((plan, index) => (
                        <motion.div
                            key={plan.name}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className={`relative p-8 rounded-2xl border transition-all ${plan.popular
                                    ? "bg-gradient-to-b from-purple-500/10 to-slate-900 border-purple-500/50 scale-105"
                                    : "bg-slate-900 border-slate-800 hover:border-slate-700"
                                }`}
                        >
                            {/* Popular badge */}
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                    <span className="px-4 py-1.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-semibold rounded-full">
                                        Most Popular
                                    </span>
                                </div>
                            )}

                            {/* Plan header */}
                            <div className="text-center mb-8">
                                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                                <p className="text-slate-400 text-sm mb-6">{plan.description}</p>
                                <div className="flex items-baseline justify-center gap-1">
                                    <span className="text-5xl font-bold text-white">
                                        ${isAnnual ? plan.price.annual : plan.price.monthly}
                                    </span>
                                    <span className="text-slate-400">/month</span>
                                </div>
                                {isAnnual && (
                                    <p className="text-sm text-green-400 mt-2">
                                        Billed annually (${(isAnnual ? plan.price.annual : plan.price.monthly) * 12}/year)
                                    </p>
                                )}
                            </div>

                            {/* Features */}
                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature) => (
                                    <li key={feature} className="flex items-start gap-3 text-slate-300">
                                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        {feature}
                                    </li>
                                ))}
                            </ul>

                            {/* CTA */}
                            <Link
                                to={plan.name === "Enterprise" ? "/contact" : "/signup"}
                                className={`block w-full py-3 text-center rounded-xl font-semibold transition-all ${plan.popular
                                        ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/25"
                                        : "bg-white/10 text-white hover:bg-white/20 border border-white/10"
                                    }`}
                            >
                                {plan.cta}
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
