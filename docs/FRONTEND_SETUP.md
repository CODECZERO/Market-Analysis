# Frontend Setup Guide

## Components Created

### 1. StockDashboard.tsx
Main dashboard component featuring:
- Stock watchlist panel with search
- Analysis display panel
- Add/remove stock functionality
- Responsive layout (mobile-friendly)

### 2. StockCard.tsx
Individual stock card in watchlist:
- Stock symbol and exchange
- Analysis status indicator
- Action buttons (analyze, remove)
- Visual selection state

### 3. AnalysisPanel.tsx
Comprehensive analysis display with 4 tabs:
- **Overview**: Investment thesis, entry strategy, targets
- **Technical**: RSI, MACD, ADX, SMA indicators
- **AI Analysis**: 3-phase LLM reasoning
- **ML Predictions**: LSTM forecasts, XGBoost signals

### 4. AddStockModal.tsx
Modal for adding stocks:
- NSE/BSE exchange selector
- Stock search with autocomplete
- Manual symbol entry fallback

## Installation

```bash
cd frontend
npm install
```

## Required Dependencies

Add to `package.json`:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.300.0",
    "recharts": "^2.10.0",
    "tailwindcss": "^3.4.0"
  }
}
```

## Tailwind Configuration

Update `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
          600: '#475569',
          500: '#64748b',
          400: '#94a3b8',
          300: '#cbd5e1',
        }
      }
    },
  },
  plugins: [],
}
```

## Usage

### 1. Import in App.tsx

```typescript
import StockDashboard from './components/StockDashboard';

function App() {
  return <StockDashboard />;
}

export default App;
```

### 2. Environment Variables

Create `.env`:

```bash
REACT_APP_API_URL=http://localhost:3000/api
```

### 3. API Integration

Components expect these endpoints:
- `GET /api/stocks/watchlist`
- `POST /api/stocks/watchlist`
- `DELETE /api/stocks/watchlist/:symbol`
- `POST /api/stocks/analyze`
- `GET /api/stocks/analyze/:id`
- `GET /api/stocks/search`

## Features

### Visual Design
- **Gradient backgrounds** (slate-900 → purple-900)
- **Glassmorphism effects** (backdrop-blur-lg)
- **Smooth transitions** on all interactive elements
- **Status indicators** with color coding
- **Responsive grid layouts**

### User Experience
- Real-time search
- Loading states
- Error handling
- Empty state messages
- Keyboard navigation support

### Data Display
- Price formatting (₹ symbol for INR)
- Percentage calculations
- Color-coded recommendations (green=buy, red=sell, amber=hold)
- Progress indicators for analysis
- Tabbed content organization

## Screenshots

### Dashboard View
```
┌─────────────────────────────────────────────────────┐
│  Stock Analysis Dashboard                    [+Add] │
├───────────────┬─────────────────────────────────────┤
│ Watchlist     │  Analysis Panel                     │
│               │                                     │
│ [Search...]   │  RELIANCE NSE         [BUY]        │
│               │  ₹2,456.75                          │
│ ○ RELIANCE    │                                     │
│ ○ TCS         │  [Overview][Technical][AI][ML]     │
│ ○ HDFCBANK    │                                     │
│               │  Investment Thesis...               │
└───────────────┴─────────────────────────────────────┘
```

## Customization

### Colors
Modify gradient in `StockDashboard.tsx`:
```tsx
className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"
```

### Tab Names
Update tabs in `AnalysisPanel.tsx`:
```tsx
const tabs = [
  { id: 'overview', label: 'Overview', icon: Info },
  // Add more tabs...
];
```

### Card Layout
Adjust grid columns in `StockDashboard.tsx`:
```tsx
className="grid grid-cols-1 lg:grid-cols-3 gap-6"
```

## Next Steps

1. Add chart components using Recharts
2. Implement WebSocket for real-time updates
3. Add export functionality (PDF reports)
4. Create mobile-optimized layouts
5. Add dark/light theme toggle

---

**Built with React + TypeScript + TailwindCSS**
