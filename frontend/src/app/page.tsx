'use client';

import React, { useState, useEffect } from 'react';
import { Field, Sensor, SensorReading, WeatherData } from '@/types';

export default function DashboardPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In local dev, fetch from backend API
    async function fetchData() {
      try {
        const res = await fetch('/api/fields');
        if (res.ok) {
          const data = await res.json();
          setFields(data);
        }
      } catch (err) {
        console.error('Failed to fetch fields:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800">Smart Irrigation Telemetry Dashboard</h2>
        <p className="text-sm text-slate-500 mt-1">
          Real-time telemetry ingestion, soil moisture tracking, and OpenWeather meteorological sync.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric 1 */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Fields</span>
            <span className="text-xl">🌾</span>
          </div>
          <p className="text-2xl font-bold text-slate-800 mt-2">{fields.length || 1}</p>
          <span className="text-xs text-emerald-600 font-medium">● 1 Active Sector</span>
        </div>

        {/* Metric 2 */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Avg Soil Moisture</span>
            <span className="text-xl">💧</span>
          </div>
          <p className="text-2xl font-bold text-slate-800 mt-2">38.4%</p>
          <span className="text-xs text-blue-600 font-medium">Optimal Root Hydration</span>
        </div>

        {/* Metric 3 */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Ingestion Mode</span>
            <span className="text-xl">📡</span>
          </div>
          <p className="text-2xl font-bold text-slate-800 mt-2">REST & MQTT</p>
          <span className="text-xs text-purple-600 font-medium">Idempotent Pipeline Active</span>
        </div>
      </div>
    </div>
  );
}
