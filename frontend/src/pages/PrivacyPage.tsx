import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0b] text-zinc-300">
            {/* Header */}
            <header className="border-b border-zinc-800">
                <div className="max-w-4xl mx-auto px-6 py-6">
                    <Link to="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                            </svg>
                        </div>
                        <span className="text-lg font-semibold text-white">Avichal</span>
                    </Link>
                </div>
            </header>

            {/* Content */}
            <motion.main
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-4xl mx-auto px-6 py-12"
            >
                <h1 className="text-3xl font-semibold text-white mb-2">Privacy Policy</h1>
                <p className="text-sm text-zinc-500 mb-8">Last updated: December 27, 2024</p>

                <div className="space-y-8 text-zinc-400 leading-relaxed">
                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">1. Information We Collect</h2>
                        <p className="mb-3">We collect information you provide directly:</p>
                        <ul className="list-disc list-inside space-y-2">
                            <li>Account information (name, email, password)</li>
                            <li>Brand names and keywords you choose to monitor</li>
                            <li>Notification preferences and settings</li>
                        </ul>
                        <p className="mt-3">We automatically collect:</p>
                        <ul className="list-disc list-inside space-y-2">
                            <li>Usage data and analytics</li>
                            <li>Device and browser information</li>
                            <li>IP address and approximate location</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">2. How We Use Your Information</h2>
                        <ul className="list-disc list-inside space-y-2">
                            <li>To provide and improve the Service</li>
                            <li>To send you alerts and notifications</li>
                            <li>To communicate about updates and features</li>
                            <li>To detect and prevent fraud or abuse</li>
                            <li>To comply with legal obligations</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">3. Data We Monitor</h2>
                        <p>
                            Avichal aggregates publicly available data from social media, news sites, and forums.
                            We only collect data that is publicly accessible. We do not access private messages,
                            private accounts, or any information behind authentication walls.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">4. Data Sharing</h2>
                        <p className="mb-3">We do not sell your personal data. We may share data with:</p>
                        <ul className="list-disc list-inside space-y-2">
                            <li>Service providers who assist in operating our platform</li>
                            <li>Legal authorities when required by law</li>
                            <li>Business partners with your explicit consent</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">5. Data Retention</h2>
                        <p>
                            We retain your account data for as long as your account is active. Mention data is retained
                            for 90 days by default, after which it is archived or deleted. You can request data deletion
                            at any time.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">6. Your Rights (GDPR/CCPA)</h2>
                        <p className="mb-3">You have the right to:</p>
                        <ul className="list-disc list-inside space-y-2">
                            <li>Access your personal data</li>
                            <li>Correct inaccurate data</li>
                            <li>Request deletion of your data</li>
                            <li>Export your data in a portable format</li>
                            <li>Opt out of marketing communications</li>
                            <li>Withdraw consent at any time</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">7. Security</h2>
                        <p>
                            We implement industry-standard security measures including encryption in transit (TLS),
                            secure password hashing, and regular security audits. However, no method of transmission
                            over the Internet is 100% secure.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">8. Cookies</h2>
                        <p>
                            We use essential cookies for authentication and session management. We use analytics cookies
                            to understand how users interact with our Service. You can control cookie preferences in
                            your browser settings.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">9. Changes to This Policy</h2>
                        <p>
                            We may update this Privacy Policy periodically. We will notify you of significant changes
                            via email or through the Service at least 30 days before they take effect.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">10. Contact</h2>
                        <p>
                            For privacy-related inquiries, contact our Data Protection Officer at{" "}
                            <span className="text-blue-500">privacy@brandtracker.io</span>
                        </p>
                    </section>
                </div>

                <div className="mt-12 pt-8 border-t border-zinc-800">
                    <Link to="/" className="text-blue-500 hover:text-blue-400">
                        ← Back to home
                    </Link>
                </div>
            </motion.main>
        </div>
    );
}
