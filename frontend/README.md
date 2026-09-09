# 📱 Frontend Dashboard — Next.js 14 PWA

> **Predictive Irrigation Intelligence & Field Management PWA Dashboard**

---

## 🏗️ Architecture Overview

Built using **Next.js 14 App Router**, **TypeScript**, and **TailwindCSS**, this PWA dashboard provides farmers and agronomists with real-time field telemetry, weather forecasts, and AI-driven irrigation recommendations.

---

## 🌟 Key Components & Views

1. **AI Recommendation Card (`AIRecommendationCard.tsx`)**:
   - Live ML trigger state (`DISPATCH PUMP` vs `HOLD / IDLE`).
   - Target water volume in Liters & duration in minutes.
   - Model confidence score gauge.
   - Rain postponed shield alerts.
2. **ML Champion Performance Card (`MLModelPerformanceCard.tsx`)**:
   - Active champion model specs (Gradient Boosting / Random Forest / PyTorch LSTM).
   - Accuracy, Volume MAE, and ROC-AUC metrics.
3. **Composite Field & Crop Registration (`/register`)**:
   - Step-by-step registration form for farmers, fields, crops, and linked IoT sensors.

---

## 🚀 Running the Frontend

```bash
# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Dashboard URL: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Type Checking

```bash
npx tsc --noEmit
```
