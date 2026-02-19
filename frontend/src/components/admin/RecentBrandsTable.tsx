/**
 * Recent Brands Table Component
 */

import { motion } from "framer-motion";
import { Building2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BrandRecord } from "@/types/api";

interface RecentBrandsTableProps {
    brands: BrandRecord[];
    onDelete: (id: string, name: string) => void;
}

export function RecentBrandsTable({ brands, onDelete }: RecentBrandsTableProps) {
    return (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50">
            <div className="p-4 border-b border-zinc-800">
                <h3 className="font-semibold text-white">Recent Brands</h3>
                <p className="text-sm text-zinc-400">Latest brands added to the platform</p>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-zinc-800 hover:bg-zinc-800/50 font-medium text-xs text-zinc-400 text-left">
                            <th className="py-3 px-4">Brand Name</th>
                            <th className="py-3 px-4">Slug</th>
                            <th className="py-3 px-4">Keywords</th>
                            <th className="py-3 px-4">Created</th>
                            <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {brands.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="text-center py-8 text-zinc-500">
                                    No brands found
                                </td>
                            </tr>
                        ) : (
                            brands.map((brand, i) => (
                                <motion.tr
                                    key={brand.slug}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="border-b last:border-0 border-zinc-800 hover:bg-zinc-800/50 group"
                                >
                                    <td className="p-4 font-medium text-white max-w-[200px] truncate">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                                                <Building2 className="w-4 h-4" />
                                            </div>
                                            {brand.name}
                                        </div>
                                    </td>
                                    <td className="p-4 text-zinc-400 font-mono text-xs">{brand.slug}</td>
                                    <td className="p-4">
                                        <div className="flex gap-1 flex-wrap">
                                            {brand.keywords?.slice(0, 2).map((k, idx) => (
                                                <Badge key={idx} variant="outline" className="border-zinc-700 text-zinc-400 text-[10px]">
                                                    {k}
                                                </Badge>
                                            ))}
                                            {(brand.keywords?.length || 0) > 2 && (
                                                <span className="text-[10px] text-zinc-500">+{brand.keywords!.length - 2}</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="p-4 text-zinc-400 text-sm">
                                        {new Date(brand.createdAt || Date.now()).toLocaleDateString()}
                                    </td>
                                    <td className="p-4 text-right">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => onDelete(brand.slug, brand.name)}
                                            className="h-8 w-8 p-0 text-zinc-400 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </td>
                                </motion.tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
