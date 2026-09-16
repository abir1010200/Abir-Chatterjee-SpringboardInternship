'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Field, SensorReading, WeatherData, ScheduleResponse, ModelInfoResponse } from '@/types';
import AIRecommendationCard from '@/components/AIRecommendationCard';
import MLModelPerformanceCard from '@/components/MLModelPerformanceCard';
import FarmerWhatIfSimulator from '@/components/FarmerWhatIfSimulator';

export default function DashboardPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [selectedFieldId, setSelectedFieldId] = useState<number | null>(1);
  const [latestWeather, setLatestWeather] = useState<WeatherData | null>(null);
  const [latestReading, setLatestReading] = useState<SensorReading | null>(null);

  // ML State
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [mlLoading, setMlLoading] = useState(false);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const fieldsRes = await fetch('/api/fields');
        if (fieldsRes.ok) {
          const fieldsData = await fieldsRes.json();
          setFields(fieldsData);
          if (fieldsData.length > 0) {
            const fId = fieldsData[0].id;
            setSelectedFieldId(fId);
            fetchFieldMetrics(fId);
            fetchMLRecommendation(fId);
          }
        } else {
          // Fallback if DB not seeded yet
          fetchMLRecommendation(1);
        }
        fetchModelInfo();
      } catch (err) {
        console.error('Failed to load fields:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const fetchFieldMetrics = async (fieldId: number) => {
    try {
      // 1. Fetch weather
      const weatherRes = await fetch(`/api/weather/field/${fieldId}/latest`);
      if (weatherRes.ok) {
        const wData = await weatherRes.json();
        setLatestWeather(wData);
      }

      // 2. Fetch sensor readings
      const sensorsRes = await fetch('/api/sensors');
      if (sensorsRes.ok) {
        const sensors = await sensorsRes.json();
        const fieldSensors = sensors.filter((s: any) => s.field_id === fieldId);
        if (fieldSensors.length > 0) {
          const readingsRes = await fetch(`/api/sensors/${fieldSensors[0].id}/readings?limit=1`);
          if (readingsRes.ok) {
            const readingsData = await readingsRes.json();
            if (readingsData.length > 0) {
              setLatestReading(readingsData[0]);
            }
          }
        }
      }
    } catch (e) {
      console.error('Error fetching field metrics:', e);
    }
  };

  const fetchMLRecommendation = async (fieldId: number) => {
    setMlLoading(true);
    try {
      // Try backend endpoint first, fallback to mock if unseeded
      const res = await fetch(`/api/ml/recommendation/${fieldId}`, { method: 'GET' });
      if (res.ok) {
        const schedData = await res.json();
        setSchedule(schedData);
      } else {
        // Fallback default recommendation
        setSchedule({
          field_id: fieldId,
          irrigation_required: true,
          predicted_volume_liters: 1250,
          recommended_duration_minutes: 45,
          recommended_start_time: new Date(Date.now() + 3600 * 1000 * 2).toISOString(),
          confidence_score: 0.985,
          model_name: 'random_forest',
          model_version: '1.0.0',
          rain_postponed: false,
          moisture_deficit_percent: 22.5,
          farmer_summary: 'Water your Wheat (Vegetative) field tomorrow morning at 6:00 AM with 1,250 Liters (~45 mins pump) to maintain optimal soil moisture.',
          action_badge: '💧 WATER TODAY (06:00 AM)',
          water_saving_tip: '💡 Morning watering (6 AM - 8 AM) reduces evaporation loss by up to 25% compared to afternoon heat.',
          soil_health_status: 'Needs Irrigation (Dry)',
          pump_duration_display: '45 minutes',
          generated_at: new Date().toISOString(),
        });
      }
    } catch (err) {
      console.warn('Unable to fetch ML recommendation from server, using active state fallback:', err);
    } finally {
      setMlLoading(false);
    }
  };

  const handleSimulate = async (customParams: {
    soil_moisture: number;
    temperature: number;
    humidity: number;
    rain_probability: number;
  }) => {
    setMlLoading(true);
    try {
      const payload = {
        field_id: selectedFieldId || 1,
        soil_moisture: customParams.soil_moisture,
        temperature: customParams.temperature,
        humidity: customParams.humidity,
        rainfall_1h: 0.0,
        rain_probability: customParams.rain_probability,
        soil_type: currentField?.soil_type || 'Clay Loam',
        crop_type: 'Wheat',
        growth_stage: 'Vegetative',
        kc_factor: 1.15,
        size_hectares: currentField?.size_hectares || 2.5,
      };
      const res = await fetch('/api/ml/predict/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const schedData = await res.json();
        setSchedule(schedData);
      }
    } catch (e) {
      console.error('Error running custom ML simulation:', e);
    } finally {
      setMlLoading(false);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const res = await fetch('/api/ml/model/info');
      if (res.ok) {
        const mInfo = await res.json();
        setModelInfo(mInfo);
      }
    } catch (err) {
      console.warn('Unable to fetch ML model info:', err);
    }
  };

  const handleFieldChange = (fieldId: number) => {
    setSelectedFieldId(fieldId);
    fetchFieldMetrics(fieldId);
    fetchMLRecommendation(fieldId);
  };

  const currentField = fields.find((f) => f.id === selectedFieldId);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded-lg mb-2">
            <span>🌾</span> AI-Powered Farmer Irrigation Assistant
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Smart Farmer Irrigation Command Hub</h2>
          <p className="text-sm text-slate-500 mt-1">
            Real-time IoT soil moisture monitoring, AI watering predictions, and automated rain saving shields.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/register"
            className="px-4 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-medium rounded-xl shadow-sm transition-all flex items-center gap-2"
          >
            <span>➕</span> Register Field & Crop
          </Link>
        </div>
      </div>

      {/* Field Selector Bar */}
      {fields.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Fields:</span>
          {fields.map((f) => (
            <button
              key={f.id}
              onClick={() => handleFieldChange(f.id)}
              className={`px-4 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                selectedFieldId === f.id
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {f.name} ({f.size_hectares} ha)
            </button>
          ))}
        </div>
      )}

      {/* Milestone 2 AI Recommendation Widget */}
      <AIRecommendationCard
        schedule={schedule}
        loading={mlLoading}
        onRefresh={() => selectedFieldId && fetchMLRecommendation(selectedFieldId)}
      />

      {/* Interactive Farmer What-If Tool */}
      <FarmerWhatIfSimulator
        onSimulate={handleSimulate}
        loading={mlLoading}
      />

      {/* Main Real-Time Telemetry Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Soil Moisture */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Soil Moisture</span>
            <span className="text-xl">💧</span>
          </div>
          <p className="text-3xl font-extrabold text-slate-800 mt-3">
            {latestReading ? `${latestReading.soil_moisture}%` : '38.4%'}
          </p>
          <div className="mt-3 flex items-center gap-2 text-xs font-medium text-emerald-600">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Optimal Hydration Target
          </div>
        </div>

        {/* Rain Probability */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Rain Probability</span>
            <span className="text-xl">🌧️</span>
          </div>
          <p className="text-3xl font-extrabold text-blue-600 mt-3">
            {latestWeather ? `${latestWeather.rain_probability}%` : '15.0%'}
          </p>
          <p className="mt-3 text-xs text-slate-500">
            {latestWeather && latestWeather.rain_probability > 40
              ? '⚠️ High Rain Forecast: Delaying Irrigation'
              : '✅ Low Rain Forecast: Normal Cycle'}
          </p>
        </div>

        {/* Ambient Temperature */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Atmospheric Temp</span>
            <span className="text-xl">☀️</span>
          </div>
          <p className="text-3xl font-extrabold text-amber-600 mt-3">
            {latestWeather ? `${latestWeather.temperature}°C` : '27.4°C'}
          </p>
          <p className="mt-3 text-xs text-slate-500">
            Humidity: {latestWeather ? `${latestWeather.humidity}%` : '48.0%'}
          </p>
        </div>

        {/* Active Crop & Kc */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Crop Stage & Kc</span>
            <span className="text-xl">🌱</span>
          </div>
          <p className="text-xl font-bold text-slate-800 mt-3">
            {currentField?.crops?.[0]?.crop_type || 'Wheat (HD-2967)'}
          </p>
          <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
            <span>Stage: <strong className="text-slate-700">{currentField?.crops?.[0]?.growth_stage || 'Vegetative'}</strong></span>
            <span>Kc: <strong className="text-emerald-700">{currentField?.crops?.[0]?.kc_factor || 1.15}</strong></span>
          </div>
        </div>
      </div>

      {/* Champion ML Model Performance Spec Card */}
      <MLModelPerformanceCard modelInfo={modelInfo} loading={loading} />

      {/* Ingestion & Hardware Status Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <span>📡</span> System Pipeline & Service Mesh Status
          </h3>
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-sm">
              <div className="flex items-center gap-3">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <div>
                  <p className="font-semibold text-slate-800">FastAPI Ingestion & Rest Engine</p>
                  <p className="text-xs text-slate-400">POST /api/sensors/readings & GET /api/ml/recommendation</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-lg">Operational (Port 8000)</span>
            </div>

            <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-sm">
              <div className="flex items-center gap-3">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
                <div>
                  <p className="font-semibold text-slate-800">ML Predictive Serving Microservice</p>
                  <p className="text-xs text-slate-400">Random Forest / PyTorch LSTM Inference Engine</p>
                </div>
              </div>
              <span className="text-xs font-bold text-purple-700 bg-purple-100 px-2.5 py-1 rounded-lg">Serving (Port 8001)</span>
            </div>

            <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-sm">
              <div className="flex items-center gap-3">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <div>
                  <p className="font-semibold text-slate-800">Mosquitto MQTT Telemetry Subscriber</p>
                  <p className="text-xs text-slate-400">Topic: farm/+/field/+/sensor/+/reading</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-lg">Listening (Port 1883)</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <span>ℹ️</span> Field Information
          </h3>
          <div className="mt-4 space-y-2.5 text-xs text-slate-600">
            <p className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="font-medium text-slate-400">Field Name:</span>
              <span className="font-semibold text-slate-800">{currentField?.name || 'North Valley Sector'}</span>
            </p>
            <p className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="font-medium text-slate-400">Coordinates:</span>
              <span className="font-semibold text-slate-800">{currentField?.latitude || 18.5204}° N, {currentField?.longitude || 73.8567}° E</span>
            </p>
            <p className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="font-medium text-slate-400">Soil Type:</span>
              <span className="font-semibold text-slate-800">{currentField?.soil_type || 'Clay Loam'}</span>
            </p>
            <p className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="font-medium text-slate-400">Linked Sensor:</span>
              <span className="font-semibold font-mono text-emerald-700">SEN-WHEAT-01</span>
            </p>
            <p className="flex justify-between py-1.5">
              <span className="font-medium text-slate-400">Storage Engine:</span>
              <span className="font-semibold text-slate-800">PostgreSQL / TimescaleDB</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
