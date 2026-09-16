'use client';

import React, { useState } from 'react';
import { ScheduleResponse } from '@/types';

interface AIRecommendationCardProps {
  schedule: ScheduleResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function AIRecommendationCard({
  schedule,
  loading,
  onRefresh,
}: AIRecommendationCardProps) {
  const [dispatching, setDispatching] = useState(false);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);
  const [unitMode, setUnitMode] = useState<'liters' | 'time'>('liters');

  const handleDispatch = async () => {
    if (!schedule) return;
    setDispatching(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    setDispatching(false);
    setDispatchSuccess(true);
    setTimeout(() => setDispatchSuccess(false), 4000);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm animate-pulse space-y-4">
        <div className="h-4 bg-slate-200 rounded w-1/3"></div>
        <div className="h-10 bg-slate-200 rounded w-1/2"></div>
        <div className="h-20 bg-slate-100 rounded-xl"></div>
      </div>
    );
  }

  if (!schedule) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center py-8">
        <div className="text-4xl mb-2">🌾</div>
        <h3 className="text-lg font-bold text-slate-800">Smart Farmer Assistant</h3>
        <p className="text-sm text-slate-500 max-w-sm mt-1 mb-4">
          Select a crop field to get instant AI recommendations for watering your crops.
        </p>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded-xl shadow transition-all"
        >
          Check Field Moisture & Get Guidance
        </button>
      </div>
    );
  }

  const isDispatch = schedule.irrigation_required && !schedule.rain_postponed;
  const volLiters = schedule.predicted_volume_liters || schedule.recommended_volume_liters || 0;
  const durationText = schedule.pump_duration_display || `${schedule.recommended_duration_minutes || 45} mins`;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all hover:shadow-md">
      {/* Top Header Banner for Farmers */}
      <div
        className={`px-6 py-3.5 flex flex-wrap items-center justify-between gap-2 text-sm font-bold tracking-wide ${
          schedule.rain_postponed
            ? 'bg-amber-500 text-white'
            : isDispatch
            ? 'bg-emerald-600 text-white'
            : 'bg-teal-700 text-white'
        }`}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">
            {schedule.rain_postponed ? '🌧️' : isDispatch ? '💧' : '🌱'}
          </span>
          <span>
            {schedule.action_badge ||
              (schedule.rain_postponed
                ? 'RAIN EXPECTED — HOLD WATERING'
                : isDispatch
                ? 'IRRIGATION RECOMMENDED TODAY'
                : 'SOIL MOISTURE OPTIMAL — NO WATER NEEDED')}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="bg-white/20 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            Status: {schedule.soil_health_status || (isDispatch ? 'Needs Irrigation' : 'Optimal Soil')}
          </span>
        </div>
      </div>

      {/* Main Body */}
      <div className="p-6 space-y-5">
        {/* Direct Farmer Advice Banner */}
        <div className="bg-emerald-50/80 border border-emerald-100 rounded-2xl p-4 space-y-1">
          <div className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
            <span>📢</span> Direct Guidance for Farmer
          </div>
          <p className="text-sm font-medium text-slate-800 leading-relaxed">
            {schedule.farmer_summary || schedule.reason}
          </p>
        </div>

        {/* Highlight Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Action Card */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <div className="text-xs font-semibold text-slate-500 mb-1">Recommended Action</div>
            <div className={`text-lg font-black ${isDispatch ? 'text-emerald-700' : 'text-slate-800'}`}>
              {isDispatch ? 'START WATER PUMP' : 'PAUSE PUMP'}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              AI Confidence: {(schedule.confidence_score * 100).toFixed(0)}%
            </div>
          </div>

          {/* Target Water Quantity / Runtime */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <div className="flex items-center justify-between mb-1">
              <div className="text-xs font-semibold text-slate-500">Water Needed</div>
              <button
                onClick={() => setUnitMode(unitMode === 'liters' ? 'time' : 'liters')}
                className="text-[11px] text-emerald-700 hover:underline font-bold"
              >
                Switch to {unitMode === 'liters' ? 'Runtime' : 'Liters'}
              </button>
            </div>
            <div className="text-lg font-black text-blue-600">
              {unitMode === 'liters'
                ? `${volLiters.toLocaleString()} Liters`
                : durationText}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {unitMode === 'liters' ? `Pump Runtime: ${durationText}` : `Volume: ${volLiters.toLocaleString()} L`}
            </div>
          </div>

          {/* Optimal Watering Window */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <div className="text-xs font-semibold text-slate-500 mb-1">Best Time Window</div>
            <div className="text-lg font-black text-purple-700">
              {schedule.recommended_start_time
                ? new Date(schedule.recommended_start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : '6:00 AM (Morning)'}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Minimizes Sun Evaporation
            </div>
          </div>
        </div>

        {/* Smart Water Saver Tip */}
        <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-3.5 flex items-start gap-2.5 text-xs text-amber-900">
          <span className="text-base leading-none">💡</span>
          <div className="leading-normal">
            {schedule.water_saving_tip ||
              'Watering during early morning hours (6 AM - 8 AM) reduces evaporation loss by up to 25% compared to afternoon heat.'}
          </div>
        </div>

        {/* Bottom Action Control Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-xs text-slate-400">
            Updated: {schedule.generated_at ? new Date(schedule.generated_at).toLocaleTimeString() : new Date().toLocaleTimeString()}
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onRefresh}
              className="px-3.5 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all flex items-center gap-1.5"
            >
              <span>🔄</span> Refresh Check
            </button>

            <button
              onClick={handleDispatch}
              disabled={dispatching || !isDispatch}
              className={`px-5 py-2.5 text-xs font-bold rounded-xl text-white shadow-sm transition-all flex items-center justify-center gap-2 w-full sm:w-auto ${
                !isDispatch
                  ? 'bg-slate-300 cursor-not-allowed'
                  : dispatchSuccess
                  ? 'bg-emerald-600'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
            >
              {dispatching ? (
                <><span>⏳</span> Dispatching Pump...</>
              ) : dispatchSuccess ? (
                <><span>✅</span> Pump Started Successfully!</>
              ) : (
                <><span>⚡</span> Start Water Pump Now</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
