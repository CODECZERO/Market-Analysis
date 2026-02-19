import { FormEvent, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Plus, Sparkles, Tag, FileText, CheckCircle2 } from "lucide-react";

import { KeywordInput } from "@/components/shared/KeywordInput";
import { LoadingState } from "@/components/shared/LoadingState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useCreateBrand } from "@/hooks/useBrands";
import { type CreateBrandRequest } from "@/types/api";

export default function CreateBrandPage() {
  const navigate = useNavigate();
  const mutation = useCreateBrand();

  const [brandName, setBrandName] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  // Calculate progress
  const progress = [
    brandName.trim().length > 0,
    keywords.length > 0,
  ].filter(Boolean).length;

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setValidationError("");

    if (!brandName.trim()) {
      setValidationError("Brand name is required");
      return;
    }
    if (keywords.length === 0) {
      setValidationError("Add at least one keyword to track");
      return;
    }

    const payload: CreateBrandRequest = {
      brandName: brandName.trim(),
      keywords,
    };

    mutation.mutate(payload, {
      onSuccess: (response) => {
        navigate(`/brands/${response.slug}/dashboard`);
      },
    });
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl px-4"
      >
        {/* Back Button */}
        <Link
          to="/brands"
          className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Brands
        </Link>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            Create New Brand
          </h1>
          <p className="text-zinc-400 mt-2">
            Set up monitoring for your brand in just a few steps
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-zinc-400">Progress</span>
            <span className="text-sm font-medium text-white">{progress}/2 completed</span>
          </div>
          <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-600 to-purple-600"
              initial={{ width: 0 }}
              animate={{ width: `${(progress / 2) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Form Card */}
        <Card className="border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-blue-950/10">
          <form onSubmit={onSubmit}>
            <CardHeader className="border-b border-zinc-800">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-400" />
                Brand Details
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6 pt-6">
              {/* Brand Name */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                  <Tag className="h-4 w-4 text-zinc-500" />
                  Brand Name
                </label>
                <Input
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  placeholder="e.g., Acme Corp"
                  className="bg-zinc-800/50 border-zinc-700 focus:border-blue-500"
                  required
                />
                <p className="text-xs text-zinc-500">
                  The primary name of your company or product
                </p>
              </div>

              {/* Keywords */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                  <Plus className="h-4 w-4 text-zinc-500" />
                  Keywords to Track
                </label>
                <KeywordInput
                  value={keywords}
                  onChange={setKeywords}
                  placeholder="Add keyword and press Enter"
                />
                <p className="text-xs text-zinc-500">
                  Include variations, hashtags, product names, and common misspellings
                </p>
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                  <FileText className="h-4 w-4 text-zinc-500" />
                  Internal Notes
                  <span className="text-zinc-600">(optional)</span>
                </label>
                <Textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Any notes for your team..."
                  className="bg-zinc-800/50 border-zinc-700 focus:border-blue-500 min-h-[80px]"
                />
              </div>

              {/* Validation Error */}
              {validationError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400"
                >
                  {validationError}
                </motion.div>
              )}

              {/* Mutation Error */}
              {mutation.isError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400"
                >
                  {(mutation.error as any)?.response?.data?.message ?? mutation.error?.message ?? "Failed to create brand"}
                </motion.div>
              )}

              {/* Loading */}
              {mutation.isPending && <LoadingState message="Creating your brand..." />}

              {/* Success */}
              {mutation.isSuccess && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3"
                >
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  <span className="text-sm text-emerald-400">
                    Brand created! Redirecting to dashboard...
                  </span>
                </motion.div>
              )}
            </CardContent>

            <CardFooter className="border-t border-zinc-800 flex justify-between">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate(-1)}
                className="text-zinc-400 hover:text-white"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={mutation.isPending || mutation.isSuccess}
                className="bg-blue-600 hover:bg-blue-500 gap-2"
              >
                {mutation.isPending ? (
                  "Creating..."
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Create Brand
                  </>
                )}
              </Button>
            </CardFooter>
          </form>
        </Card>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 p-4 rounded-xl border border-zinc-800 bg-zinc-900/30"
        >
          <p className="text-sm font-medium text-zinc-300 mb-2">💡 Pro Tips</p>
          <ul className="text-xs text-zinc-500 space-y-1">
            <li>• Include common misspellings of your brand name</li>
            <li>• Add product names and hashtags you want to monitor</li>
            <li>• The more keywords, the better coverage you'll have</li>
          </ul>
        </motion.div>
      </motion.div>
    </div>
  );
}
