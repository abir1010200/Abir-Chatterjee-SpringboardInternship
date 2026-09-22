'use client';

import React, { useState } from 'react';
import { ScheduleResponse } from '@/types';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { Volume2, Play, CheckCircle2, Clock, Droplets, Sparkles, RefreshCw, Zap } from 'lucide-react';

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
  const { t, speakText, isSpeaking, stopSpeaking } = useKrishiPals();
  const [dispatching, setDispatching] = useState(false);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);
  const [unitMode, setUnitMode] = useState<'liters' | 'time'>('liters');

  const handleDispatch = async () => {
    if (!schedule) return;
    setDispatching(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    setDispatching(false);
    setDispatchSuccess(true);
    speakText('Water pump started successfully. Dispatching water volume now.');
    setTimeout(() => setDispatchSuccess(false), 4000);
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg animate-pulse space-y-4">
        <div className="h-5 bg-slate-200 dark:bg-slate-800 rounded-xl w-1/3"></div>
        <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-2xl w-1/2"></div>
        <div className="h-24 bg-slate-100 dark:bg-slate-800/60 rounded-2xl"></div>
      </div>
    );
  }

  if (!schedule) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col items-center justify-center text-center py-8">
        <div className="text-5xl mb-3 animate-float">🌾</div>
        <h3 className="text-lg font-black text-slate-800 dark:text-white">KrishiPals AI Assistant</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-1 mb-4">
          Select a crop field to get instant AI recommendations for watering your crops.
        </p>
        <button
          onClick={onRefresh}
          className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold text-xs rounded-2xl shadow-lg transition-all"
        >
          Check Field Moisture & Get Guidance
        </button>
      </div>
    );
  }

  const isDispatch = schedule.irrigation_required && !schedule.rain_postponed;
  const volLiters = schedule.predicted_volume_liters || schedule.recommended_volume_liters || 0;
  const durationText = schedule.pump_duration_display || `${schedule.recommended_duration_minutes || 45} mins`;

  const summaryToSpeak = `${schedule.rain_postponed ? 'Rain forecast detected.' : 'Irrigation recommended.'} ${schedule.farmer_summary || schedule.reason}`;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden transition-all hover:shadow-2xl">
      {/* Top Header Banner for Farmers */}
      <div
        className={`px-6 py-4 flex flex-wrap items-center justify-between gap-3 text-xs sm:text-sm font-black tracking-wide ${
          schedule.rain_postponed
            ? 'bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-600 text-slate-950'
            : isDispatch
            ? 'bg-gradient-to-r from-emerald-700 via-teal-700 to-emerald-800 text-white'
            : 'bg-gradient-to-r from-teal-800 to-slate-900 text-white'
        }`}
      >
        <div className="flex items-center gap-2.5">
          <span className="text-xl">
            {schedule.rain_postponed ? '🌧️' : isDispatch ? '💧' : '🌱'}
          </span>
          <span>
            {schedule.action_badge ||
              (schedule.rain_postponed
                ? t.rainShieldActive
                : isDispatch
                ? t.actionRecommended
                : t.optimalHydration)}
          </span>
        </div>

        {/* Audio Speaker Readout Button */}
        <button
          onClick={() => (isSpeaking ? stopSpeaking() : speakText(summaryToSpeak))}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black shadow-xs transition-all ${
            isSpeaking
              ? 'bg-amber-400 text-slate-950 animate-pulse'
              : 'bg-white/20 hover:bg-white/30 text-white border border-white/30'
          }`}
          title="Listen in Audio (Native Language)"
        >
          <Volume2 className="w-3.5 h-3.5" />
          <span>{isSpeaking ? 'Pause Audio' : t.listenAudio}</span>
        </button>
      </div>

      {/* Main Body */}
      <div className="p-6 space-y-5">
        {/* Direct Farmer Advice Banner */}
        <div className="bg-emerald-50/90 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl p-4 space-y-1.5 shadow-inner">
          <div className="text-[11px] font-extrabold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> KrishiPals Guidance
            </span>
            <span className="text-[10px] bg-emerald-200 dark:bg-emerald-900 text-emerald-900 dark:text-emerald-100 px-2 py-0.5 rounded-full font-bold">
              AI Confidence: {(schedule.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 leading-relaxed">
            {schedule.farmer_summary || schedule.reason}
          </p>
        </div>

        {/* Highlight Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Action Card */}
          <div className="bg-slate-50 dark:bg-slate-800/60 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-700/60">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
              Recommended Action
            </div>
            <div className={`text-lg font-black ${isDispatch ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-800 dark:text-white'}`}>
              {isDispatch ? 'START WATER PUMP' : 'PAUSE PUMP'}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-semibold">
              Status: {schedule.soil_health_status || 'Hydrated'}
            </div>
          </div>

          {/* Target Water Quantity / Runtime */}
          <div className="bg-slate-50 dark:bg-slate-800/60 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-700/60">
            <div className="flex items-center justify-between mb-1">
              <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Water Needed
              </div>
              <button
                onClick={() => setUnitMode(unitMode === 'liters' ? 'time' : 'liters')}
                className="text-[10px] text-emerald-600 dark:text-emerald-400 hover:underline font-extrabold"
              >
                Switch to {unitMode === 'liters' ? 'Runtime' : 'Liters'}
              </button>
            </div>
            <div className="text-lg font-black text-blue-600 dark:text-blue-400">
              {unitMode === 'liters'
                ? `${volLiters.toLocaleString()} Liters`
                : durationText}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-semibold">
              {unitMode === 'liters' ? `Pump Runtime: ${durationText}` : `Volume: ${volLiters.toLocaleString()} L`}
            </div>
          </div>

          {/* Optimal Window */}
          <div className="bg-slate-50 dark:bg-slate-800/60 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-700/60">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
              {t.recommendedTime}
            </div>
            <div className="text-lg font-black text-purple-600 dark:text-purple-400" suppressHydrationWarning>
              {schedule.recommended_start_time
                ? new Date(schedule.recommended_start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : '06:00 AM'}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-semibold">
              {t.morningCoolWindow}
            </div>
          </div>
        </div>

        {/* Smart Saver Tip */}
        <div className="bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/50 rounded-2xl p-3.5 flex items-start gap-2.5 text-xs text-amber-900 dark:text-amber-200">
          <span className="text-base leading-none">💡</span>
          <div className="leading-normal font-medium">
            {schedule.water_saving_tip ||
              'Watering during early morning hours (6 AM - 8 AM) reduces evaporation loss by up to 25% compared to afternoon heat.'}
          </div>
        </div>

        {/* Bottom Action Control Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium" suppressHydrationWarning>
            Generated: {schedule.generated_at ? new Date(schedule.generated_at).toLocaleTimeString() : 'Recently'}
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onRefresh}
              className="px-3.5 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all flex items-center justify-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              <span>Refresh Check</span>
            </button>

            <button
              onClick={handleDispatch}
              disabled={dispatching || !isDispatch}
              className={`px-6 py-3 text-xs font-extrabold rounded-2xl text-white shadow-lg transition-all flex items-center justify-center gap-2 w-full sm:w-auto ${
                !isDispatch
                  ? 'bg-slate-300 dark:bg-slate-800 text-slate-500 cursor-not-allowed shadow-none'
                  : dispatchSuccess
                  ? 'bg-emerald-600 dark:bg-emerald-500'
                  : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700'
              }`}
            >
              {dispatching ? (
                <><span>⏳</span> {t.dispatchingPump}</>
              ) : dispatchSuccess ? (
                <><CheckCircle2 className="w-4 h-4 text-white" /> {t.pumpStarted}</>
              ) : (
                <><Zap className="w-4 h-4 fill-current" /> {t.startPumpNow}</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
