/**
 * Team Settings Page
 * 
 * Manage team members, invitations, and role-based permissions.
 */

import { motion } from 'framer-motion';
import { Users, UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';

import { useTeamSettings } from '@/hooks/team';
import { TeamMembersList, PendingInvitationsList, InviteTeamModal } from '@/components/team';

export default function TeamSettingsPage() {
    const {
        members,
        invitations,
        loading,
        showInviteModal,
        setShowInviteModal,
        inviteForm,
        handleRemoveMember,
        handleCancelInvitation
    } = useTeamSettings();

    return (
        <div className="space-y-8">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                            <Users className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white tracking-tight">Team</h1>
                            <p className="text-zinc-400">Manage your team members and permissions</p>
                        </div>
                    </div>
                    <Button
                        onClick={() => setShowInviteModal(true)}
                        className="gap-2 bg-purple-600 hover:bg-purple-500"
                    >
                        <UserPlus className="w-4 h-4" />
                        Invite Member
                    </Button>
                </motion.div>

                {/* Team Members */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <TeamMembersList
                        members={members}
                        loading={loading}
                        onRemove={handleRemoveMember}
                        onInviteClick={() => setShowInviteModal(true)}
                    />
                </motion.div>

                {/* Pending Invitations */}
                {invitations.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <PendingInvitationsList
                            invitations={invitations}
                            onCancel={handleCancelInvitation}
                        />
                    </motion.div>
                )}

                {/* Invite Modal */}
                <InviteTeamModal
                    isOpen={showInviteModal}
                    onClose={() => setShowInviteModal(false)}
                    email={inviteForm.email}
                    setEmail={inviteForm.setEmail}
                    role={inviteForm.role}
                    setRole={inviteForm.setRole}
                    inviting={inviteForm.inviting}
                    onSubmit={inviteForm.handleSubmit}
                />
            </div >
        </div >
    );
}
