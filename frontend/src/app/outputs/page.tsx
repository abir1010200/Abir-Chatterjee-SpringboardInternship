'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  BarChart3,
  Layers,
  Cpu,
  Database,
  CheckCircle2,
  Sliders,
  Play,
  Volume2,
  ExternalLink,
  ArrowLeft,
  ChevronRight,
  TrendingUp,
  Droplets,
  Calendar,
  ShieldAlert,
} from 'lucide-react';
import FarmerWhatIfSimulator from '@/components/FarmerWhatIfSimulator';
import MLModelPerformanceCard from '@/components/MLModelPerformanceCard';
import IrrigationLogModal from '@/components/IrrigationLogModal';

interface OutputItem {
  id: string;
  category: 'ui' | 'ml' | 'eda' | 'api';
  title: string;
  subtitle: string;
  imageSrc: string;
  badge: string;
  description: string;
  metrics?: { label: string; value: string }[];
}

const outputsData: OutputItem[] = [
  // --- UI Outputs ---
  {
    id: 'login',
    category: 'ui',
    title: 'Farmer Authentication & PWA Gateway',
    subtitle: 'Mobile-first PWA login for rural operatives',
    imageSrc: '/images/milestone3/01_farmer_login_pwa.png',
    badge: 'PWA Web App',
    description:
      'Responsive login gateway supporting session persistence, fast demo login buttons, and service worker caching for offline resilience.',
    metrics: [
      { label: 'Auth Strategy', value: 'JWT / Session' },
      { label: 'Offline Support', value: 'Service Worker' },
      { label: 'Role', value: 'Farm Operative' },
    ],
  },
  {
    id: 'dashboard',
    category: 'ui',
    title: 'Live AI Command Dashboard',
    subtitle: 'Real-time telemetry, quick actions & weather forecast',
    imageSrc: '/images/milestone3/02_live_command_dashboard.png',
    badge: 'Command Center',
    description:
      'Unified executive cockpit presenting connected fields, real-time weather synched from OpenWeather, and instant AI guidance widgets.',
    metrics: [
      { label: 'Active Fields', value: '8 Parcels' },
      { label: 'Sensors Online', value: '14 Units' },
      { label: 'Water Saved', value: '56.9%' },
    ],
  },
  {
    id: 'fields',
    category: 'ui',
    title: 'Multi-Field Telemetry & Sensor Gauges',
    subtitle: 'Real-time volumetric soil moisture & crop stages',
    imageSrc: '/images/milestone3/03_field_management_telemetry.png',
    badge: 'IoT Fleet',
    description:
      'Live soil moisture dial gauges, ambient temperature readings, battery health monitoring, and FAO-56 Kc crop stage indicators.',
    metrics: [
      { label: 'Soil Sampling', value: '15-min intervals' },
      { label: 'Battery Monitor', value: 'Lithium LiFePO4' },
      { label: 'Soil Types', value: 'Clay, Loam, Sandy' },
    ],
  },
  {
    id: 'analytics',
    category: 'ui',
    title: 'Time-Series Sensor & Water Analytics',
    subtitle: 'Diurnal drying curves, ET0 and water usage trends',
    imageSrc: '/images/milestone3/04_sensor_and_water_analytics.png',
    badge: 'Analytics',
    description:
      'Interactive time-series charts illustrating diurnal soil drying curves, rain recharge events, and weekly volumetric consumption comparisons.',
    metrics: [
      { label: 'Telemetry Span', value: '180 Days' },
      { label: 'Sampling Points', value: '17,280' },
      { label: 'Resolution', value: 'Hourly' },
    ],
  },
  {
    id: 'schedule',
    category: 'ui',
    title: 'AI Irrigation Timetable & Schedule',
    subtitle: 'Physics-constrained dispatch slots & rain shields',
    imageSrc: '/images/milestone3/05_ai_irrigation_schedule.png',
    badge: 'Optimization',
    description:
      'Automated dispatch calendar enforcing 24h rain delay shields, 12h over-watering lockout safety buffers, and early-morning ET windows.',
    metrics: [
      { label: 'Rain Threshold', value: '> 40% Rain' },
      { label: 'Lockout Buffer', value: '12 Hours' },
      { label: 'Window', value: '04:00 - 07:00' },
    ],
  },
  {
    id: 'pump',
    category: 'ui',
    title: 'IoT Pump Hardware Dispatch Execution',
    subtitle: 'Manual and automated valve actuator dispatching',
    imageSrc: '/images/milestone3/06_pump_hardware_dispatch.png',
    badge: 'Actuation',
    description:
      'Real-time pump triggering verifying physical valve status, scheduled delivery duration (45 mins), and target delivery volume (1,200 Liters).',
    metrics: [
      { label: 'Actuator Protocol', value: 'MQTT / Relay' },
      { label: 'State Feedback', value: 'Active / Flowing' },
      { label: 'Delivery Target', value: '1,200 L' },
    ],
  },
  {
    id: 'swagger',
    category: 'api',
    title: 'FastAPI Interactive Swagger REST API',
    subtitle: 'Serving ML inference, telemetry ingestion & CRUD routes',
    imageSrc: '/images/milestone3/07_fastapi_swagger_docs.png',
    badge: 'FastAPI Backend',
    description:
      'OpenAPI 3.1 interactive documentation supporting REST ingestion, APScheduler weather sync, and scikit-learn / PyTorch serving.',
    metrics: [
      { label: 'Framework', value: 'FastAPI 0.110+' },
      { label: 'Validation', value: 'Pydantic v2' },
      { label: 'Port', value: ':8000' },
    ],
  },

  // --- ML Outputs ---
  {
    id: 'leaderboard',
    category: 'ml',
    title: 'Model Comparison & Benchmark Leaderboard',
    subtitle: 'Benchmarking Gradient Boosting, Random Forest & PyTorch LSTM',
    imageSrc: '/images/milestone3/08_model_comparison_leaderboard.png',
    badge: 'Champion ML',
    description:
      'Comprehensive benchmark leaderboard showing Gradient Boosting achieving the lowest Volume MAE (576.2 L) and high classification accuracy (99.27%).',
    metrics: [
      { label: 'Champion', value: 'HistGradientBoosting' },
      { label: 'Volume MAE', value: '576.2 Liters' },
      { label: 'ROC-AUC', value: '0.9892' },
    ],
  },
  {
    id: 'feat_imp',
    category: 'ml',
    title: 'Agronomic Feature Importance Ranking',
    subtitle: 'Top domain drivers in predictive irrigation decisions',
    imageSrc: '/images/milestone3/09_feature_importance_gradient_boosting.png',
    badge: 'Feature Store',
    description:
      'Relative feature importances: Soil moisture deficit, vapor pressure deficit (VPD), rain probability, and Kc factor drive >70% of model weight.',
    metrics: [
      { label: 'Top Feature', value: 'Moisture Deficit' },
      { label: 'VPD Weight', value: 'High' },
      { label: 'Total Features', value: '47 Engineered' },
    ],
  },
  {
    id: 'confusion',
    category: 'ml',
    title: 'Classification Confusion Matrix',
    subtitle: 'Unseen test evaluation for binary irrigation dispatching',
    imageSrc: '/images/milestone3/10_confusion_matrix_gradient_boosting.png',
    badge: 'Validation',
    description:
      'Normalized confusion matrix showing a 96.0% true positive rate on irrigation triggers and an ultra-low 0.8% false alarm rate.',
    metrics: [
      { label: 'Precision', value: '86.61%' },
      { label: 'Recall', value: '96.04%' },
      { label: 'F1-Score', value: '0.9108' },
    ],
  },
  {
    id: 'roc',
    category: 'ml',
    title: 'ROC-AUC Performance Curve',
    subtitle: 'Receiver operating characteristic across decision thresholds',
    imageSrc: '/images/milestone3/11_roc_curve_gradient_boosting.png',
    badge: 'ROC-AUC',
    description:
      'ROC curve demonstrating near-perfect class separation (AUC = 0.9892) between moisture-depleted crops and adequately hydrated fields.',
    metrics: [
      { label: 'AUC Score', value: '0.9892' },
      { label: 'Optimal Threshold', value: '0.50' },
      { label: 'Sensitivity', value: 'High' },
    ],
  },
  {
    id: 'residuals',
    category: 'ml',
    title: 'Water Volume Regression Residuals',
    subtitle: 'Error distribution between predicted and actual liters',
    imageSrc: '/images/milestone3/12_volume_residuals_gradient_boosting.png',
    badge: 'Volume Metering',
    description:
      'Residual plot showing tight normal distribution around zero, confirming consistent water volume predictions without systematic bias.',
    metrics: [
      { label: 'Mean Error', value: '~0 Liters' },
      { label: 'R² Score', value: '0.781' },
      { label: 'Standard Dev', value: 'Low' },
    ],
  },

  // --- EDA Outputs ---
  {
    id: 'soil_trends',
    category: 'eda',
    title: 'Soil Moisture Drying Curves & Infiltration Spikes',
    subtitle: 'Diurnal solar depletion & sharp recharge transitions',
    imageSrc: '/images/milestone3/13_soil_moisture_trends.png',
    badge: 'Physics EDA',
    description:
      'Longitudinal 180-day telemetry curves capturing daytime transpiration moisture drops and instant infiltration recovery spikes upon rainfall.',
    metrics: [
      { label: 'Diurnal Cycle', value: '24-hour periodic' },
      { label: 'Infiltration', value: 'Immediate' },
      { label: 'Decay Rate', value: 'Physics-informed' },
    ],
  },
  {
    id: 'crop_water',
    category: 'eda',
    title: 'FAO-56 Crop Water Requirements by Stage',
    subtitle: 'Crop coefficient Kc trajectory across vegetative & flowering',
    imageSrc: '/images/milestone3/14_crop_water_requirements.png',
    badge: 'Agronomy',
    description:
      'Crop coefficient (Kc) curves peaking during flowering and mid-season fruit development (Kc = 1.15 - 1.25), dictating higher target volumes.',
    metrics: [
      { label: 'Initial Kc', value: '0.40' },
      { label: 'Peak Kc', value: '1.25' },
      { label: 'Crops Evaluated', value: 'Wheat, Tomato, Corn' },
    ],
  },
  {
    id: 'weather_dist',
    category: 'eda',
    title: 'Environmental & Meteorological Distributions',
    subtitle: 'Temperature, relative humidity, solar radiation & rain',
    imageSrc: '/images/milestone3/15_weather_distributions.png',
    badge: 'Weather Telemetry',
    description:
      'Bivariate and marginal distributions validating realistic meteorological variance across seasonal agro-climatic boundaries.',
    metrics: [
      { label: 'Temp Range', value: '12°C - 42°C' },
      { label: 'Humidity Span', value: '25% - 95%' },
      { label: 'Solar Max', value: '1,000 W/m²' },
    ],
  },
  {
    id: 'irrigation_patterns',
    category: 'eda',
    title: 'Historical Irrigation Trigger Patterns',
    subtitle: 'Volume deliveries, moisture triggers & target balance',
    imageSrc: '/images/milestone3/16_irrigation_history_patterns.png',
    badge: 'Dataset Analysis',
    description:
      'Exploration of target balance (~15% positive irrigation frequency) and volumetric distribution across distinct soil types.',
    metrics: [
      { label: 'Target Ratio', value: '15.2% Positive' },
      { label: 'Avg Volume', value: '1,450 Liters' },
      { label: 'Max Delivery', value: '4,000 Liters' },
    ],
  },
];

export default function Milestone3OutputsPage() {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [selectedImage, setSelectedImage] = useState<OutputItem | null>(null);
  const [isLogModalOpen, setIsLogModalOpen] = useState(false);
  const [simResults, setSimResults] = useState<{
    soil_moisture: number;
    temperature: number;
    recommended_volume: number;
    action: string;
  } | null>(null);

  const handleSimulate = (params: {
    soil_moisture: number;
    temperature: number;
    humidity: number;
    rain_probability: number;
  }) => {
    // Client-side JavaScript model inference simulation
    const deficit = Math.max(0, 36.0 - params.soil_moisture);
    const rainFactor = params.rain_probability > 40 ? 0 : 1;
    const estVol = rainFactor === 0 ? 0 : Math.round(deficit * 120 + params.temperature * 15);
    const action =
      params.rain_probability > 40
        ? '🛡️ RAIN SHIELD ACTIVE (HOLD)'
        : params.soil_moisture < 30
        ? '💧 IMMEDIATE WATERING REQUIRED'
        : '🌱 OPTIMAL SOIL MOISTURE (HOLD)';

    setSimResults({
      soil_moisture: params.soil_moisture,
      temperature: params.temperature,
      recommended_volume: estVol,
      action,
    });
  };

  const filteredItems =
    activeCategory === 'all'
      ? outputsData
      : outputsData.filter((item) => item.category === activeCategory);

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header Banner */}
      <div className="bg-gradient-to-br from-emerald-950 via-teal-900 to-slate-950 rounded-3xl p-6 text-white shadow-2xl relative overflow-hidden border border-emerald-500/30">
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-extrabold rounded-full mb-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-spin" style={{ animationDuration: '8s' }} />
              <span>Milestone 3 Production Deliverable</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              System Outputs & Model Showcase
            </h1>
            <p className="text-xs sm:text-sm text-emerald-200/90 mt-1 max-w-xl font-medium leading-relaxed">
              Consolidated gallery of live Next.js PWA interfaces, client-side JavaScript model simulators, FastAPI Swagger docs, and ML evaluation outputs.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-extrabold text-xs rounded-2xl border border-white/20 transition-all flex items-center gap-1.5"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-2xl shadow-lg transition-all flex items-center gap-1.5"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Swagger API</span>
            </a>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          { key: 'all', label: 'All Pictures (16)' },
          { key: 'ui', label: 'PWA Web App (6)' },
          { key: 'ml', label: 'ML Models & Leaderboard (5)' },
          { key: 'eda', label: 'Agronomic EDA (4)' },
          { key: 'api', label: 'FastAPI Swagger (1)' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveCategory(tab.key)}
            className={`px-4 py-2 rounded-2xl text-xs font-black whitespace-nowrap transition-all shadow-xs ${
              activeCategory === tab.key
                ? 'bg-emerald-700 dark:bg-emerald-600 text-white shadow-md'
                : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Live Interactive JavaScript Models Section */}
      <div className="bg-gradient-to-br from-purple-50/80 via-slate-50 to-emerald-50/80 dark:from-slate-900 dark:via-purple-950/20 dark:to-slate-900 rounded-3xl p-6 border border-purple-200 dark:border-purple-900/40 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-purple-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-2xl bg-purple-600 text-white flex items-center justify-center font-black shadow-md">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-black text-slate-900 dark:text-white">
                Live JavaScript Model Simulator & Modals Running on Localhost
              </h2>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                Test client-side JavaScript parameter adjustments, live model inference triggers, and pop-up modal dialogs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsLogModalOpen(true)}
              className="px-3.5 py-2 bg-purple-600 hover:bg-purple-700 text-white font-extrabold text-xs rounded-xl shadow-md transition-all flex items-center gap-1.5"
            >
              <span>Launch Irrigation Log Modal</span>
            </button>
          </div>
        </div>

        {/* Live Simulation Output Pill if computed */}
        {simResults && (
          <div className="p-4 bg-white dark:bg-slate-800 rounded-2xl border border-purple-200 dark:border-purple-700/50 shadow-md flex flex-wrap items-center justify-between gap-3 animate-fadeIn">
            <div>
              <div className="text-[10px] font-black uppercase text-purple-600 dark:text-purple-300">
                Live JS Model Output
              </div>
              <div className="text-sm font-black text-slate-900 dark:text-white">
                {simResults.action}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-bold">Recommended Delivery</div>
              <div className="text-base font-black text-blue-600 dark:text-blue-400">
                {simResults.recommended_volume.toLocaleString()} Liters
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FarmerWhatIfSimulator onSimulate={handleSimulate} loading={false} />
          <MLModelPerformanceCard
            modelInfo={{
              active_model: 'gradient_boosting',
              version: '1.0.0',
              trained_at: '2026-09-12T14:30:00Z',
              metrics: {
                accuracy: 0.9927,
                precision: 0.8661,
                recall: 0.9604,
                volume_mae: 576.2,
                roc_auc: 0.9892,
              },
            }}
            loading={false}
          />
        </div>
      </div>

      {/* Outputs Picture Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredItems.map((item, idx) => (
          <div
            key={item.id}
            className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-md hover:shadow-2xl transition-all group flex flex-col"
          >
            {/* Image Preview Container */}
            <div
              onClick={() => setSelectedImage(item)}
              className="relative w-full aspect-[16/10] bg-slate-100 dark:bg-slate-950 overflow-hidden cursor-pointer group-hover:opacity-95 transition-opacity"
            >
              {/* Image using native img to guarantee immediate render across localhost and relative routes */}
              <img
                src={item.imageSrc}
                alt={item.title}
                className="w-full h-full object-cover object-top transition-transform duration-300 group-hover:scale-[1.02]"
                loading="lazy"
              />
              <div className="absolute top-3 left-3 px-3 py-1 bg-slate-900/80 backdrop-blur-md text-white text-[10px] font-black rounded-full border border-white/20">
                Figure {idx + 1} — {item.badge}
              </div>
              <div className="absolute bottom-3 right-3 px-2.5 py-1 bg-emerald-600/90 backdrop-blur-md text-white text-[10px] font-extrabold rounded-lg shadow-sm">
                Click to Expand 🔍
              </div>
            </div>

            {/* Description Body */}
            <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <h3 className="text-base font-black text-slate-900 dark:text-white tracking-tight">
                  {item.title}
                </h3>
                <p className="text-xs text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">
                  {item.subtitle}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  {item.description}
                </p>
              </div>

              {/* Metrics Pill Grid */}
              {item.metrics && (
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                  {item.metrics.map((m, mIdx) => (
                    <div
                      key={mIdx}
                      className="bg-slate-50 dark:bg-slate-800/60 p-2 rounded-xl border border-slate-100 dark:border-slate-800 text-center"
                    >
                      <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider truncate">
                        {m.label}
                      </div>
                      <div className="text-xs font-black text-slate-800 dark:text-slate-100 truncate mt-0.5">
                        {m.value}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Modal Lightbox for Full-Size Pictures */}
      {selectedImage && (
        <div
          onClick={() => setSelectedImage(null)}
          className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-white dark:bg-slate-900 max-w-4xl w-full rounded-3xl overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4 p-5 max-h-[90vh] flex flex-col"
          >
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-black text-slate-900 dark:text-white">
                  {selectedImage.title}
                </h3>
                <p className="text-xs text-slate-500">{selectedImage.subtitle}</p>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-black text-sm flex items-center justify-center hover:bg-slate-200"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-auto rounded-2xl bg-slate-950 flex items-center justify-center p-2">
              <img
                src={selectedImage.imageSrc}
                alt={selectedImage.title}
                className="max-h-[65vh] w-auto object-contain rounded-xl"
              />
            </div>

            <div className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {selectedImage.description}
            </div>
          </div>
        </div>
      )}

      {/* Interactive JavaScript Irrigation Log Modal Dialog */}
      <IrrigationLogModal
        isOpen={isLogModalOpen}
        onClose={() => setIsLogModalOpen(false)}
        onSaveSuccess={() => {
          setIsLogModalOpen(false);
          alert('Irrigation log entry saved successfully!');
        }}
        fields={[
          {
            id: 1,
            farmer_id: 1,
            name: 'North Valley Wheat Sector',
            latitude: 18.5204,
            longitude: 73.8567,
            size_hectares: 4.5,
            soil_type: 'Clay Loam',
            created_at: '2026-08-26T17:28:03.530407',
          },
          {
            id: 2,
            farmer_id: 2,
            name: 'Nashik Tomato Sector 1',
            latitude: 19.9975,
            longitude: 73.7898,
            size_hectares: 2.2,
            soil_type: 'Sandy Loam',
            created_at: '2026-08-26T17:58:18.986231',
          },
        ]}
      />
    </div>
  );
}
