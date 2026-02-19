import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function TermsPage() {
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
                <h1 className="text-3xl font-semibold text-white mb-2">Terms of Service</h1>
                <p className="text-sm text-zinc-500 mb-8">Last updated: December 27, 2024</p>

                <div className="space-y-8 text-zinc-400 leading-relaxed">
                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">1. Acceptance of Terms</h2>
                        <p>
                            By accessing or using Avichal ("the Service"), you agree to be bound by these Terms of Service.
                            If you do not agree to these terms, do not use the Service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">2. Description of Service</h2>
                        <p>
                            Avichal is a brand monitoring platform that aggregates publicly available mentions of your brand
                            from various online sources including social media, news sites, and forums. The Service uses AI to
                            analyze sentiment and provide insights.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">3. User Accounts</h2>
                        <ul className="list-disc list-inside space-y-2">
                            <li>You must provide accurate information when creating an account</li>
                            <li>You are responsible for maintaining the security of your account credentials</li>
                            <li>You must notify us immediately of any unauthorized access</li>
                            <li>One person or entity may not maintain multiple free accounts</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">4. Acceptable Use</h2>
                        <p className="mb-3">You agree not to:</p>
                        <ul className="list-disc list-inside space-y-2">
                            <li>Use the Service for any unlawful purpose</li>
                            <li>Attempt to gain unauthorized access to any part of the Service</li>
                            <li>Interfere with or disrupt the Service or servers</li>
                            <li>Use automated systems to access the Service beyond normal usage</li>
                            <li>Monitor brands you do not have legitimate interest in</li>
                            <li>Resell or redistribute the Service without authorization</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">5. Data and Privacy</h2>
                        <p>
                            We collect and process data as described in our <Link to="/privacy" className="text-blue-500 hover:text-blue-400">Privacy Policy</Link>.
                            By using the Service, you consent to such collection and processing.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">6. Third-Party Data Sources</h2>
                        <p>
                            The Service aggregates publicly available data from third-party sources. We do not guarantee the
                            accuracy, completeness, or availability of this data. Third-party platforms may change their
                            policies at any time, which may affect Service functionality.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">7. Intellectual Property</h2>
                        <p>
                            The Service and its original content, features, and functionality are owned by Avichal
                            and are protected by international copyright, trademark, and other intellectual property laws.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">8. Limitation of Liability</h2>
                        <p>
                            The Service is provided "as is" without warranties of any kind. We shall not be liable for any
                            indirect, incidental, special, consequential, or punitive damages resulting from your use of
                            the Service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">9. Changes to Terms</h2>
                        <p>
                            We reserve the right to modify these terms at any time. We will notify users of significant
                            changes via email or through the Service. Continued use after changes constitutes acceptance.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-medium text-white mb-3">10. Contact</h2>
                        <p>
                            For questions about these Terms, contact us at <span className="text-blue-500">legal@brandtracker.io</span>
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
