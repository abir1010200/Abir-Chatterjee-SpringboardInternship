'use client';

import React, { useState } from 'react';

interface FarmerWhatIfSimulatorProps {
  onSimulate: (customParams: {
    soil_moisture: number;
    temperature: number;
    humidity: number;
    rain_probability: number;
  }) => void;
  loading: boolean;
}

export default function FarmerWhatIfSimulator({ onSimulate, loading }: FarmerWhatIfSimulatorProps) {
  const [moisture, setMoisture] = useState<number>(20.0);
  const [temp, setTemp] = useState<number>(32.0);
  const [humidity, setHumidity] = useState<number>(45.0);
  const [rainProb, setRainProb] = useState<number>(10.0);

  const handleApplyPreset = (preset: 'hot' | 'dry' | 'rain' | 'optimal') => {
    if (preset === 'hot') {
      setMoisture(18.0);
      setTemp(40.0);
      setHumidity(30.0);
      setRainProb(5.0);
    } else if (preset === 'dry') {
      setMoisture(12.0);
      setTemp(35.0);
      setHumidity(35.0);
      setRainProb(0.0);
    } else if (preset === 'rain') {
      setMoisture(22.0);
      setTemp(25.0);
      setHumidity(80.0);
      setRainProb(75.0);
    } else {
      setMoisture(32.0);
      setTemp(27.0);
      setHumidity(60.0);
      setRainProb(15.0);
    }
  };

  const handleRunSimulation = () => {
    onSimulate({
      soil_moisture: moisture,
      temperature: temp,
      humidity: humidity,
      rain_probability: rainProb,
    });
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-emerald-50 text-emerald-800 text-xs font-bold rounded-lg mb-1">
            <span>🧪</span> Interactive Farmer What-If Tool
          </div>
          <h3 className="text-base font-bold text-slate-800 tracking-tight">
            Test AI Irrigation Decision Live
          </h3>
        </div>
        <div className="flex items-center gap-1.5 text-xs flex-wrap">
          <span className="text-slate-400">Quick Presets:</span>
          <button
            type="button"
            onClick={() => handleApplyPreset('dry')}
            className="px-2 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 font-semibold rounded-lg border border-amber-200"
          >
            ☀️ Hot & Dry
          </button>
          <button
            type="button"
            onClick={() => handleApplyPreset('rain')}
            className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-800 font-semibold rounded-lg border border-blue-200"
          >
            🌧️ Rain Incoming
          </button>
          <button
            type="button"
            onClick={() => handleApplyPreset('optimal')}
            className="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold rounded-lg border border-emerald-200"
          >
            🌱 Moist Soil
          </button>
        </div>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Soil Moisture Slider */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 space-y-2">
          <div className="flex justify-between items-center text-xs font-bold text-slate-700">
            <span>💧 Soil Moisture</span>
            <span className="text-emerald-700 text-sm">{moisture}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="60"
            step="1"
            value={moisture}
            onChange={(e) => setMoisture(parseFloat(e.target.value))}
            className="w-full accent-emerald-600 cursor-pointer"
          />
          <div className="text-[11px] text-slate-400 flex justify-between">
            <span>5% (Extremely Dry)</span>
            <span>60% (Wet)</span>
          </div>
        </div>

        {/* Temperature Slider */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 space-y-2">
          <div className="flex justify-between items-center text-xs font-bold text-slate-700">
            <span>🌡️ Air Temperature</span>
            <span className="text-amber-700 text-sm">{temp}°C</span>
          </div>
          <input
            type="range"
            min="15"
            max="48"
            step="1"
            value={temp}
            onChange={(e) => setTemp(parseFloat(e.target.value))}
            className="w-full accent-amber-600 cursor-pointer"
          />
          <div className="text-[11px] text-slate-400 flex justify-between">
            <span>15°C (Cool)</span>
            <span>48°C (Extreme Heat)</span>
          </div>
        </div>

        {/* Humidity Slider */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 space-y-2">
          <div className="flex justify-between items-center text-xs font-bold text-slate-700">
            <span>💨 Air Humidity</span>
            <span className="text-blue-700 text-sm">{humidity}%</span>
          </div>
          <input
            type="range"
            min="10"
            max="95"
            step="1"
            value={humidity}
            onChange={(e) => setHumidity(parseFloat(e.target.value))}
            className="w-full accent-blue-600 cursor-pointer"
          />
          <div className="text-[11px] text-slate-400 flex justify-between">
            <span>10% (Dry Air)</span>
            <span>95% (Humid)</span>
          </div>
        </div>

        {/* Rain Probability Slider */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 space-y-2">
          <div className="flex justify-between items-center text-xs font-bold text-slate-700">
            <span>🌧️ Rain Forecast</span>
            <span className="text-purple-700 text-sm">{rainProb}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={rainProb}
            onChange={(e) => setRainProb(parseFloat(e.target.value))}
            className="w-full accent-purple-600 cursor-pointer"
          />
          <div className="text-[11px] text-slate-400 flex justify-between">
            <span>0% (No Rain)</span>
            <span>100% (Heavy Rain)</span>
          </div>
        </div>
      </div>

      {/* Trigger Button */}
      <div className="flex justify-end pt-1">
        <button
          type="button"
          onClick={handleRunSimulation}
          disabled={loading}
          className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-2"
        >
          {loading ? (
            <><span>⏳</span> Calculating ML Prediction...</>
          ) : (
            <><span>🚀</span> Simulate AI Irrigation Decision</>
          )}
        </button>
      </div>
    </div>
  );
}
