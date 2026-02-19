import React, { createContext, useContext, useEffect, useRef, useState, useCallback, type ReactNode } from "react";
import { useAuth } from "./AuthContext";

interface WebSocketContextType {
    isConnected: boolean;
    subscribeToBrand: (brand: string) => void;
    unsubscribeFromBrand: (brand: string) => void;
    lastMessage: any;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// Determine WS URL
const WS_BASE = (import.meta.env.VITE_API_URL || "https://premier-johna-codeczero-7c931fc8.koyeb.app").replace(/^http/, "ws");
const WS_URL = `${WS_BASE}/ws`;

export function WebSocketProvider({ children }: { children: ReactNode }) {
    const { accessToken, isAuthenticated } = useAuth();
    const ws = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<any>(null);

    // Track active subscriptions to resubscribe on reconnect
    const subscriptions = useRef<Set<string>>(new Set());

    const connect = useCallback(() => {
        if (!accessToken || !isAuthenticated) return;
        if (ws.current?.readyState === WebSocket.OPEN) return;

        const url = `${WS_URL}?token=${accessToken}`;
        const socket = new WebSocket(url);

        socket.onopen = () => {
            console.log("[WS] Connected");
            setIsConnected(true);

            // Resubscribe to existing brands
            subscriptions.current.forEach(brand => {
                socket.send(JSON.stringify({ type: "subscribe", brand }));
            });
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("[WS] Message:", data);
                setLastMessage(data);
            } catch (err) {
                console.error("[WS] Parse error:", err);
            }
        };

        socket.onclose = () => {
            console.log("[WS] Disconnected. Reconnecting in 3s...");
            setIsConnected(false);
            ws.current = null;
            setTimeout(connect, 3000); // Simple linear backoff
        };

        socket.onerror = (err) => {
            console.error("[WS] Error:", err);
            socket.close();
        };

        ws.current = socket;
    }, [accessToken, isAuthenticated]);

    useEffect(() => {
        if (isAuthenticated && accessToken) {
            connect();
        }
        return () => {
            ws.current?.close();
        };
    }, [isAuthenticated, accessToken, connect]);

    const subscribeToBrand = useCallback((brand: string) => {
        if (subscriptions.current.has(brand)) return;

        subscriptions.current.add(brand);
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "subscribe", brand }));
        }
    }, [isAuthenticated]); // Only depends on auth state basically

    const unsubscribeFromBrand = useCallback((brand: string) => {
        subscriptions.current.delete(brand);
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "unsubscribe", brand }));
        }
    }, []);

    return (
        <WebSocketContext.Provider value={{ isConnected, subscribeToBrand, unsubscribeFromBrand, lastMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
}

export function useWebSocket() {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error("useWebSocket must be used within a WebSocketProvider");
    }
    return context;
}
