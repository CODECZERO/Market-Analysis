# Frontend Integration Guide

## 🔌 Connecting Frontend to FastAPI Backend

### Quick Setup

1. **Start Backend:**
```bash
cd market_analysis
./run-all.sh
```

2. **Configure Frontend:**
```bash
cd frontend
cp .env.local .env
# Edit .env if API is not on localhost:8000
```

3. **Install Dependencies:**
```bash
npm install
```

4. **Start Frontend:**
```bash
npm run dev
```

Frontend will be on `http://localhost:5173`

---

## 📡 API Integration Examples

### 1. Health Check

```typescript
import { API_CONFIG } from './config';

async function checkHealth() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/api/health`);
  const data = await response.json();
  
  if (data.status === 'healthy') {
    console.log('✅ Backend is healthy');
  }
}
```

### 2. Analyze Stock

```typescript
async function analyzeStock(symbol: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/api/stocks/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol })
  });
  
  const result = await response.json();
  const analysisId = result.data.analysisId;
  
  // Poll for progress
  return pollProgress(analysisId);
}
```

### 3. Poll for Progress

```typescript
async function pollProgress(analysisId: string) {
  while (true) {
    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/stocks/analyze/${analysisId}/progress`
    );
    const data = await response.json();
    
    if (data.status === 'completed') {
      return data.result;
    } else if (data.status === 'failed') {
      throw new Error(data.error);
    }
    
    // Update progress UI
    console.log(`Progress: ${data.progress}%`);
    
    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, API_CONFIG.POLL_INTERVAL));
  }
}
```

### 4. Get Watchlist

```typescript
async function getWatchlist() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/api/stocks/watchlist`);
  const data = await response.json();
  
  return data.watchlist;
}
```

---

## 🎨 Example: Update StockDashboard Component

```typescript
// frontend/src/components/StockDashboard.tsx

import { useState, useEffect } from 'react';
import { API_CONFIG } from '../config';

export function StockDashboard() {
  const [watchlist, setWatchlist] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  
  // Load watchlist on mount
  useEffect(() => {
    loadWatchlist();
  }, []);
  
  async function loadWatchlist() {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/stocks/watchlist`);
      const data = await response.json();
      setWatchlist(data.watchlist);
    } catch (error) {
      console.error('Failed to load watchlist:', error);
    }
  }
  
  async function handleAnalyze(symbol: string) {
    setAnalyzing(true);
    
    try {
      // Trigger analysis
      const analyzeResponse = await fetch(`${API_CONFIG.BASE_URL}/api/stocks/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
      });
      
      const { data } = await analyzeResponse.json();
      const analysisId = data.analysisId;
      
      // Poll for result
      let result;
      while (true) {
        const progressResponse = await fetch(
          `${API_CONFIG.BASE_URL}/api/stocks/analyze/${analysisId}/progress`
        );
        const progressData = await progressResponse.json();
        
        if (progressData.status === 'completed') {
          result = progressData.result;
          break;
        } else if (progressData.status === 'failed') {
          throw new Error(progressData.error);
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      
      // Update UI with result
      console.log('Analysis complete:', result);
      // TODO: Update state and display result
      
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  }
  
  return (
    <div>
      <h1>Stock Dashboard</h1>
      {/* Render watchlist and analysis results */}
    </div>
  );
}
```

---

## 🔧 Environment Variables

**Frontend (.env or .env.local):**
```bash
VITE_API_URL=http://localhost:8000
```

**Backend (.env):**
```bash
# Existing configs...

# Optional: LLM API Keys
GROQ_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Optional: News/Social Scrapers
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

---

## 📋 Complete Integration Checklist

- [x] Backend running (`./run-all.sh`)
- [x] FastAPI server on port 8000
- [x] Frontend `.env` configured
- [ ] Update StockDashboard to use real API
- [ ] Update AddStockModal to call `/api/stocks/watchlist`
- [ ] Add error handling for failed requests
- [ ] Add loading states during analysis
- [ ] Display progress during long operations
- [ ] Handle authentication (if added later)

---

## 🎯 Next Steps

1. **Update existing components** to use `API_CONFIG`
2. **Replace mock data** with real API calls
3. **Add error boundaries** for better UX
4. **Implement retry logic** for failed requests
5. **Add toast notifications** for success/error states

---

## 📚 API Endpoints Reference

See `FASTAPI_GUIDE.md` for complete API documentation.

**Quick Reference:**
- `GET /api/health` - Check system status
- `POST /api/stocks/analyze` - Trigger analysis
- `GET /api/stocks/analyze/{id}/progress` - Get progress
- `GET /api/stocks/analyze/{id}` - Get result
- `GET /api/stocks/watchlist` - Get watchlist
- `POST /api/stocks/watchlist` - Add to watchlist
- `DELETE /api/stocks/watchlist/{symbol}` - Remove from watchlist
- `GET /api/stocks/quote/{symbol}` - Get current quote

---

**You're all set! The backend is ready for frontend integration.** 🚀
