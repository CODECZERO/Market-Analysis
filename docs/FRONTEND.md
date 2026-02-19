# Frontend Service Documentation

## Overview

The frontend is a **React 18** single-page application built with **Vite** for fast development and optimized production builds.

| Property | Value |
|----------|-------|
| Port | 5173 (dev), 80 (Docker) |
| Build Tool | Vite 5.0 |
| Package Name | `pitch-pulse-monitor` |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React 18.3 |
| Build | Vite 5.0 |
| Styling | Tailwind CSS 3.4, tailwind-merge |
| Components | Radix UI (scroll-area, slot, switch, tabs) |
| Data Fetching | TanStack React Query 5.36 |
| Routing | React Router DOM 6.22 |
| Charts | Recharts 2.9 |
| Animations | Framer Motion 11.0 |
| Icons | Lucide React |
| SEO | react-helmet-async |

---

## Directory Structure

```
frontend/src/
├── App.tsx              # Main router configuration
├── main.tsx             # Entry point
├── index.css            # Global styles
├── components/          # 144 reusable components
│   ├── admin/           # Admin dashboard components
│   ├── alerts/          # Alert management
│   ├── analytics/       # Charts and analytics
│   ├── brands/          # Brand management
│   ├── competitors/     # Competition analysis
│   ├── crisis/          # Crisis thermometer
│   ├── dashboard/       # Main dashboard sections
│   ├── landing/         # Landing page sections
│   ├── leads/           # Money Mode components
│   ├── live/            # Live mentions feed
│   ├── market/          # Market gap analysis
│   ├── reports/         # Report generation
│   ├── shared/          # Shared components
│   ├── team/            # Team management
│   └── ui/              # Base UI primitives
├── contexts/            # React contexts (Auth)
├── hooks/               # Custom hooks (15 categories)
├── layouts/             # AppLayout, BrandLayout
├── lib/                 # Utilities
├── pages/               # 24 page components
├── services/            # API service layer
└── types/               # TypeScript types
```

---

## Pages (Routes)

### Public Routes
| Route | Page | Description |
|-------|------|-------------|
| `/` | LandingPage | Marketing landing |
| `/login` | LoginPage | User authentication |
| `/signup` | SignupPage | User registration |
| `/verify-email` | VerifyEmailPage | Email verification |
| `/terms` | TermsPage | Terms of service |
| `/privacy` | PrivacyPage | Privacy policy |
| `/brand/:slug` | BrandSEOPage | Programmatic SEO pages |

### Protected Routes (App Layout)
| Route | Page | Description |
|-------|------|-------------|
| `/brands` | BrandListPage | List user's brands |
| `/brands/create` | CreateBrandPage | Create new brand |
| `/brands/:id/dashboard` | BrandDashboardPage | Brand overview |
| `/brands/:id/live` | LiveMentionsPage | Real-time mentions |
| `/brands/:id/analytics` | AnalyticsPage | Sentiment charts |
| `/brands/:id/competitors` | CompetitorsPage | Competition tracking |
| `/brands/:id/reports` | ReportsPage | Generate reports |
| `/brands/:id/web-insights` | WebInsightsPage | Web scraping insights |

### V4.0 Advanced Features
| Route | Page | Description |
|-------|------|-------------|
| `/money-mode` | MoneyModePage | Sales lead detection |
| `/crisis` | CrisisThermometerPage | Real-time crisis monitoring |
| `/market-gap` | MarketGapPage | Competitor weakness analysis |
| `/admin` | AdminDashboardPage | System administration |
| `/settings` | AlertSettingsPage | Alert configuration |
| `/team` | TeamSettingsPage | Team management |

---

## Hooks Architecture

Custom hooks organized by feature:

| Hook Category | Purpose |
|---------------|---------|
| `useAuth` | Authentication state |
| `useBrands` | Brand CRUD operations |
| `useLeads` | Money Mode leads |
| `useCrisis` | Crisis metrics |
| `useCompetitors` | Competitor data |
| `useDashboard` | Dashboard aggregations |
| `useLive` | Real-time mentions |
| `useReports` | Report generation |
| `useStats` | Statistics |
| `useTeam` | Team management |

---

## Scripts

```bash
npm run dev      # Start dev server (port 5173)
npm run build    # Production build
npm run preview  # Preview production build
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | API Gateway base URL | `/api` |

---

## Build Output

Production build goes to `dist/` and is served by Nginx in Docker.
