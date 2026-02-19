/**
 * Recent Users Table Component
 */

import { motion } from "framer-motion";
import { User, Mail, Trash2, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { RecentUser } from "@/hooks/admin/useAdminDashboard";

interface RecentUsersTableProps {
    users: RecentUser[];
    onDelete: (id: string, name: string) => void;
}

export function RecentUsersTable({ users, onDelete }: RecentUsersTableProps) {
    return (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50">
            <div className="p-4 border-b border-zinc-800">
                <h3 className="font-semibold text-white">Recent Signups</h3>
                <p className="text-sm text-zinc-400">Newest users on the platform</p>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-zinc-800 hover:bg-zinc-800/50 font-medium text-xs text-zinc-400 text-left">
                            <th className="py-3 px-4">User</th>
                            <th className="py-3 px-4">Status</th>
                            <th className="py-3 px-4">Joined</th>
                            <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="text-center py-8 text-zinc-500">
                                    No users found
                                </td>
                            </tr>
                        ) : (
                            users.map((user, i) => (
                                <motion.tr
                                    key={user.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="border-b last:border-0 border-zinc-800 hover:bg-zinc-800/50 group"
                                >
                                    <td className="p-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center border border-zinc-700">
                                                <User className="w-4 h-4 text-zinc-400" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-white text-sm">{user.name}</p>
                                                <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                                                    <Mail className="w-3 h-3" />
                                                    {user.email}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Badge variant="secondary" className="bg-green-500/10 text-green-400 border-green-500/20 font-normal">
                                            Active
                                        </Badge>
                                    </td>
                                    <td className="p-4 text-zinc-400 text-sm">
                                        <div className="flex items-center gap-1.5">
                                            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
                                            {new Date(user.signupDate).toLocaleDateString()}
                                        </div>
                                    </td>
                                    <td className="p-4 text-right">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-500/10"
                                            onClick={() => onDelete(user.id, user.name)}
                                            title="Delete User"
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
