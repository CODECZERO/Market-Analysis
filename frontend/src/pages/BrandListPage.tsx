/**
 * Brand List Page
 * 
 * Main dashboard for viewing all active brands.
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Plus, Building2 } from "lucide-react";

import { BrandStats, BrandListing, ActionCards } from "@/components/brands";
import { Button } from "@/components/ui/button";
import { useBrands } from "@/hooks/useBrands";

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
};

export default function BrandListPage() {
  const { data, isLoading, isError, error } = useBrands();
  const brandCount = data?.length ?? 0;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 pb-24"
    >
      {/* Header */}
      <motion.div
        variants={cardVariants}
        className="flex flex-wrap items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Building2 className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-white">
              Brand Command Center
            </h1>
            <p className="text-sm text-zinc-400">
              Monitor and protect your brand reputation
            </p>
          </div>
        </div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button asChild className="bg-blue-600 hover:bg-blue-500 gap-2 px-5 h-10">
            <Link to="/brands/create">
              <Plus className="h-4 w-4" />
              Add Brand
            </Link>
          </Button>
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={cardVariants}>
        <BrandStats brandCount={brandCount} />
      </motion.div>

      {/* Brand List */}
      <motion.div variants={cardVariants}>
        <BrandListing
          data={data}
          isLoading={isLoading}
          isError={isError}
          error={error}
        />
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={cardVariants}>
        <ActionCards />
      </motion.div>
    </motion.div>
  );
}
