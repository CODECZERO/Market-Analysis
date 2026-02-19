import type { ComponentType } from "react";
import { NavLink, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { LogOut, Settings, ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  items: {
    label: string;
    to: string;
    icon: ComponentType<{ className?: string }>;
    badge?: string | number;
  }[];
  title?: string;
}

export function Sidebar({ items, title }: SidebarProps) {
  const { user, logout } = useAuth();

  return (
    <aside className="hidden h-screen w-64 border-r border-zinc-800 bg-[#0a0a0b] md:flex md:flex-col">
      {/* Content */}
      <div className="flex flex-col h-full p-4">
        {/* Logo Header */}
        <Link to="/brands" className="group mb-6 px-2">
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="flex items-center gap-3"
          >
            <img
              src="/logo.png"
              alt="Avichal Logo"
              className="w-9 h-9 rounded-lg"
            />
            <div>
              <h1 className="text-base font-semibold text-white">
                {title ?? "Avichal"}
              </h1>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                Brand Intelligence
              </p>
            </div>
          </motion.div>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 space-y-1">
          <p className="text-[10px] font-medium uppercase tracking-wider text-zinc-500 mb-2 px-3">
            Menu
          </p>
          {items.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.to}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-blue-500/10 text-white border border-blue-500/20"
                        : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <Icon className={cn(
                        "h-4 w-4",
                        isActive ? "text-blue-500" : "text-zinc-500 group-hover:text-zinc-300"
                      )} />
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-blue-500/20 text-blue-400">
                          {item.badge}
                        </span>
                      )}
                      <ChevronRight className={cn(
                        "h-3.5 w-3.5 opacity-0 -translate-x-1 transition-all",
                        isActive ? "opacity-100 translate-x-0 text-blue-500" : "group-hover:opacity-50 group-hover:translate-x-0"
                      )} />
                    </>
                  )}
                </NavLink>
              </motion.div>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="mt-auto pt-4 border-t border-zinc-800 space-y-2">
          {/* Settings Link */}
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-500 hover:text-white hover:bg-zinc-800/50"
              )
            }
          >
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </NavLink>

          {/* User Profile */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500 text-sm font-medium">
              {user?.name?.charAt(0).toUpperCase() ?? "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.name ?? "User"}
              </p>
              <p className="text-xs text-zinc-500 truncate">
                {user?.email ?? "user@example.com"}
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => logout()}
              className="p-1.5 rounded-md text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
              title="Logout"
            >
              <LogOut className="h-3.5 w-3.5" />
            </motion.button>
          </div>
        </div>
      </div>
    </aside>
  );
}
