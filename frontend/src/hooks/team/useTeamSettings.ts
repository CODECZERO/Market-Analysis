/**
 * Team Settings Hook
 */

import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/lib/api";

export interface TeamMember {
    id: string;
    email: string;
    name: string;
    role: 'admin' | 'member' | 'viewer';
    status: 'active' | 'pending' | 'invited';
    avatarUrl?: string;
    joinedAt?: string;
    lastActive?: string;
}

export interface Invitation {
    id: string;
    email: string;
    role: 'member' | 'viewer';
    sentAt: string;
    expiresAt: string;
}

export function useTeamSettings() {
    const { brandId } = useParams();
    const [members, setMembers] = useState<TeamMember[]>([]);
    const [invitations, setInvitations] = useState<Invitation[]>([]);
    const [loading, setLoading] = useState(true);
    const [showInviteModal, setShowInviteModal] = useState(false);

    // Invite form
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState<'member' | 'viewer'>('member');
    const [inviting, setInviting] = useState(false);

    useEffect(() => {
        if (brandId) fetchTeamData();
    }, [brandId]);

    const fetchTeamData = async () => {
        try {
            const res = await api.get(`/api/brands/${brandId}/team`);
            setMembers(res.data.members || []);
            setInvitations(res.data.invitations || []);
        } catch (error) {
            console.error('Failed to fetch team data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inviteEmail.trim()) return;
        setInviting(true);

        try {
            await api.post(`/api/brands/${brandId}/team/invite`, {
                email: inviteEmail,
                role: inviteRole
            });

            setShowInviteModal(false);
            setInviteEmail('');
            fetchTeamData();
        } catch (error) {
            console.error('Failed to send invitation:', error);
        } finally {
            setInviting(false);
        }
    };

    const handleRemoveMember = async (memberId: string) => {
        if (!confirm('Are you sure you want to remove this team member?')) return;

        try {
            await api.delete(`/api/brands/${brandId}/team/members/${memberId}`);
            setMembers(prev => prev.filter(m => m.id !== memberId));
        } catch (error) {
            console.error('Failed to remove member:', error);
        }
    };

    const handleCancelInvitation = async (inviteId: string) => {
        try {
            await api.delete(`/api/brands/${brandId}/team/invitations/${inviteId}`);
            setInvitations(prev => prev.filter(i => i.id !== inviteId));
        } catch (error) {
            console.error('Failed to cancel invitation:', error);
        }
    };

    return {
        brandId,
        members,
        invitations,
        loading,
        showInviteModal,
        setShowInviteModal,
        inviteForm: {
            email: inviteEmail,
            setEmail: setInviteEmail,
            role: inviteRole,
            setRole: setInviteRole,
            inviting,
            handleSubmit: handleInvite
        },
        handleRemoveMember,
        handleCancelInvitation
    };
}
