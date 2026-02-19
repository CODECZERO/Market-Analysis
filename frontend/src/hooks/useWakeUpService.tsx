/**
 * useWakeUpService - Hook to pre-warm Render free tier services
 * 
 * Render's free tier spins down services after ~50s of inactivity.
 * This hook sends a lightweight health check to wake up services
 * when the app loads, reducing perceived latency for initial requests.
 */

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";

const PING_TIMEOUT = 30000; // 30 seconds for initial wake-up

interface WakeUpState {
  isWaking: boolean;
  isReady: boolean;
  error: string | null;
  retryCount: number;
}

export function useWakeUpService() {
  const [state, setState] = useState<WakeUpState>({
    isWaking: true,
    isReady: false,
    error: null,
    retryCount: 0,
  });

  const wakeUp = useCallback(async () => {
    setState((prev) => ({ ...prev, isWaking: true, error: null }));

    try {
      // Use AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), PING_TIMEOUT);

      const response = await api.get("/health", {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Axios throws on non-200 by default, so if we are here, it's ok
      setState({ isWaking: false, isReady: true, error: null, retryCount: 0 });
      console.log("[WakeUp] Service is ready");
    } catch (err: any) {
      const errorMessage = err.message || "Unknown error";
      console.log("[WakeUp] Wake-up attempt failed:", errorMessage);

      setState((prev) => ({
        isWaking: false,
        isReady: false,
        error: errorMessage.includes("aborted") ? "Service is starting up..." : errorMessage,
        retryCount: prev.retryCount + 1,
      }));
    }
  }, []);

  useEffect(() => {
    // Auto-wake on mount
    wakeUp();

    // Keep service warm with periodic pings every 4 minutes
    // (Render sleeps after ~5 minutes of inactivity)
    const keepAliveInterval = setInterval(() => {
      api.get("/health").catch(() => {
        // Silent fail - just trying to keep service warm
      });
    }, 4 * 60 * 1000);

    return () => clearInterval(keepAliveInterval);
  }, [wakeUp]);

  return {
    ...state,
    retry: wakeUp,
  };
}

/**
 * Cold Start Loading Component
 */
export function ColdStartLoader({
  isWaking,
  error,
  onRetry
}: {
  isWaking: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  if (!isWaking && !error) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0a0a0b]/95 backdrop-blur-sm">
      <div className="text-center max-w-md px-6">
        <div className="mb-6">
          {isWaking ? (
            <div className="w-12 h-12 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
          ) : (
            <div className="w-12 h-12 rounded-full bg-orange-500/10 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          )}
        </div>

        <h2 className="text-xl font-semibold text-white mb-2">
          {isWaking ? "Waking up services..." : "Connection issue"}
        </h2>

        <p className="text-zinc-400 text-sm mb-6">
          {isWaking
            ? "Our servers are waking up from sleep mode. This may take up to 30 seconds on the free tier."
            : error || "Unable to connect to the server. Please try again."
          }
        </p>

        {isWaking && (
          <div className="flex items-center justify-center gap-2 text-xs text-zinc-500">
            <span className="inline-block w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
            <span>Free tier - servers sleep after inactivity</span>
          </div>
        )}

        {!isWaking && error && (
          <button
            onClick={onRetry}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}

export type { WakeUpState };
