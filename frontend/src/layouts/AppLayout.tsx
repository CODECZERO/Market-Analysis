import { Outlet, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { appNavItems } from "@/lib/navigation";

import { useWakeUpService, ColdStartLoader } from "@/hooks/useWakeUpService";

export default function AppLayout() {
  const location = useLocation();
  const { isWaking, error, retry } = useWakeUpService();

  return (
    <div className="flex min-h-screen bg-[#0a0a0b] text-white">
      {/* Subtle gradient orb - matches landing page */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.03, 0.05, 0.03],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/4 right-1/4 w-[800px] h-[500px] bg-blue-500 rounded-full blur-[150px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.05, 1],
            opacity: [0.02, 0.04, 0.02],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-1/4 left-1/4 w-[600px] h-[400px] bg-purple-500 rounded-full blur-[120px]"
        />
      </div>

      {/* Subtle grid background - matches landing page */}
      <div
        className="fixed inset-0 opacity-[0.02] pointer-events-none z-0"
        style={{
          backgroundImage: `linear-gradient(#fff 1px, transparent 1px),
                  linear-gradient(90deg, #fff 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
      />

      <ColdStartLoader isWaking={isWaking} error={error} onRetry={retry} />
      <Sidebar items={appNavItems} title="Avichal" />
      <div className="flex flex-1 flex-col relative z-10">
        <Topbar pathname={location.pathname} />
        <main className="flex-1 p-6">
          <div className="mx-auto w-full max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
