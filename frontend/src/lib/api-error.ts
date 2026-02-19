/**
 * API Error Handler Utilities
 * 
 * Standardized error handling for API calls with retry logic and toast notifications.
 */

export interface ApiError {
    status: number;
    message: string;
    code?: string;
    details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: ApiError;
}

/**
 * Parse error response from API
 */
export function parseApiError(error: unknown): ApiError {
    if (error instanceof Response) {
        return {
            status: error.status,
            message: error.statusText || 'Request failed',
            code: `HTTP_${error.status}`
        };
    }

    if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
            return {
                status: 0,
                message: 'Unable to connect to server. Please check your internet connection.',
                code: 'NETWORK_ERROR'
            };
        }
        return {
            status: 500,
            message: error.message,
            code: 'UNKNOWN_ERROR'
        };
    }

    return {
        status: 500,
        message: 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR'
    };
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: ApiError): string {
    switch (error.status) {
        case 400:
            return 'Invalid request. Please check your input.';
        case 401:
            return 'Session expired. Please log in again.';
        case 403:
            return 'You do not have permission to perform this action.';
        case 404:
            return 'The requested resource was not found.';
        case 429:
            return 'Too many requests. Please wait a moment and try again.';
        case 500:
        case 502:
        case 503:
            return 'Server error. Our team has been notified.';
        case 0:
            return 'Network error. Please check your connection.';
        default:
            return error.message || 'Something went wrong.';
    }
}

/**
 * Show toast notification for error
 */
export function showErrorToast(error: ApiError): void {
    const message = getErrorMessage(error);

    // Use browser native notification or console for now
    // Can be replaced with a toast library like react-hot-toast or sonner
    console.error(`[API Error] ${error.code}: ${message}`);

    // Show alert for critical errors
    if (error.status === 401) {
        // Redirect to login
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
    }
}

/**
 * Retry wrapper for API calls
 */
export async function withRetry<T>(
    fn: () => Promise<T>,
    options: { maxRetries?: number; delay?: number; retryOn?: number[] } = {}
): Promise<T> {
    const { maxRetries = 3, delay = 1000, retryOn = [408, 429, 500, 502, 503, 504] } = options;

    let lastError: unknown;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            const apiError = parseApiError(error);

            // Don't retry on certain errors
            if (!retryOn.includes(apiError.status) && apiError.status !== 0) {
                throw error;
            }

            // Don't retry on last attempt
            if (attempt === maxRetries - 1) {
                throw error;
            }

            // Exponential backoff
            const waitTime = delay * Math.pow(2, attempt);
            console.log(`[API] Retry ${attempt + 1}/${maxRetries} after ${waitTime}ms`);
            await new Promise(resolve => setTimeout(resolve, waitTime));
        }
    }

    throw lastError;
}

/**
 * Enhanced fetch wrapper with error handling
 */
export async function apiFetch<T>(
    url: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
    const token = localStorage.getItem('access_token');

    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers
    };

    try {
        const response = await fetch(url, { ...options, headers });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            const error: ApiError = {
                status: response.status,
                message: errorBody.message || response.statusText,
                code: errorBody.code,
                details: errorBody.details
            };
            showErrorToast(error);
            return { success: false, error };
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        const apiError = parseApiError(error);
        showErrorToast(apiError);
        return { success: false, error: apiError };
    }
}

/**
 * API fetch with automatic retry
 */
export async function apiFetchWithRetry<T>(
    url: string,
    options: RequestInit = {},
    retryOptions?: { maxRetries?: number; delay?: number }
): Promise<ApiResponse<T>> {
    return withRetry(() => apiFetch<T>(url, options), retryOptions);
}
