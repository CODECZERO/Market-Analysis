/**
 * API Client Configuration
 * 
 * Base Axios instance with interceptors for:
 * - JWT Authentication
 * - Cold start retry logic
 * - Token refresh on 401
 */

import axios, { type AxiosError } from "axios";

// Configuration
const RENDER_COLD_START_TIMEOUT = 120000; // 120 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY_BASE = 2000; // 2 seconds

// Storage keys - must match AuthContext.tsx
export const ACCESS_TOKEN_KEY = "brand_tracker_access_token";
export const REFRESH_TOKEN_KEY = "brand_tracker_refresh_token";

// Create base Axios instance
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? "https://premier-johna-codeczero-7c931fc8.koyeb.app",
    timeout: RENDER_COLD_START_TIMEOUT,
});

// ============================================================================
// REQUEST INTERCEPTOR - Add JWT Token
// ============================================================================
api.interceptors.request.use((config) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ============================================================================
// RETRY INTERCEPTOR - Handle Cold Starts
// ============================================================================
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const config = error.config;
        if (!config) return Promise.reject(error);

        const retryCount = (config as { _retryCount?: number })._retryCount ?? 0;

        const shouldRetry =
            retryCount < MAX_RETRIES &&
            (error.code === "ECONNABORTED" ||
                error.code === "ERR_NETWORK" ||
                error.response?.status === 502 ||
                error.response?.status === 503 ||
                error.response?.status === 504);

        if (shouldRetry) {
            (config as { _retryCount?: number })._retryCount = retryCount + 1;
            const delay = RETRY_DELAY_BASE * Math.pow(2, retryCount);
            console.log(`[API] Service warming up, retry ${retryCount + 1}/${MAX_RETRIES} in ${delay}ms...`);
            await new Promise((resolve) => setTimeout(resolve, delay));
            return api.request(config);
        }

        return Promise.reject(error);
    }
);

// ============================================================================
// TOKEN REFRESH INTERCEPTOR - Handle 401
// ============================================================================
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token!);
        }
    });
    failedQueue = [];
};

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config;
        if (!originalRequest) return Promise.reject(error);

        if (error.response?.status === 401 && !(originalRequest as any)._retry) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    })
                    .catch((err) => Promise.reject(err));
            }

            (originalRequest as any)._retry = true;
            isRefreshing = true;

            try {
                const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
                if (!refreshToken) throw new Error("No refresh token");

                const baseURL = api.defaults.baseURL || "";
                const apiPrefix = baseURL.endsWith("/api") ? "" : "/api";
                const response = await axios.post(`${baseURL}${apiPrefix}/auth/refresh`, {
                    refreshToken,
                });

                const { accessToken, refreshToken: newRefreshToken } = response.data.data;

                localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
                localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);

                originalRequest.headers.Authorization = `Bearer ${accessToken}`;
                processQueue(null, accessToken);

                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                window.dispatchEvent(new CustomEvent("auth:logout"));
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
export function isWaitingResponse(value: unknown): value is { status: "waiting"; message: string } {
    return Boolean(value && typeof value === "object" && (value as { status?: string }).status === "waiting");
}
