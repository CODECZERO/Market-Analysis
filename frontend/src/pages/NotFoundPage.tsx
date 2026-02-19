import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Home, Search, Shield, DollarSign } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-[#0a0a0b]">
      {/* Subtle grid background - matching landing page */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(#fff 1px, transparent 1px),
                  linear-gradient(90deg, #fff 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
      />

      {/* Animated Background Gradients - subtle */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-blue-500 rounded-full blur-[150px]"
          animate={{
            x: [0, 30, 0],
            y: [0, 20, 0],
            opacity: [0.03, 0.05, 0.03],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-purple-500 rounded-full blur-[120px]"
          animate={{
            x: [0, -20, 0],
            y: [0, -30, 0],
            opacity: [0.02, 0.04, 0.02],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 flex flex-col items-center text-center px-6"
      >
        {/* 404 Text - refined size */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="relative mb-6"
        >
          <span className="text-[120px] sm:text-[140px] font-bold leading-none bg-gradient-to-br from-zinc-600 via-zinc-500 to-zinc-700 bg-clip-text text-transparent">
            404
          </span>
          <motion.div
            className="absolute inset-0 text-[120px] sm:text-[140px] font-bold leading-none bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 bg-clip-text text-transparent blur-2xl"
            animate={{ opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            404
          </motion.div>
        </motion.div>

        {/* Message */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="space-y-2 mb-8"
        >
          <h1 className="text-2xl font-semibold text-white">
            Page Not Found
          </h1>
          <p className="text-sm text-zinc-400 max-w-md">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="flex flex-wrap gap-3 justify-center"
        >
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button asChild className="bg-blue-600 hover:bg-blue-500 text-white px-5 h-10">
              <Link to="/brands">
                <Home className="mr-2 h-4 w-4" />
                Go to Dashboard
              </Link>
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button asChild variant="outline" className="border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800 text-zinc-300 h-10">
              <Link to="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Link>
            </Button>
          </motion.div>
        </motion.div>

        {/* Quick Links - matching landing page card style */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="mt-12 p-5 rounded-xl bg-zinc-900/50 border border-zinc-800"
        >
          <p className="text-xs text-zinc-500 mb-4">Quick navigation</p>
          <div className="grid grid-cols-3 gap-3">
            <QuickLink to="/brands" icon={<Search className="w-4 h-4" />} label="Brands" />
            <QuickLink to="/crisis" icon={<Shield className="w-4 h-4" />} label="Crisis" />
            <QuickLink to="/money-mode" icon={<DollarSign className="w-4 h-4" />} label="Money Mode" />
          </div>
        </motion.div>
      </motion.div>

      {/* Footer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.5 }}
        className="absolute bottom-6 text-xs text-zinc-600"
      >
        {new Date().getFullYear()} Avichal — Brand Intelligence Platform
      </motion.p>
    </div>
  );
}

function QuickLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <motion.div whileHover={{ y: -2 }}>
      <Link
        to={to}
        className="flex flex-col items-center gap-2 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 hover:border-blue-500/30 transition-colors group"
      >
        <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500 group-hover:scale-105 transition-transform">
          {icon}
        </div>
        <span className="text-xs text-zinc-400 group-hover:text-white transition-colors">{label}</span>
      </Link>
    </motion.div>
  );
}
