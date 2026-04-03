# QuantPulse Frontend

React-based frontend for QuantPulse India stock analytics platform.

## Features

- Interactive stock dashboard
- Real-time price charts with technical indicators
- Market movers (top gainers/losers)
- AI-powered stock analysis
- News sentiment visualization
- Market regime indicators
- Responsive design for all devices

## Tech Stack

- React 18 with TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- Recharts for data visualization
- React Router for navigation
- Axios for API calls

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Run development server
npm run dev
```

Development server runs at: http://localhost:5173

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── app/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── StockDashboard.tsx
│   │   ├── StockChart.tsx
│   │   ├── MarketMovers.tsx
│   │   └── AIPredictionCard.tsx
│   ├── pages/              # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── services/           # API client
│   │   └── api.ts
│   └── App.tsx             # Main app component
├── main.tsx                # Entry point
└── index.css               # Global styles
```

## Configuration

Environment variables in `.env`:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# For production
# VITE_API_BASE_URL=https://your-backend.onrender.com
```

All environment variables must be prefixed with `VITE_`.

## Key Components

### StockDashboard
Main dashboard component with stock search and analysis display.

### StockChart
Interactive price chart with technical indicators (SMA, EMA, Bollinger Bands).

### MarketMovers
Displays top gainers and losers in the market.

### AIPredictionCard
Shows AI-generated investment insights from multi-agent system.

### MarketContextStrip
Displays current market regime and Nifty 50 status.

## Development

```bash
# Run development server with hot reload
npm run dev

# Type checking
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variable: `VITE_API_BASE_URL=https://your-backend-url.com`
3. Deploy automatically on push to main branch

### Manual Build

```bash
npm run build
# Upload dist/ folder to your hosting provider
```

## API Integration

The frontend communicates with the backend via REST API. All API calls are centralized in `src/app/services/api.ts`.

Key features:
- Automatic request timeouts
- Error handling with user-friendly messages
- Retry mechanisms for failed requests
- Loading states for better UX

## Styling

Uses Tailwind CSS with custom configuration:
- Custom color palette for financial data
- Responsive breakpoints
- Dark mode support (planned)
- Accessible components

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - see [../LICENSE](../LICENSE) for details.
