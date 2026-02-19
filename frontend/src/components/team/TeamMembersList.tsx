/**
 * Team Members List
 */

import { motion } from "framer-motion";
import { Users, Trash2, Crown, Shield, Eye, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TeamMember } from "@/hooks/team";

interface TeamMembersListProps {
    members: TeamMember[];
    loading: boolean;
    onRemove: (id: string) => void;
    onInviteClick: () => void;
}

const roleColors = {
    admin: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    member: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    viewer: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
};

const roleIcons = {
    admin: <Crown className="w-3 h-3" />,
    member: <Shield className="w-3 h-3" />,
    viewer: <Eye className="w-3 h-3" />
};

export function TeamMembersList({ members, loading, onRemove, onInviteClick }: TeamMembersListProps) {
    return (
        <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
            <CardHeader className="border-b border-zinc-800/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                        <Users className="h-4 w-4 text-blue-400" />
                    </div>
                    Team Members
                    <span className="text-sm font-normal text-zinc-500">
                        ({members.length})
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                {loading ? (
                    <div className="p-8 text-center text-zinc-500">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                        Loading team...
                    </div>
                ) : members.length === 0 ? (
                    <div className="p-12 text-center">
                        <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center mx-auto mb-4">
                            <Users className="w-6 h-6 text-zinc-500" />
                        </div>
                        <h3 className="text-lg font-medium text-white mb-2">No Team Members</h3>
                        <p className="text-sm text-zinc-400 mb-6">
                            Invite your first team member to collaborate.
                        </p>
                        <Button onClick={onInviteClick} variant="outline">
                            Invite Member
                        </Button>
                    </div>
                ) : (
                    <div className="divide-y divide-zinc-800/50">
                        {members.map((member, index) => (
                            <motion.div
                                key={member.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="p-4 flex items-center justify-between hover:bg-zinc-800/30 transition-colors group"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-medium">
                                        {member.name?.charAt(0).toUpperCase() || member.email.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h4 className="font-medium text-white">
                                                {member.name || member.email}
                                            </h4>
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border flex items-center gap-1 ${roleColors[member.role]}`}>
                                                {roleIcons[member.role]}
                                                {member.role}
                                            </span>
                                        </div>
                                        <p className="text-sm text-zinc-500">{member.email}</p>
                                    </div>
                                </div>
                                {member.role !== 'admin' && (
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => onRemove(member.id)}
                                        className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                )}
                            </motion.div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
