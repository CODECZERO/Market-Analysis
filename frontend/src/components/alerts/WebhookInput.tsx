/**
 * Webhook Input Component
 * 
 * Input field for webhook URLs with test button
 */

import { Hash, MessageSquare, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WebhookInputProps {
    channel: "slack" | "discord";
    webhookUrl: string;
    onWebhookChange: (value: string) => void;
    onTest: () => void;
    testing: boolean;
}

const CHANNEL_CONFIG = {
    slack: {
        icon: Hash,
        name: "Slack",
        placeholder: "https://hooks.slack.com/services/...",
        helpUrl: "https://api.slack.com/messaging/webhooks",
        bgColor: "bg-[#4A154B]",
    },
    discord: {
        icon: MessageSquare,
        name: "Discord",
        placeholder: "https://discord.com/api/webhooks/...",
        helpUrl: "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks",
        bgColor: "bg-[#5865F2]",
    },
};

export function WebhookInput({
    channel,
    webhookUrl,
    onWebhookChange,
    onTest,
    testing,
}: WebhookInputProps) {
    const config = CHANNEL_CONFIG[channel];
    const Icon = config.icon;

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl ${config.bgColor} flex items-center justify-center`}>
                        <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <p className="font-medium text-white">{config.name}</p>
                        <p className="text-xs text-zinc-500">Receive alerts in your {config.name} channel</p>
                    </div>
                </div>
                <a
                    href={config.helpUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                    Get webhook <ExternalLink className="w-3 h-3" />
                </a>
            </div>
            <div className="flex gap-3">
                <input
                    type="url"
                    placeholder={config.placeholder}
                    value={webhookUrl}
                    onChange={(e) => onWebhookChange(e.target.value)}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-zinc-800/50 border border-zinc-700/50 text-white placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 transition-colors text-sm"
                />
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onTest}
                    disabled={testing || !webhookUrl}
                    className="border-zinc-700 hover:bg-zinc-800"
                >
                    {testing ? "Testing..." : "Test"}
                </Button>
            </div>
        </div>
    );
}
