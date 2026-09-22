'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Field, SensorReading, WeatherData, ScheduleResponse, ModelInfoResponse } from '@/types';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import AIRecommendationCard from '@/components/AIRecommendationCard';
import FieldSummaryCard from '@/components/FieldSummaryCard';
import MLModelPerformanceCard from '@/components/MLModelPerformanceCard';
import FarmerWhatIfSimulator from '@/components/FarmerWhatIfSimulator';
import { Sprout, Calendar, History, BarChart3, PlusCircle, Droplets, Thermometer, CloudRain, Clock, Sparkles, Volume2, Mic } from 'lucide-react';

export default function DashboardPage() {
  const { t, speakText, setIsAssistantOpen, selectedFieldId, setSelectedFieldId } = useKrishiPals();
  const [mounted, setMounted] = useState(false);
  const [fields, setFields] = useState<Field[]>([]);
  const [latestWeather, setLatestWeather] = useState<WeatherData | null>(null);
  const [latestReading, setLatestReading] = useState<SensorReading | null>(null);

  // ML State
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [mlLoading, setMlLoading] = useState(false);

  // Static constant default fallback fields
  const fallbackFields: Field[] = [
    {
      id: 1,
      farmer_id: 1,
      name: 'North Valley Field',
      latitude: 18.5204,
      longitude: 73.8567,
      size_hectares: 2.5,
      soil_type: 'Clay Loam',
      created_at: '2026-01-10T00:00:00.000Z',
      crops: [
        {
          id: 1,
          field_id: 1,
          crop_type: 'Wheat (HD-2967)',
          growth_stage: 'Vegetative',
          planted_date: '2026-01-10',
          kc_factor: 1.15,
          is_active: true,
        },
      ],
    },
    {
      id: 2,
      farmer_id: 1,
      name: 'East Orchard Sector',
      latitude: 18.525,
      longitude: 73.86,
      size_hectares: 1.8,
      soil_type: 'Sandy Loam',
      created_at: '2026-01-10T00:00:00.000Z',
      crops: [
        {
          id: 2,
          field_id: 2,
          crop_type: 'Tomato (Hybrid)',
          growth_stage: 'Flowering',
          planted_date: '2026-02-01',
          kc_factor: 1.25,
          is_active: true,
        },
      ],
    },
  ];

  useEffect(() => {
    setMounted(true);

    async function loadDashboardData() {
      try {
        const fieldsRes = await fetch('/api/fields');
        if (fieldsRes.ok) {
          const fieldsData = await fieldsRes.json();
          if (fieldsData && fieldsData.length > 0) {
            setFields(fieldsData);
            const fId = fieldsData[0].id;
            setSelectedFieldId(fId);
            fetchFieldMetrics(fId);
            fetchMLRecommendation(fId);
          } else {
            setFields(fallbackFields);
            setSelectedFieldId(1);
            fetchMLRecommendation(1);
          }
        } else {
          setFields(fallbackFields);
          setSelectedFieldId(1);
          fetchMLRecommendation(1);
        }
        fetchModelInfo();
      } catch (err) {
        console.warn('Using fallback field structure:', err);
        setFields(fallbackFields);
        setSelectedFieldId(1);
        fetchMLRecommendation(1);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const fetchFieldMetrics = async (fieldId: number) => {
    try {
      const weatherRes = await fetch(`/api/weather/field/${fieldId}/latest`);
      if (weatherRes.ok) {
        const wData = await weatherRes.json();
        setLatestWeather(wData);
      }

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
      const res = await fetch(`/api/ml/recommendation/${fieldId}`, { method: 'GET' });
      if (res.ok) {
        const schedData = await res.json();
        setSchedule(schedData);
      } else {
        setSchedule({
          field_id: fieldId,
          irrigation_required: true,
          predicted_volume_liters: 1250,
          recommended_duration_minutes: 45,
          recommended_start_time: '2026-09-19T06:00:00.000Z',
          confidence_score: 0.985,
          model_name: 'random_forest',
          model_version: '1.0.0',
          rain_postponed: false,
          moisture_deficit_percent: 22.5,
          farmer_summary: 'Water your active field tomorrow morning at 6:00 AM with 1,250 Liters (~45 mins pump) to maintain optimal soil moisture.',
          action_badge: '💧 WATER TODAY (06:00 AM)',
          water_saving_tip: '💡 Morning watering (6 AM - 8 AM) reduces evaporation loss by up to 25% compared to afternoon heat.',
          soil_health_status: 'Needs Irrigation (Dry)',
          pump_duration_display: '45 minutes',
          generated_at: '2026-09-19T06:00:00.000Z',
        });
      }
    } catch (err) {
      console.warn('Unable to fetch ML recommendation from server:', err);
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
        crop_type: currentField?.crops?.[0]?.crop_type || 'Wheat',
        growth_stage: currentField?.crops?.[0]?.growth_stage || 'Vegetative',
        kc_factor: currentField?.crops?.[0]?.kc_factor || 1.15,
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

  const activeFieldsList = fields.length > 0 ? fields : fallbackFields;
  const currentField = activeFieldsList.find((f) => f.id === selectedFieldId) || activeFieldsList[0];

  if (!mounted) {
    return (
      <div className="p-8 text-center text-slate-400 text-xs animate-pulse">
        Loading KrishiPals Ultra HD Dashboard...
      </div>
    );
  }

  return (
    <div className="space-y-5 pb-6">
      {/* KrishiPals Welcome Banner */}
      <div className="bg-gradient-to-br from-emerald-950 via-teal-900 to-slate-950 rounded-3xl p-6 text-white shadow-2xl relative overflow-hidden border border-emerald-500/30 glow-border">
        {/* Decorative background glow */}
        <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[11px] font-extrabold rounded-full mb-2.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-spin" style={{ animationDuration: '8s' }} />
              <span>KrishiPals AI Farm Ecosystem</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">{t.welcomeFarmer}</h2>
            <p className="text-xs text-emerald-200/90 mt-1 max-w-md font-medium leading-relaxed">
              {t.aiAssistantSubtitle}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsAssistantOpen(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-black text-xs rounded-2xl shadow-lg transition-all flex items-center gap-1.5"
            >
              <Mic className="w-4 h-4" />
              <span>{t.speakToKrishiPals}</span>
            </button>

            <Link
              href="/register"
              className="px-3.5 py-2.5 bg-white/10 hover:bg-white/20 text-white font-extrabold text-xs rounded-2xl border border-white/20 transition-all flex items-center gap-1.5"
            >
              <PlusCircle className="w-4 h-4 text-emerald-400" />
              <span>{t.addField}</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Action Navigation Grid */}
      <div className="grid grid-cols-4 gap-2.5">
        <Link
          href="/fields"
          className="bg-white dark:bg-slate-900 p-3.5 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:border-emerald-500 hover:shadow-md transition-all flex flex-col items-center text-center group"
        >
          <span className="w-10 h-10 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Sprout className="w-5 h-5" />
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{t.fields}</span>
        </Link>

        <Link
          href="/schedule"
          className="bg-white dark:bg-slate-900 p-3.5 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:border-emerald-500 hover:shadow-md transition-all flex flex-col items-center text-center group"
        >
          <span className="w-10 h-10 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Calendar className="w-5 h-5" />
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{t.schedule}</span>
        </Link>

        <Link
          href="/history"
          className="bg-white dark:bg-slate-900 p-3.5 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:border-emerald-500 hover:shadow-md transition-all flex flex-col items-center text-center group"
        >
          <span className="w-10 h-10 rounded-2xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <History className="w-5 h-5" />
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{t.history}</span>
        </Link>

        <Link
          href="/analytics"
          className="bg-white dark:bg-slate-900 p-3.5 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:border-emerald-500 hover:shadow-md transition-all flex flex-col items-center text-center group"
        >
          <span className="w-10 h-10 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <BarChart3 className="w-5 h-5" />
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{t.trends}</span>
        </Link>
      </div>

      {/* Field Cards Selector */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-extrabold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {t.registeredFields} ({activeFieldsList.length})
          </h3>
          <Link href="/fields" className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 hover:underline">
            {t.manageAll} →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {activeFieldsList.map((f) => (
            <FieldSummaryCard
              key={f.id}
              field={f}
              soilMoisture={latestReading ? latestReading.soil_moisture : 38.4}
              temperature={latestWeather ? latestWeather.temperature : 27.4}
              rainProbability={latestWeather ? latestWeather.rain_probability : 15.0}
              isSelected={selectedFieldId === f.id}
              onSelect={() => handleFieldChange(f.id)}
            />
          ))}
        </div>
      </div>

      {/* AI Recommendation Widget */}
      <AIRecommendationCard
        schedule={schedule}
        loading={mlLoading}
        onRefresh={() => selectedFieldId && fetchMLRecommendation(selectedFieldId)}
      />

      {/* Today's Irrigation Schedule Summary */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-md space-y-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-extrabold text-sm text-slate-900 dark:text-white">{t.todaysIrrigationPlan}</h3>
          </div>
          <span className="text-[10px] font-extrabold px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200">
            {schedule?.rain_postponed ? '🛡️ Rain Shield Active' : '💧 Action Recommended'}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-2xl border border-slate-100 dark:border-slate-700/60">
            <span className="text-slate-400 font-bold uppercase text-[10px]">{t.recommendedTime}</span>
            <p className="font-black text-base text-slate-800 dark:text-slate-100 mt-0.5">06:00 AM</p>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-medium">{t.morningCoolWindow}</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-2xl border border-slate-100 dark:border-slate-700/60">
            <span className="text-slate-400 font-bold uppercase text-[10px]">{t.waterVolumeDuration}</span>
            <p className="font-black text-base text-emerald-600 dark:text-emerald-400 mt-0.5">
              {schedule?.predicted_volume_liters || 1250} Liters
            </p>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-medium">~{schedule?.recommended_duration_minutes || 45} mins pump run</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <Link
            href="/schedule"
            className="w-full text-center py-2.5 bg-emerald-700 hover:bg-emerald-800 dark:bg-emerald-600 text-white rounded-2xl font-extrabold text-xs shadow-md transition-all"
          >
            View Full Dispatch Details →
          </Link>
        </div>
      </div>

      {/* Real-Time Telemetry Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
            <span>{t.soilMoisture}</span>
            <Droplets className="w-4 h-4 text-blue-500" />
          </div>
          <p className="text-2xl font-black text-slate-800 dark:text-white mt-2">
            {latestReading ? `${latestReading.soil_moisture}%` : '38.4%'}
          </p>
          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold mt-1">{t.optimalHydration}</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
            <span>{t.rainProbability}</span>
            <CloudRain className="w-4 h-4 text-sky-500" />
          </div>
          <p className="text-2xl font-black text-sky-600 dark:text-sky-400 mt-2">
            {latestWeather ? `${latestWeather.rain_probability}%` : '15.0%'}
          </p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium mt-1">{t.clearSkies}</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
            <span>{t.airTemp}</span>
            <Thermometer className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-2">
            {latestWeather ? `${latestWeather.temperature}°C` : '27.4°C'}
          </p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium mt-1">
            {t.humidity}: {latestWeather ? `${latestWeather.humidity}%` : '48%'}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
            <span>{t.cropAndKc}</span>
            <Sprout className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-sm font-black text-slate-800 dark:text-white mt-2 truncate">
            {currentField?.crops?.[0]?.crop_type || 'Wheat'}
          </p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium mt-1">
            Kc: <strong className="text-emerald-600 dark:text-emerald-400">{currentField?.crops?.[0]?.kc_factor || 1.15}</strong>
          </p>
        </div>
      </div>

      {/* Interactive Farmer What-If Tool */}
      <FarmerWhatIfSimulator onSimulate={handleSimulate} loading={mlLoading} />

      {/* Model Performance Card */}
      <MLModelPerformanceCard modelInfo={modelInfo} loading={loading} />
    </div>
  );
}
