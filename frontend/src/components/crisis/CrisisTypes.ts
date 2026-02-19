/**
 * Crisis Component Types
 */

export interface CrisisMetrics {
    riskScore: number;
    severity: "normal" | "warning" | "critical";
    velocityMultiplier: number;
    sentimentIntensity: number;
    mentionCount: number;
    reasons: string[];
}

export interface AlertEvent {
    id: string;
    monitorId: string;
    riskScore: number;
    severity: "low" | "medium" | "high" | "critical";
    triggeredReasons: string[];
    recommendedAction: string;
    createdAt: string;
    isResolved: boolean;
}

export interface VelocityPoint {
    timestamp: string;
    mentionsPerMinute: number;
    sentiment: number;
}
