# 📱 Frontend Management Dashboard — Next.js 16 PWA (Milestone 3)

> **Predictive Irrigation Intelligence, Field Telemetry & Interactive What-If Simulator PWA**

---

## 🏗️ Architecture Overview

Built using **Next.js 16 (App Router)**, **React 19**, **TypeScript**, and **TailwindCSS**, this Progressive Web Application provides farmers, agronomists, and system operators with a high-performance command center for precision irrigation.

### Key Capabilities
1. **Progressive Web App (PWA)**:
   - Installable on mobile and desktop via `manifest.json`.
   - Offline asset and network resilience via Service Worker (`sw.js`).
2. **Farmer Authentication & Security**:
   - JWT and cookie-based authentication gateway (`/login`).
   - One-click demo login presets and persistent active farmer profile header.
3. **Live AI Command Center (`/`)**:
   - Real-time soil moisture dial gauges and battery life indicators.
   - Synchronized OpenWeather weather widget.
   - Live AI irrigation dispatch recommendation card with confidence gauge.
4. **Client-Side JavaScript Models & What-If Simulator**:
   - Interactive agronomic sliders (moisture, temperature, humidity, rain probability).
   - Real-time client-side calculation of irrigation deficit without network delay.
   - Native Web Speech API voice synthesis in English and Indian accents.
5. **IoT Pump Hardware Actuation**:
   - Automated and manual pump valve actuation with live countdown execution.
   - Over-watering lockout protection and safety delay shields.
6. **Time-Series Sensor & Water Analytics (`/analytics`, `/history`)**:
   - 180-day telemetry trends, diurnal drying curves, and weekly volumetric consumption.
7. **Milestone 3 Outputs & Visual Showcase (`/outputs`)**:
   - Dedicated interactive gallery exhibiting 16 high-resolution system captures.

---

## 📁 Directory Layout

```
frontend/
├── public/
│   ├── manifest.json              # PWA manifest
│   ├── sw.js                      # Offline service worker
│   └── images/milestone3/         # High-resolution screenshots (16 items)
├── src/
│   ├── app/
│   │   ├── page.tsx               # Main AI Command Dashboard
│   │   ├── login/page.tsx         # Farmer Authentication Gateway
│   │   ├── fields/page.tsx        # Multi-parcel telemetry monitoring
│   │   ├── schedule/page.tsx      # AI irrigation schedule & timetable
│   │   ├── analytics/page.tsx     # Time-series telemetry & water analytics
│   │   ├── history/page.tsx       # Historical irrigation logs
│   │   ├── outputs/page.tsx       # Milestone 3 Visual Outputs Showcase Gallery
│   │   └── register/page.tsx      # Farmer, field, crop & sensor registration
│   ├── components/
│   │   ├── AIRecommendationCard.tsx
│   │   ├── FarmerWhatIfSimulator.tsx
│   │   ├── IrrigationLogModal.tsx
│   │   ├── MLModelPerformanceCard.tsx
│   │   └── BottomNav.tsx
│   └── types/index.ts             # TypeScript definitions
└── next.config.js                 # API rewrite proxies for FastAPI microservices
```

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Start development server
npm run dev
```

Application URL: [http://localhost:3000](http://localhost:3000)  
Outputs Gallery URL: [http://localhost:3000/outputs](http://localhost:3000/outputs)

---

## 🧪 Type Checking

```bash
npx tsc --noEmit
```
Exits cleanly with zero errors.
