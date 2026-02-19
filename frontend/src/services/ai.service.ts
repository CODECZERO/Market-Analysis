import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

/**
 * Direct LLM API Service
 * Fast AI responses without going through Worker pipeline
 */

interface ChatMessage {
    role: "system" | "user" | "assistant";
    content: string;
}

interface ChatResponse {
    text: string;
    model: string;
    provider: string;
    latencyMs: number;
}

interface PitchResponse {
    pitch: string;
    latencyMs: number;
}

interface SentimentResponse {
    sentiment: "positive" | "neutral" | "negative";
    score: number;
    summary: string;
    latencyMs: number;
}

interface AIStatusResponse {
    status: "active" | "inactive";
    provider: string | null;
    model: string;
}

/**
 * Get AI provider status
 */
export function useAIStatus() {
    return useQuery<AIStatusResponse>({
        queryKey: ["ai", "status"],
        queryFn: async () => {
            const { data } = await api.get("/api/v1/ai/status");
            return data;
        },
        staleTime: 60_000, // 1 minute
    });
}

/**
 * Send a chat completion request
 */
export function useAIChat() {
    return useMutation<ChatResponse, Error, { messages: ChatMessage[]; temperature?: number }>({
        mutationFn: async ({ messages, temperature = 0.7 }) => {
            const { data } = await api.post("/api/v1/ai/chat", { messages, temperature });
            return data.data;
        },
    });
}

/**
 * Generate a sales pitch for a lead
 */
export function useGeneratePitch() {
    return useMutation<PitchResponse, Error, { brand: string; leadText: string; painPoint?: string }>({
        mutationFn: async ({ brand, leadText, painPoint = "" }) => {
            const { data } = await api.post("/api/v1/ai/pitch", { brand, leadText, painPoint });
            return data.data;
        },
    });
}

/**
 * Quick sentiment analysis
 */
export function useQuickSentiment() {
    return useMutation<SentimentResponse, Error, { text: string }>({
        mutationFn: async ({ text }) => {
            const { data } = await api.post("/api/v1/ai/sentiment", { text });
            return data.data;
        },
    });
}

/**
 * Direct API calls (for non-hook usage)
 */
export const aiService = {
    async getStatus(): Promise<AIStatusResponse> {
        const { data } = await api.get("/api/v1/ai/status");
        return data;
    },

    async chat(messages: ChatMessage[], temperature = 0.7): Promise<ChatResponse> {
        const { data } = await api.post("/api/v1/ai/chat", { messages, temperature });
        return data.data;
    },

    async generatePitch(brand: string, leadText: string, painPoint = ""): Promise<string> {
        const { data } = await api.post("/api/v1/ai/pitch", { brand, leadText, painPoint });
        return data.data.pitch;
    },

    async analyzeSentiment(text: string): Promise<SentimentResponse> {
        const { data } = await api.post("/api/v1/ai/sentiment", { text });
        return data.data;
    },
};
