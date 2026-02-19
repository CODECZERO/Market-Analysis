import { NavLink, Outlet, useParams } from "react-router-dom";

import { useBrand } from "@/hooks/useBrands";
import { brandNavItems } from "@/lib/navigation";
import { cn } from "@/lib/utils";

export default function BrandLayout() {
  const { brandId = "" } = useParams();
  const { data: brand, isLoading } = useBrand(brandId);

  const navItems = brandId ? brandNavItems(brandId) : [];

  return (
    <div className="space-y-6">
      {/* Premium Glass Morphism Header */}
      <div className="relative overflow-hidden rounded-xl border border-zinc-800/50 bg-gradient-to-br from-zinc-900/90 via-zinc-900/80 to-zinc-900/70 p-6 backdrop-blur-xl shadow-xl">
        {/* Subtle gradient accent orb */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-500 mb-1">Brand Dashboard</p>
              <h2 className="text-3xl font-semibold text-white tracking-tight">
                {isLoading ? "Loading brand..." : brand?.name ?? brandId ?? "Unknown brand"}
              </h2>
            </div>
            <div className="text-xs text-zinc-500 bg-zinc-800/50 px-3 py-1.5 rounded-full border border-zinc-700/50">
              Slug: <span className="text-zinc-400">{(brand?.slug ?? brandId) || "n/a"}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                      : "bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-white border border-zinc-700/50"
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
      <Outlet />
    </div>
  );
}
