/**
 * Session Tracking Utility
 * 
 * Tracks user sessions, logout times, and determines when to load historical data.
 * Uses both localStorage and cookies for cross-tab synchronization.
 */

const SESSION_KEY = 'brand_tracker_session';
const COOKIE_NAME = 'brand_tracker_last_active';
const CURRENT_SESSION_KEY = 'brand_tracker_current_session';
const MAX_HISTORY_DAYS = 30; // Cap historical data to 30 days

export interface SessionInfo {
    sessionId: string;
    lastActiveTime: number;
    logoutTime: number | null;
    isFirstLoad: boolean;
    loginTime: number;
}

/**
 * Generate a unique session ID
 */
function generateSessionId(): string {
    return `${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
}

/**
 * Set a cookie with expiration
 */
function setCookie(name: string, value: string, days: number = 7): void {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

/**
 * Get cookie value by name
 */
function getCookie(name: string): string | null {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

/**
 * Delete a cookie
 */
function deleteCookie(name: string): void {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

/**
 * Initialize or retrieve session information
 */
export function initializeSession(): SessionInfo {
    const now = Date.now();

    // Check if there's an existing session in localStorage
    const storedSession = localStorage.getItem(SESSION_KEY);
    const currentSession = sessionStorage.getItem(CURRENT_SESSION_KEY);

    if (storedSession && !currentSession) {
        // User is returning (new browser session)
        const session: SessionInfo = JSON.parse(storedSession);

        // Mark as first load for this browser session
        session.isFirstLoad = true;

        // Update session
        session.sessionId = generateSessionId();
        session.loginTime = now;
        session.lastActiveTime = now;

        // Save to localStorage and sessionStorage
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        sessionStorage.setItem(CURRENT_SESSION_KEY, 'true');
        setCookie(COOKIE_NAME, now.toString(), 7);

        return session;
    } else if (storedSession && currentSession) {
        // Same browser session, just a refresh
        const session: SessionInfo = JSON.parse(storedSession);
        session.isFirstLoad = false;
        session.lastActiveTime = now;

        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        setCookie(COOKIE_NAME, now.toString(), 7);

        return session;
    } else {
        // Brand new session
        const newSession: SessionInfo = {
            sessionId: generateSessionId(),
            lastActiveTime: now,
            logoutTime: null,
            isFirstLoad: false, // First time ever, no history to load
            loginTime: now,
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(newSession));
        sessionStorage.setItem(CURRENT_SESSION_KEY, 'true');
        setCookie(COOKIE_NAME, now.toString(), 7);

        return newSession;
    }
}

/**
 * Update last active time
 */
export function trackActivity(): void {
    const session = getSessionInfo();
    if (session) {
        const now = Date.now();
        session.lastActiveTime = now;
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        setCookie(COOKIE_NAME, now.toString(), 7);
    }
}

/**
 * Track logout and store the timestamp
 */
export function trackLogout(): void {
    const session = getSessionInfo();
    if (session) {
        const now = Date.now();
        session.logoutTime = now;
        session.lastActiveTime = now;
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        setCookie(COOKIE_NAME, now.toString(), 7);
    }

    // Clear current session flag
    sessionStorage.removeItem(CURRENT_SESSION_KEY);
}

/**
 * Get current session info
 */
export function getSessionInfo(): SessionInfo | null {
    const stored = localStorage.getItem(SESSION_KEY);
    if (stored) {
        try {
            return JSON.parse(stored) as SessionInfo;
        } catch {
            return null;
        }
    }
    return null;
}

/**
 * Calculate time range for historical data fetch
 * Returns null if no historical data should be fetched
 */
export function getTimeRange(): { fromDate: string; toDate: string } | null {
    const session = getSessionInfo();

    if (!session || !session.logoutTime || !session.isFirstLoad) {
        return null;
    }

    const now = Date.now();
    const logoutTime = session.logoutTime;

    // Calculate days since logout
    const daysSinceLogout = (now - logoutTime) / (1000 * 60 * 60 * 24);

    // Cap at MAX_HISTORY_DAYS
    const fromTime = daysSinceLogout > MAX_HISTORY_DAYS
        ? now - (MAX_HISTORY_DAYS * 24 * 60 * 60 * 1000)
        : logoutTime;

    return {
        fromDate: new Date(fromTime).toISOString(),
        toDate: new Date(now).toISOString(),
    };
}

/**
 * Check if this is the first load since logout
 */
export function isFirstLoad(): boolean {
    const session = getSessionInfo();
    return session ? session.isFirstLoad : false;
}

/**
 * Mark that historical data has been loaded
 */
export function markSessionLoaded(): void {
    const session = getSessionInfo();
    if (session) {
        session.isFirstLoad = false;
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    }
}

/**
 * Get formatted time since logout for display
 */
export function getTimeSinceLogout(): string | null {
    const session = getSessionInfo();

    if (!session || !session.logoutTime) {
        return null;
    }

    const now = Date.now();
    const diff = now - session.logoutTime;

    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''}`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''}`;
    } else {
        return 'a moment';
    }
}

/**
 * Clear session data (for debugging or complete logout)
 */
export function clearSession(): void {
    localStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(CURRENT_SESSION_KEY);
    deleteCookie(COOKIE_NAME);
}
