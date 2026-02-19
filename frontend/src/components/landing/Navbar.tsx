import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

export function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <motion.nav
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                ? "bg-[#0a0a0b]/90 backdrop-blur-md border-b border-zinc-800"
                : "bg-transparent"
                }`}
        >
            <div className="max-w-6xl mx-auto px-6">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2">
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            className="w-8 h-8"
                        >
                            <img
                                src="/logo.png"
                                alt="Avichal Logo"
                                className="w-8 h-8 rounded-lg"
                            />
                        </motion.div>
                        <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Avichal</span>
                    </Link>

                    {/* Desktop nav */}
                    <div className="hidden md:flex items-center gap-8">
                        <motion.a
                            href="#features"
                            whileHover={{ color: "#ffffff" }}
                            className="text-sm text-zinc-400 transition-colors"
                        >
                            Features
                        </motion.a>
                        <motion.div whileHover={{ color: "#ffffff" }}>
                            <Link to="/docs" className="text-sm text-zinc-400 transition-colors">
                                Docs
                            </Link>
                        </motion.div>
                    </div>

                    {/* CTA */}
                    <div className="hidden md:flex items-center gap-4">
                        <motion.div whileHover={{ color: "#ffffff" }}>
                            <Link
                                to="/login"
                                className="text-sm text-zinc-400 transition-colors"
                            >
                                Sign in
                            </Link>
                        </motion.div>
                        <motion.div
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Link
                                to="/signup"
                                className="text-sm px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                            >
                                Get started
                            </Link>
                        </motion.div>
                    </div>

                    {/* Mobile menu button */}
                    <motion.button
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 text-zinc-400 hover:text-white"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            {isMobileMenuOpen ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </motion.button>
                </div>

                {/* Mobile menu */}
                <AnimatePresence>
                    {isMobileMenuOpen && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="md:hidden overflow-hidden"
                        >
                            <div className="py-4 border-t border-zinc-800">
                                <div className="flex flex-col gap-4">
                                    <a href="#features" className="text-sm text-zinc-400 hover:text-white transition-colors">
                                        Features
                                    </a>
                                    <Link to="/docs" className="text-sm text-zinc-400 hover:text-white transition-colors">
                                        Docs
                                    </Link>
                                    <hr className="border-zinc-800" />
                                    <Link to="/login" className="text-sm text-zinc-400 hover:text-white transition-colors">
                                        Sign in
                                    </Link>
                                    <Link
                                        to="/signup"
                                        className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg text-center"
                                    >
                                        Get started
                                    </Link>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.nav>
    );
}
