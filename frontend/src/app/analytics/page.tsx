'use client';

import React, { useState } from 'react';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceArea,
} from 'recharts';
import { BarChart3, Droplets, CloudRain, Thermometer, Volume2 } from 'lucide-react';

export default function AnalyticsPage() {
  const { t, speakText } = useKrishiPals();
  const [timeRange, setTimeRange] = useState<'7d' | '30d'>('7d');

  // Soil Moisture 7-day time series dataset
  const moistureData = [
    { day: 'Mon', moisture: 34.2, minTarget: 30, maxTarget: 45 },
    { day: 'Tue', moisture: 31.8, minTarget: 30, maxTarget: 45 },
    { day: 'Wed', moisture: 28.5, minTarget: 30, maxTarget: 45 },
    { day: 'Thu', moisture: 42.1, minTarget: 30, maxTarget: 45 },
    { day: 'Fri', moisture: 39.4, minTarget: 30, maxTarget: 45 },
    { day: 'Sat', moisture: 36.0, minTarget: 30, maxTarget: 45 },
    { day: 'Sun', moisture: 33.5, minTarget: 30, maxTarget: 45 },
  ];

  // Weather & Rain probability 7-day dataset
  const weatherData = [
    { day: 'Mon', temp: 26.5, rainProb: 10, rainfall: 0 },
    { day: 'Tue', temp: 28.0, rainProb: 15, rainfall: 0 },
    { day: 'Wed', temp: 27.5, rainProb: 65, rainfall: 12.4 },
    { day: 'Thu', temp: 25.0, rainProb: 40, rainfall: 3.2 },
    { day: 'Fri', temp: 27.2, rainProb: 10, rainfall: 0 },
    { day: 'Sat', temp: 29.1, rainProb: 5, rainfall: 0 },
    { day: 'Sun', temp: 28.4, rainProb: 20, rainfall: 0 },
  ];

  // Water usage dataset
  const waterUsageData = [
    { day: 'Mon', applied: 1200, target: 1250 },
    { day: 'Tue', applied: 0, target: 0 },
    { day: 'Wed', applied: 1250, target: 1250 },
    { day: 'Thu', applied: 0, target: 0 },
    { day: 'Fri', applied: 1100, target: 1200 },
    { day: 'Sat', applied: 0, target: 0 },
    { day: 'Sun', applied: 1250, target: 1250 },
  ];

  return (
    <div className="space-y-5 pb-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-4 shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-base font-extrabold text-slate-800 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" /> KrishiPals Sensor & Weather {t.trends}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            Real-time IoT soil moisture timelines, rain forecasts & water consumption charts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => speakText('Soil moisture average is 36 percent. Water saved this week is 4,500 liters.')}
            className="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-2xl text-xs font-bold transition-all"
            title="Read Analytics Aloud"
          >
            <Volume2 className="w-4 h-4 text-emerald-600" />
          </button>

          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs font-bold">
            <button
              onClick={() => setTimeRange('7d')}
              className={`px-3 py-1 rounded-xl transition-all ${
                timeRange === '7d' ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs font-extrabold' : 'text-slate-500 dark:text-slate-400'
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange('30d')}
              className={`px-3 py-1 rounded-xl transition-all ${
                timeRange === '30d' ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs font-extrabold' : 'text-slate-500 dark:text-slate-400'
              }`}
            >
              30 Days
            </button>
          </div>
        </div>
      </div>

      {/* 1. Soil Moisture Trend Chart */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="w-4 h-4 text-blue-500" />
            <h3 className="font-extrabold text-sm text-slate-800 dark:text-white">Soil Moisture (%) Timeline</h3>
          </div>
          <span className="text-[10px] font-extrabold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 px-2.5 py-0.5 rounded-full">
            Target Hydration: 30% - 45%
          </span>
        </div>

        <div className="h-56 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={moistureData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis domain={[20, 50]} tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ borderRadius: '16px', fontSize: '12px', border: '1px solid #cbd5e1' }}
              />
              <ReferenceArea y1={30} y2={45} fill="#10b981" fillOpacity={0.15} />
              <Line
                type="monotone"
                dataKey="moisture"
                name="Soil Moisture %"
                stroke="#0284c7"
                strokeWidth={3}
                dot={{ r: 4, fill: '#0284c7' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Weather & Rainfall Trend Chart */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CloudRain className="w-4 h-4 text-sky-500" />
            <h3 className="font-extrabold text-sm text-slate-800 dark:text-white">Temperature (°C) & Rain Probability (%)</h3>
          </div>
        </div>

        <div className="h-56 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={weatherData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ borderRadius: '16px', fontSize: '12px', border: '1px solid #cbd5e1' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '5px' }} />
              <Bar dataKey="rainProb" name="Rain Prob %" fill="#38bdf8" radius={[8, 8, 0, 0]} />
              <Bar dataKey="temp" name="Temperature °C" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Water Consumption Chart */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-extrabold text-sm text-slate-800 dark:text-white">Water Consumption (Liters Applied)</h3>
          </div>
        </div>

        <div className="h-56 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={waterUsageData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ borderRadius: '16px', fontSize: '12px', border: '1px solid #cbd5e1' }}
              />
              <Bar dataKey="applied" name="Liters Applied" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
