/**
 * Alert Settings Hook
 */

import { useState } from "react";
import { api } from "@/lib/api";

interface AlertSettings {
    slackWebhook: string;
    discordWebhook: string;
    emailEnabled: boolean;
    emailAddress: string;
    weeklyDigest: boolean;
    digestDay: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday';
    alertTypes: {
        crisis: boolean;
        sentimentDrop: boolean;
        spike: boolean;
        keyword: boolean;
    };
}

export function useAlertSettings() {
    const [settings, setSettings] = useState<AlertSettings>({
        slackWebhook: "",
        discordWebhook: "",
        emailEnabled: false,
        emailAddress: "",
        weeklyDigest: false,
        digestDay: 'monday',
        alertTypes: {
            crisis: true,
            sentimentDrop: true,
            spike: true,
            keyword: false,
        }
    });
    const [isSaving, setIsSaving] = useState(false);
    const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");
    const [testingChannel, setTestingChannel] = useState<string | null>(null);

    const handleSave = async () => {
        setIsSaving(true);
        setSaveStatus("idle");
        try {
            await api.post("/api/v1/alerts/settings", settings);
            setSaveStatus("success");
            setTimeout(() => setSaveStatus("idle"), 3000);
        } catch (error) {
            setSaveStatus("error");
        } finally {
            setIsSaving(false);
        }
    };

    const testWebhook = async (channel: "slack" | "discord") => {
        setTestingChannel(channel);
        try {
            const webhookUrl = channel === "slack" ? settings.slackWebhook : settings.discordWebhook;

            if (!webhookUrl) {
                alert(`Please enter a ${channel} webhook URL first`);
                return;
            }

            await api.post("/api/v1/alerts/test", {
                channel,
                webhookUrl
            });

            alert(`Test notification sent to ${channel}!`);
        } catch (error) {
            alert(`Failed to send test notification to ${channel}`);
        } finally {
            setTestingChannel(null);
        }
    };

    return {
        settings,
        setSettings,
        isSaving,
        saveStatus,
        testingChannel,
        handleSave,
        testWebhook
    };
}
