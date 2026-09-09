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

  const handleDispatch = async () => {
    if (!schedule) return;
    setDispatching(true);
    // Simulate pump trigger call
    await new Promise((resolve) => setTimeout(resolve, 800));
    setDispatching(false);
    setDispatchSuccess(true);
    setTimeout(() => setDispatchSuccess(false), 4000);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm animate-pulse space-y-4">
        <div className="h-4 bg-slate-200 rounded w-1/3"></div>
        <div className="h-8 bg-slate-200 rounded w-1/2"></div>
        <div className="h-16 bg-slate-100 rounded-xl"></div>
      </div>
    );
  }

  if (!schedule) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center py-8">
        <div className="text-4xl mb-2">🤖</div>
        <h3 className="text-lg font-bold text-slate-800">No ML Schedule Available</h3>
        <p className="text-sm text-slate-500 max-w-sm mt-1 mb-4">
          Select an active field to compute real-time moisture deficit and ML-driven pump dispatch.
        </p>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded-xl shadow transition-all"
        >
          Compute Recommendation
        </button>
      </div>
    );
  }

  const isDispatch = schedule.irrigation_required && !schedule.rain_postponed;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all hover:shadow-md">
      {/* Header Accent Bar */}
      <div
        className={`px-6 py-3 flex items-center justify-between text-xs font-semibold uppercase tracking-wider ${
          schedule.rain_postponed
            ? 'bg-amber-500 text-white'
            : isDispatch
            ? 'bg-emerald-600 text-white'
            : 'bg-slate-700 text-white'
        }`}
      >
        <div className="flex items-center gap-2">
          <span>{schedule.rain_postponed ? '🌧️' : isDispatch ? '💧' : '🌱'}</span>
          <span>
            {schedule.rain_postponed
              ? 'Irrigation Postponed (Rain Forecast)'
              : isDispatch
              ? 'Irrigation Recommended'
              : 'Soil Moisture Optimal (Idle)'}
          </span>
        </div>
        <div className="flex items-center gap-1.5 opacity-90">
          <span>Model: {schedule.model_name} (v{schedule.model_version})</span>
        </div>
      </div>

      {/* Main Body */}
      <div className="p-6 space-y-6">
        {/* Top Highlight Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Action Trigger Card */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
            <div className="text-xs font-medium text-slate-500 mb-1">Trigger Recommendation</div>
            <div className={`text-xl font-extrabold ${isDispatch ? 'text-emerald-700' : 'text-slate-800'}`}>
              {isDispatch ? 'DISPATCH PUMP' : 'HOLD / IDLE'}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Confidence Score: {(schedule.confidence_score * 100).toFixed(1)}%
            </div>
          </div>

          {/* Volume Target */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
            <div className="text-xs font-medium text-slate-500 mb-1">Target Water Volume</div>
            <div className="text-xl font-extrabold text-blue-600">
              {(schedule.predicted_volume_liters || schedule.recommended_volume_liters || 0).toLocaleString()} <span className="text-xs font-semibold">Liters</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Duration: {schedule.recommended_duration_minutes} mins
            </div>
          </div>

          {/* Moisture Deficit */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
            <div className="text-xs font-medium text-slate-500 mb-1">Moisture Deficit</div>
            <div className="text-xl font-extrabold text-purple-600">
              {(schedule.moisture_deficit_percent ?? 24.5).toFixed(1)}%
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Target Window: {schedule.recommended_start_time ? new Date(schedule.recommended_start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Optimal Window'}
            </div>
          </div>
        </div>

        {/* Rain Postponed Warning if active */}
        {schedule.rain_postponed && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-amber-800 flex items-start gap-3">
            <span className="text-xl">🌧️</span>
            <div>
              <div className="font-semibold text-sm">Rain Event Shield Active</div>
              <div className="text-xs mt-0.5 opacity-90">
                {schedule.rain_postponed_reason || 'Significant precipitation forecasted within the next 24 hours. Automated dispatch delayed to prevent nutrient runoff.'}
              </div>
            </div>
          </div>
        )}

        {/* Bottom Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="text-xs text-slate-400">
            Generated: {schedule.generated_at ? new Date(schedule.generated_at).toLocaleTimeString() : new Date().toLocaleTimeString()}
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onRefresh}
              className="px-3.5 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all flex items-center gap-1.5"
            >
              <span>🔄</span> Recalculate ML
            </button>

            <button
              onClick={handleDispatch}
              disabled={dispatching || !isDispatch}
              className={`px-4 py-2 text-xs font-semibold rounded-xl text-white shadow transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto ${
                !isDispatch
                  ? 'bg-slate-300 cursor-not-allowed'
                  : dispatchSuccess
                  ? 'bg-green-600'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
            >
              {dispatching ? (
                <><span>⏳</span> Dispatching Valve...</>
              ) : dispatchSuccess ? (
                <><span>✅</span> Valve Dispatched!</>
              ) : (
                <><span>🚀</span> Execute Dispatch</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
