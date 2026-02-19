// Frontend Configuration
// API endpoint for backend connection

export const API_CONFIG = {
    // FastAPI Server
    BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',

    ENDPOINTS: {
        HEALTH: '/api/health',
        ANALYZE: '/api/stocks/analyze',
        RESULT: '/api/stocks/analyze',
        PROGRESS: '/api/stocks/analyze',
        WATCHLIST: '/api/stocks/watchlist',
        QUOTE: '/api/stocks/quote',
    },

    // Request timeouts
    TIMEOUT: 30000, // 30 seconds

    // Polling intervals
    POLL_INTERVAL: 2000, // 2 seconds for progress
};

// Usage:
// import { API_CONFIG } from './config';
// const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`);
