'use client';

import React from 'react';
import { Field } from '@/types';
import { Sprout, MapPin, Droplets, Thermometer, CloudRain, CheckCircle2 } from 'lucide-react';

interface FieldSummaryCardProps {
  field: Field;
  soilMoisture: number;
  temperature: number;
  rainProbability: number;
  isSelected: boolean;
  onSelect: () => void;
}

export default function FieldSummaryCard({
  field,
  soilMoisture,
  temperature,
  rainProbability,
  isSelected,
  onSelect,
}: FieldSummaryCardProps) {
  const activeCrop = field.crops && field.crops.length > 0 ? field.crops[0] : null;

  // Compute hydration visual color
  const getMoistureColor = (val: number) => {
    if (val < 30) return { text: 'text-rose-600 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/40', border: 'border-rose-200 dark:border-rose-900', label: 'Dry' };
    if (val <= 60) return { text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/40', border: 'border-emerald-200 dark:border-emerald-900', label: 'Optimal' };
    return { text: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-950/40', border: 'border-blue-200 dark:border-blue-900', label: 'Saturated' };
  };

  const moistureStyle = getMoistureColor(soilMoisture);

  return (
    <div
      onClick={onSelect}
      className={`rounded-3xl p-4 cursor-pointer transition-all duration-200 border relative overflow-hidden ${
        isSelected
          ? 'bg-white dark:bg-slate-900 border-emerald-500 dark:border-emerald-400 shadow-xl ring-2 ring-emerald-500/30'
          : 'bg-white/80 dark:bg-slate-900/80 border-slate-200 dark:border-slate-800 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 hover:shadow-md'
      }`}
    >
      {isSelected && (
        <div className="absolute top-3 right-3 text-emerald-500">
          <CheckCircle2 className="w-5 h-5 fill-emerald-100 dark:fill-emerald-900" />
        </div>
      )}

      {/* Header Info */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-md text-lg shrink-0">
          🌾
        </div>
        <div className="flex-1 min-w-0 pr-6">
          <h3 className="font-extrabold text-sm text-slate-900 dark:text-white truncate">
            {field.name}
          </h3>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-0.5">
            <MapPin className="w-3 h-3 text-emerald-600" />
            <span>{field.size_hectares} Ha • {field.soil_type}</span>
          </p>
        </div>
      </div>

      {/* Active Crop Tag */}
      {activeCrop && (
        <div className="mt-3 flex items-center justify-between bg-slate-50 dark:bg-slate-800/80 px-3 py-1.5 rounded-xl text-[11px] border border-slate-100 dark:border-slate-700/60">
          <span className="font-bold text-slate-700 dark:text-slate-200 truncate">
            🌱 {activeCrop.crop_type}
          </span>
          <span className="text-[10px] font-extrabold text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/60 px-2 py-0.5 rounded-md shrink-0">
            {activeCrop.growth_stage}
          </span>
        </div>
      )}

      {/* Telemetry Gauge Strip */}
      <div className="grid grid-cols-3 gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 text-center">
        <div className={`p-2 rounded-xl border ${moistureStyle.bg} ${moistureStyle.border}`}>
          <div className="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase">Moisture</div>
          <div className={`text-base font-black ${moistureStyle.text} mt-0.5`}>
            {soilMoisture}%
          </div>
        </div>

        <div className="p-2 rounded-xl border border-amber-100 dark:border-amber-900/40 bg-amber-50/60 dark:bg-amber-950/20">
          <div className="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase">Temp</div>
          <div className="text-base font-black text-amber-600 dark:text-amber-400 mt-0.5">
            {temperature}°C
          </div>
        </div>

        <div className="p-2 rounded-xl border border-sky-100 dark:border-sky-900/40 bg-sky-50/60 dark:bg-sky-950/20">
          <div className="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase">Rain Prob</div>
          <div className="text-base font-black text-sky-600 dark:text-sky-400 mt-0.5">
            {rainProbability}%
          </div>
        </div>
      </div>
    </div>
  );
}
