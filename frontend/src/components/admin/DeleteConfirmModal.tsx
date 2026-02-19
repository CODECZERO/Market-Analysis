/**
 * Delete Confirm Modal Component
 * 
 * Confirmation dialog for deleting users or brands
 */

import { motion } from "framer-motion";

interface DeleteModalState {
    type: "user" | "brand";
    id: string;
    name: string;
}

interface DeleteConfirmModalProps {
    data: DeleteModalState | null;
    onClose: () => void;
    onConfirm: () => void;
}

export function DeleteConfirmModal({ data, onClose, onConfirm }: DeleteConfirmModalProps) {
    if (!data) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-sm w-full shadow-xl"
            >
                <h3 className="text-lg font-bold text-white mb-2">Confirm Deletion</h3>
                <p className="text-zinc-400 text-sm mb-6">
                    Are you sure you want to delete <b>{data.name}</b>?
                    <br />
                    <span className="text-red-400 block mt-2 text-xs">
                        Warning: This action is irreversible and will delete all associated data (mentions, stats, etc).
                    </span>
                </p>
                <div className="flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onConfirm}
                        className="px-4 py-2 text-sm bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 rounded-lg transition font-medium"
                    >
                        Delete {data.type === 'user' ? 'User' : 'Brand'}
                    </button>
                </div>
            </motion.div>
        </div>
    );
}

export type { DeleteModalState };
