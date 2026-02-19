/**
 * Pending Invitations List
 */

import { Clock, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Invitation } from "@/hooks/team";

interface PendingInvitationsListProps {
    invitations: Invitation[];
    onCancel: (id: string) => void;
}

export function PendingInvitationsList({ invitations, onCancel }: PendingInvitationsListProps) {
    if (invitations.length === 0) return null;

    return (
        <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
            <CardHeader className="border-b border-zinc-800/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                        <Clock className="h-4 w-4 text-amber-400" />
                    </div>
                    Pending Invitations
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0 divide-y divide-zinc-800/50">
                {invitations.map((invite) => (
                    <div key={invite.id} className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center">
                                <Mail className="w-5 h-5 text-zinc-500" />
                            </div>
                            <div>
                                <p className="font-medium text-white">{invite.email}</p>
                                <p className="text-xs text-zinc-500">
                                    Invited as {invite.role} • Expires {new Date(invite.expiresAt).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onCancel(invite.id)}
                            className="text-zinc-400 hover:text-red-400"
                        >
                            Cancel
                        </Button>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
}
