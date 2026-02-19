/**
 * Alert Settings Page
 * 
 * Configures notification channels and alert preferences.
 */

import { motion } from "framer-motion";
import {
    Bell, Mail, MessageSquare, Hash, Save,
    CheckCircle2, AlertCircle, ExternalLink,
    Zap, Shield, TrendingDown, Activity, Calendar
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTypeToggle } from "@/components/alerts/AlertTypeToggle";
import { useAlertSettings } from "@/hooks/alerts";

// Animation variants
const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.1, delayChildren: 0.1 }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
};

export default function AlertSettingsPage() {
    const {
        settings,
        setSettings,
        isSaving,
        saveStatus,
        testingChannel,
        handleSave,
        testWebhook
    } = useAlertSettings();

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Background Orbs */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    animate={{ x: [0, 30, 0], y: [0, -20, 0] }}
                    transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute -top-20 right-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[100px]"
                />
                <motion.div
                    animate={{ x: [0, -20, 0], y: [0, 30, 0] }}
                    transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute bottom-20 -left-20 w-[300px] h-[300px] bg-purple-500/10 rounded-full blur-[80px]"
                />
            </div>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="relative z-10 space-y-8 p-6 max-w-4xl mx-auto"
            >
                {/* Header */}
                <motion.div variants={itemVariants} className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                        <Bell className="w-7 h-7 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">
                            Alert Settings
                        </h1>
                        <p className="text-zinc-400 mt-0.5">
                            Configure how you receive brand monitoring alerts
                        </p>
                    </div>
                </motion.div>

                {/* Notification Channels */}
                <motion.div variants={itemVariants}>
                    <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
                        <CardHeader className="border-b border-zinc-800/50">
                            <CardTitle className="text-lg font-semibold flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                                    <MessageSquare className="h-4 w-4 text-blue-400" />
                                </div>
                                Notification Channels
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6 space-y-6">
                            {/* Slack */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-[#4A154B] flex items-center justify-center">
                                            <Hash className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-white">Slack</p>
                                            <p className="text-xs text-zinc-500">Receive alerts in your Slack channel</p>
                                        </div>
                                    </div>
                                    <a
                                        href="https://api.slack.com/messaging/webhooks"
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
                                        placeholder="https://hooks.slack.com/services/..."
                                        value={settings.slackWebhook}
                                        onChange={(e) => setSettings(s => ({ ...s, slackWebhook: e.target.value }))}
                                        className="flex-1 px-4 py-2.5 rounded-xl bg-zinc-800/50 border border-zinc-700/50 text-white placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 transition-colors text-sm"
                                    />
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => testWebhook("slack")}
                                        disabled={testingChannel === "slack" || !settings.slackWebhook}
                                        className="border-zinc-700 hover:bg-zinc-800"
                                    >
                                        {testingChannel === "slack" ? "Testing..." : "Test"}
                                    </Button>
                                </div>
                            </div>

                            {/* Discord */}
                            <div className="space-y-3 pt-4 border-t border-zinc-800/50">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center">
                                            <MessageSquare className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-white">Discord</p>
                                            <p className="text-xs text-zinc-500">Receive alerts in your Discord server</p>
                                        </div>
                                    </div>
                                    <a
                                        href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
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
                                        placeholder="https://discord.com/api/webhooks/..."
                                        value={settings.discordWebhook}
                                        onChange={(e) => setSettings(s => ({ ...s, discordWebhook: e.target.value }))}
                                        className="flex-1 px-4 py-2.5 rounded-xl bg-zinc-800/50 border border-zinc-700/50 text-white placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 transition-colors text-sm"
                                    />
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => testWebhook("discord")}
                                        disabled={testingChannel === "discord" || !settings.discordWebhook}
                                        className="border-zinc-700 hover:bg-zinc-800"
                                    >
                                        {testingChannel === "discord" ? "Testing..." : "Test"}
                                    </Button>
                                </div>
                            </div>

                            {/* Email */}
                            <div className="space-y-3 pt-4 border-t border-zinc-800/50">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
                                            <Mail className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-white">Email</p>
                                            <p className="text-xs text-zinc-500">Receive alert summaries via email</p>
                                        </div>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={settings.emailEnabled}
                                            onChange={(e) => setSettings(s => ({ ...s, emailEnabled: e.target.checked }))}
                                            className="sr-only peer"
                                        />
                                        <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600" />
                                    </label>
                                </div>
                                {settings.emailEnabled && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        className="overflow-hidden"
                                    >
                                        <input
                                            type="email"
                                            placeholder="your@email.com"
                                            value={settings.emailAddress}
                                            onChange={(e) => setSettings(s => ({ ...s, emailAddress: e.target.value }))}
                                            className="w-full px-4 py-2.5 rounded-xl bg-zinc-800/50 border border-zinc-700/50 text-white placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 transition-colors text-sm"
                                        />
                                    </motion.div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Alert Types */}
                <motion.div variants={itemVariants}>
                    <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
                        <CardHeader className="border-b border-zinc-800/50">
                            <CardTitle className="text-lg font-semibold flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                                    <Zap className="h-4 w-4 text-amber-400" />
                                </div>
                                Alert Types
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6">
                            <div className="grid gap-4 sm:grid-cols-2">
                                <AlertTypeToggle
                                    icon={<Shield className="w-4 h-4" />}
                                    title="Crisis Alerts"
                                    description="High urgency negative mentions"
                                    color="red"
                                    enabled={settings.alertTypes.crisis}
                                    onChange={(v) => setSettings(s => ({ ...s, alertTypes: { ...s.alertTypes, crisis: v } }))}
                                />
                                <AlertTypeToggle
                                    icon={<TrendingDown className="w-4 h-4" />}
                                    title="Sentiment Drops"
                                    description="Sudden drop in sentiment score"
                                    color="amber"
                                    enabled={settings.alertTypes.sentimentDrop}
                                    onChange={(v) => setSettings(s => ({ ...s, alertTypes: { ...s.alertTypes, sentimentDrop: v } }))}
                                />
                                <AlertTypeToggle
                                    icon={<Activity className="w-4 h-4" />}
                                    title="Mention Spikes"
                                    description="Unusual increase in mentions"
                                    color="blue"
                                    enabled={settings.alertTypes.spike}
                                    onChange={(v) => setSettings(s => ({ ...s, alertTypes: { ...s.alertTypes, spike: v } }))}
                                />
                                <AlertTypeToggle
                                    icon={<Hash className="w-4 h-4" />}
                                    title="Keyword Alerts"
                                    description="Specific keyword detected"
                                    color="purple"
                                    enabled={settings.alertTypes.keyword}
                                    onChange={(v) => setSettings(s => ({ ...s, alertTypes: { ...s.alertTypes, keyword: v } }))}
                                />
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Weekly Digest */}
                <motion.div variants={itemVariants}>
                    <Card className="border-zinc-800/50 bg-zinc-900/30 backdrop-blur-xl">
                        <CardHeader className="border-b border-zinc-800/50">
                            <CardTitle className="text-lg font-semibold flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                                    <Calendar className="h-4 w-4 text-emerald-400" />
                                </div>
                                Weekly Email Digest
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6 space-y-4">
                            <p className="text-sm text-zinc-400">
                                Receive a comprehensive summary of your brand's performance every week.
                            </p>
                            <div className="flex items-center justify-between p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                                        <Mail className="w-5 h-5 text-emerald-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-white">Enable Weekly Digest</p>
                                        <p className="text-xs text-zinc-500">Sent to your registered email address</p>
                                    </div>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={settings.weeklyDigest}
                                        onChange={(e) => setSettings(s => ({ ...s, weeklyDigest: e.target.checked }))}
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500" />
                                </label>
                            </div>
                            {settings.weeklyDigest && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    className="overflow-hidden space-y-3"
                                >
                                    <label className="block text-sm font-medium text-zinc-400">Send on</label>
                                    <select
                                        value={settings.digestDay}
                                        onChange={(e) => setSettings(s => ({ ...s, digestDay: e.target.value as any }))}
                                        className="w-full px-4 py-2.5 rounded-xl bg-zinc-800/50 border border-zinc-700/50 text-white focus:outline-none focus:border-emerald-500/50 transition-colors text-sm"
                                    >
                                        <option value="monday">Monday 9:00 AM</option>
                                        <option value="tuesday">Tuesday 9:00 AM</option>
                                        <option value="wednesday">Wednesday 9:00 AM</option>
                                        <option value="thursday">Thursday 9:00 AM</option>
                                        <option value="friday">Friday 9:00 AM</option>
                                    </select>
                                    <p className="text-xs text-zinc-500">
                                        Includes: Sentiment trends, top mentions, competitor updates, and actionable insights.
                                    </p>
                                </motion.div>
                            )}
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Save Button */}
                <motion.div variants={itemVariants} className="flex justify-end">
                    <Button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 gap-2 px-8 h-11 shadow-lg shadow-blue-500/20"
                    >
                        {isSaving ? (
                            "Saving..."
                        ) : saveStatus === "success" ? (
                            <>
                                <CheckCircle2 className="w-4 h-4" />
                                Saved!
                            </>
                        ) : saveStatus === "error" ? (
                            <>
                                <AlertCircle className="w-4 h-4" />
                                Failed
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4" />
                                Save Settings
                            </>
                        )}
                    </Button>
                </motion.div>
            </motion.div>
        </div>
    );
}
