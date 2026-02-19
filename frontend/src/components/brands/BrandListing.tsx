/**
 * Brand Listing Component
 * 
 * Displays the list of brands with loading/error states
 */

import { Link } from "react-router-dom";

import { motion } from "framer-motion";
import { Shield, Building2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/shared/LoadingState";
import { BrandTable } from "./BrandTable";
import type { BrandListResponse } from "@/types/api";

interface BrandListingProps {
    data: BrandListResponse | undefined;
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
}

export function BrandListing({ data, isLoading, isError, error }: BrandListingProps) {
    return (
        <div className="rounded-xl bg-zinc-900/50 border border-zinc-800 overflow-hidden">
            <div className="border-b border-zinc-800 px-5 py-4">
                <h2 className="text-base font-medium text-white">Brand Overview</h2>
            </div>
            <div>
                {isLoading && (
                    <div className="p-8">
                        <LoadingState message="Fetching your brands..." />
                    </div>
                )}

                {isError && (
                    <div className="p-8 text-center">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 mb-4">
                            <Shield className="w-5 h-5 text-red-400" />
                        </div>
                        <p className="text-sm text-red-400 mb-4">
                            {error?.message ?? "Unable to load brands"}
                        </p>
                        <Button
                            variant="outline"
                            size="sm"
                            className="border-zinc-700 hover:bg-zinc-800"
                            onClick={() => window.location.reload()}
                        >
                            Retry
                        </Button>
                    </div>
                )}

                {data && data.length === 0 && (
                    <div className="p-12 text-center">
                        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-zinc-800 border border-zinc-700 mb-5">
                            <Building2 className="w-6 h-6 text-zinc-500" />
                        </div>
                        <h3 className="text-lg font-medium text-white mb-2">No brands yet</h3>
                        <p className="text-sm text-zinc-400 mb-6 max-w-sm mx-auto">
                            Start monitoring your brand reputation by adding your first brand.
                        </p>
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                            <Button asChild className="bg-blue-600 hover:bg-blue-500 px-5 h-10">
                                <Link to="/brands/create">
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Your First Brand
                                </Link>
                            </Button>
                        </motion.div>
                    </div>
                )}

                {data && data.length > 0 && <BrandTable brands={data} />}
            </div>
        </div>
    );
}
