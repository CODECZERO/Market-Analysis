import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Helmet } from "react-helmet-async";

// This page is generated for programmatic SEO
// URL pattern: /brand/:brandSlug (e.g., /brand/nike, /brand/apple)
export default function BrandSEOPage() {
    const { brandSlug } = useParams<{ brandSlug: string }>();
    const brandName = brandSlug ? brandSlug.charAt(0).toUpperCase() + brandSlug.slice(1) : "Your Brand";

    return (
        <>
            <Helmet>
                <title>{brandName} Brand Monitoring | Track {brandName} Mentions Online | Avichal</title>
                <meta
                    name="description"
                    content={`Monitor ${brandName} mentions across Reddit, Twitter, Hacker News, and news sites. Get real-time alerts and AI sentiment analysis for ${brandName}.`}
                />
                <meta name="keywords" content={`${brandName} mentions, ${brandName} brand monitoring, ${brandName} sentiment, track ${brandName} online`} />
                <link rel="canonical" href={`https://brandtracker.io/brand/${brandSlug}`} />

                {/* Open Graph */}
                <meta property="og:title" content={`Monitor ${brandName} Brand Mentions | Avichal`} />
                <meta property="og:description" content={`Real-time ${brandName} monitoring across social media, forums, and news. AI-powered sentiment analysis.`} />
                <meta property="og:type" content="website" />
                <meta property="og:url" content={`https://brandtracker.io/brand/${brandSlug}`} />

                {/* Twitter Card */}
                <meta name="twitter:card" content="summary_large_image" />
                <meta name="twitter:title" content={`Monitor ${brandName} Mentions | Avichal`} />
                <meta name="twitter:description" content={`Track what people say about ${brandName} online. AI sentiment analysis.`} />

                {/* Structured Data */}
                <script type="application/ld+json">
                    {JSON.stringify({
                        "@context": "https://schema.org",
                        "@type": "SoftwareApplication",
                        "name": `${brandName} Brand Monitoring - Avichal`,
                        "description": `Monitor ${brandName} mentions and sentiment across social media and news sites`,
                        "applicationCategory": "BusinessApplication",
                        "offers": {
                            "@type": "Offer",
                            "price": "0",
                            "priceCurrency": "USD",
                        },
                    })}
                </script>
            </Helmet>

            <div className="min-h-screen bg-[#0a0a0b] text-zinc-300">
                {/* Header */}
                <header className="border-b border-zinc-800">
                    <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                        <Link to="/" className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                                </svg>
                            </div>
                            <span className="text-lg font-semibold text-white">Avichal</span>
                        </Link>
                        <Link to="/signup" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors">
                            Start Free
                        </Link>
                    </div>
                </header>

                {/* Hero */}
                <section className="py-16">
                    <div className="max-w-4xl mx-auto px-6 text-center">
                        <motion.h1
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-4xl md:text-5xl font-semibold text-white mb-4"
                        >
                            Monitor <span className="text-blue-500">{brandName}</span> Mentions Online
                        </motion.h1>
                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="text-lg text-zinc-400 mb-8 max-w-2xl mx-auto"
                        >
                            Track what people say about {brandName} on Reddit, Twitter, Hacker News, YouTube,
                            and news sites. Get AI-powered sentiment analysis and instant alerts.
                        </motion.p>
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            <Link
                                to="/signup"
                                className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors"
                            >
                                Start Monitoring {brandName} Free
                            </Link>
                            <p className="text-sm text-zinc-500 mt-3">No credit card required</p>
                        </motion.div>
                    </div>
                </section>

                {/* Features for this brand */}
                <section className="py-16 bg-zinc-900/50">
                    <div className="max-w-6xl mx-auto px-6">
                        <h2 className="text-2xl font-semibold text-white text-center mb-12">
                            What You Can Track for {brandName}
                        </h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            {[
                                {
                                    title: "Social Mentions",
                                    description: `See every time someone mentions ${brandName} on Reddit, Twitter, or Hacker News.`,
                                },
                                {
                                    title: "Sentiment Analysis",
                                    description: `Know if people are speaking positively or negatively about ${brandName}.`,
                                },
                                {
                                    title: "Crisis Alerts",
                                    description: `Get notified when negative sentiment about ${brandName} spikes.`,
                                },
                            ].map((feature, i) => (
                                <motion.div
                                    key={feature.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: i * 0.1 }}
                                    className="p-6 rounded-xl bg-zinc-800/50 border border-zinc-700"
                                >
                                    <h3 className="text-lg font-medium text-white mb-2">{feature.title}</h3>
                                    <p className="text-sm text-zinc-400">{feature.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* CTA */}
                <section className="py-16">
                    <div className="max-w-2xl mx-auto px-6 text-center">
                        <h2 className="text-2xl font-semibold text-white mb-4">
                            Start Monitoring {brandName} Today
                        </h2>
                        <p className="text-zinc-400 mb-8">
                            Join hundreds of brands using Avichal.
                        </p>
                        <Link
                            to="/signup"
                            className="inline-flex items-center justify-center px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors"
                        >
                            Create Free Account
                        </Link>
                    </div>
                </section>

                {/* Footer */}
                <footer className="border-t border-zinc-800 py-8">
                    <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-zinc-500">2024 Avichal. All rights reserved.</p>
                        <div className="flex gap-6 text-sm text-zinc-500">
                            <Link to="/privacy" className="hover:text-zinc-300">Privacy</Link>
                            <Link to="/terms" className="hover:text-zinc-300">Terms</Link>
                            <Link to="/" className="hover:text-zinc-300">Home</Link>
                        </div>
                    </div>
                </footer>
            </div>
        </>
    );
}
