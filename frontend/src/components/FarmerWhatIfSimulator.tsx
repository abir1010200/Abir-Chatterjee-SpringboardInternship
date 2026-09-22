'use client';

import React, { useState } from 'react';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { Sliders, RefreshCw, Play, Volume2, Sparkles } from 'lucide-react';

interface FarmerWhatIfSimulatorProps {
  onSimulate: (params: {
    soil_moisture: number;
    temperature: number;
    humidity: number;
    rain_probability: number;
  }) => void;
  loading: boolean;
}

export default function FarmerWhatIfSimulator({ onSimulate, loading }: FarmerWhatIfSimulatorProps) {
  const { t, speakText } = useKrishiPals();
  const [moisture, setMoisture] = useState(30.0);
  const [temp, setTemp] = useState(32.0);
  const [humidity, setHumidity] = useState(40.0);
  const [rainProb, setRainProb] = useState(10.0);

  const handleRunSimulation = () => {
    onSimulate({
      soil_moisture: moisture,
      temperature: temp,
      humidity: humidity,
      rain_probability: rainProb,
    });
    speakText(`Running simulation for ${moisture}% soil moisture and ${temp}°C temperature.`);
  };

  const handleReset = () => {
    setMoisture(38.4);
    setTemp(27.4);
    setHumidity(48.0);
    setRainProb(15.0);
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 flex items-center justify-center font-bold">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-black text-sm text-slate-900 dark:text-white">
              {t.whatIfSimulatorTitle}
            </h3>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
              Adjust sliders to test how AI water predictions change under heatwaves or dry spells
            </p>
          </div>
        </div>

        <button
          onClick={handleReset}
          className="text-[11px] font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 flex items-center gap-1"
        >
          <RefreshCw className="w-3 h-3" />
          <span>{t.resetDefaults}</span>
        </button>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Soil Moisture Slider */}
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
            <span>💧 Soil Moisture (%)</span>
            <span className="text-blue-600 dark:text-blue-400 font-black">{moisture}%</span>
          </div>
          <input
            type="range"
            min="10"
            max="80"
            step="1"
            value={moisture}
            onChange={(e) => setMoisture(parseFloat(e.target.value))}
            className="w-full accent-blue-600 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400">
            <span>Dry (10%)</span>
            <span>Optimal (40%)</span>
            <span>Wet (80%)</span>
          </div>
        </div>

        {/* Temperature Slider */}
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
            <span>🌡️ Temperature (°C)</span>
            <span className="text-amber-600 dark:text-amber-400 font-black">{temp}°C</span>
          </div>
          <input
            type="range"
            min="15"
            max="45"
            step="0.5"
            value={temp}
            onChange={(e) => setTemp(parseFloat(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400">
            <span>Cool (15°C)</span>
            <span>Normal (28°C)</span>
            <span>Heatwave (45°C)</span>
          </div>
        </div>

        {/* Humidity Slider */}
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
            <span>💨 Air Humidity (%)</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-black">{humidity}%</span>
          </div>
          <input
            type="range"
            min="15"
            max="95"
            step="1"
            value={humidity}
            onChange={(e) => setHumidity(parseFloat(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400">
            <span>Arid (15%)</span>
            <span>Humid (95%)</span>
          </div>
        </div>

        {/* Rain Probability Slider */}
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
            <span>🌧️ Rain Forecast (%)</span>
            <span className="text-sky-600 dark:text-sky-400 font-black">{rainProb}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={rainProb}
            onChange={(e) => setRainProb(parseFloat(e.target.value))}
            className="w-full accent-sky-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400">
            <span>No Rain (0%)</span>
            <span>Heavy Rain (100%)</span>
          </div>
        </div>
      </div>

      {/* Execute Button */}
      <button
        onClick={handleRunSimulation}
        disabled={loading}
        className="w-full py-3 bg-gradient-to-r from-purple-700 via-indigo-700 to-emerald-700 hover:from-purple-800 hover:to-emerald-800 text-white font-extrabold text-xs rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2"
      >
        {loading ? (
          <><span>⏳</span> Running Physics AI Engine...</>
        ) : (
          <><Sparkles className="w-4 h-4 text-purple-200" /> {t.simulateScenario}</>
        )}
      </button>
    </div>
  );
}
