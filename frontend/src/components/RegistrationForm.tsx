'use client';

import React, { useState } from 'react';
import { FieldRegistrationPayload } from '@/types';

export default function RegistrationForm({ onSuccess }: { onSuccess?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [formData, setFormData] = useState<FieldRegistrationPayload>({
    farmer: {
      name: '',
      email: '',
      phone: '',
      address: '',
    },
    field: {
      name: '',
      latitude: 18.5204,
      longitude: 73.8567,
      size_hectares: 3.5,
      soil_type: 'Clay Loam',
    },
    crop: {
      crop_type: 'Wheat',
      growth_stage: 'Vegetative',
      planted_date: new Date().toISOString().split('T')[0],
      kc_factor: 1.15,
    },
    sensor: {
      sensor_id: 'SEN-FIELD01-01',
      sensor_type: 'soil_moisture',
      model_name: 'SoilOptix-Capacitive-Pro',
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const res = await fetch('/api/fields/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to register field and crop configuration.');
      }

      const data = await res.json();
      setSuccessMsg(`✅ Successfully registered Field ID ${data.field_id} linked to Sensor ${data.sensor_id}!`);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || 'An unexpected error occurred during registration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8 space-y-8">
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-sm font-medium">
          {successMsg}
        </div>
      )}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm font-medium">
          {errorMsg}
        </div>
      )}

      {/* 1. Farmer Profile */}
      <div>
        <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <span>👨‍🌾</span> 1. Farmer Profile
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">Primary owner or manager of the agricultural sector.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Full Name</label>
            <input
              type="text"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="e.g. Ramesh Kumar"
              value={formData.farmer.name}
              onChange={(e) => setFormData({ ...formData, farmer: { ...formData.farmer, name: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="farmer@agrofarm.com"
              value={formData.farmer.email}
              onChange={(e) => setFormData({ ...formData, farmer: { ...formData.farmer, email: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Phone Number</label>
            <input
              type="tel"
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="+91-9876543210"
              value={formData.farmer.phone}
              onChange={(e) => setFormData({ ...formData, farmer: { ...formData.farmer, phone: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Farm Location / Address</label>
            <input
              type="text"
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="Sector 4B, Pune Rural"
              value={formData.farmer.address}
              onChange={(e) => setFormData({ ...formData, farmer: { ...formData.farmer, address: e.target.value } })}
            />
          </div>
        </div>
      </div>

      <hr className="border-slate-100" />

      {/* 2. Field Details */}
      <div>
        <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <span>📍</span> 2. Field & Geolocation Configuration
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">Coordinates are used for hyper-local OpenWeather integration.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Field Name</label>
            <input
              type="text"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="e.g. East Valley Plot A"
              value={formData.field.name}
              onChange={(e) => setFormData({ ...formData, field: { ...formData.field, name: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Latitude</label>
            <input
              type="number"
              step="any"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.field.latitude}
              onChange={(e) => setFormData({ ...formData, field: { ...formData.field, latitude: parseFloat(e.target.value) || 0 } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Longitude</label>
            <input
              type="number"
              step="any"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.field.longitude}
              onChange={(e) => setFormData({ ...formData, field: { ...formData.field, longitude: parseFloat(e.target.value) || 0 } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Size (Hectares)</label>
            <input
              type="number"
              step="0.1"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.field.size_hectares}
              onChange={(e) => setFormData({ ...formData, field: { ...formData.field, size_hectares: parseFloat(e.target.value) || 1 } })}
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-600 mb-1">Soil Type</label>
            <select
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.field.soil_type}
              onChange={(e) => setFormData({ ...formData, field: { ...formData.field, soil_type: e.target.value } })}
            >
              <option value="Clay Loam">Clay Loam (High Retention)</option>
              <option value="Sandy Loam">Sandy Loam (Rapid Drainage)</option>
              <option value="Silty Clay">Silty Clay (Moderate Retention)</option>
              <option value="Loam">Loam (Standard Equilibrium)</option>
              <option value="Peat">Peat (High Organic Matter)</option>
            </select>
          </div>
        </div>
      </div>

      <hr className="border-slate-100" />

      {/* 3. Crop & Growth Stage */}
      <div>
        <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <span>🌱</span> 3. Crop Lifecycle & Water Demand (Kc)
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">Defines the crop coefficient for evapotranspiration estimation.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Crop Type</label>
            <input
              type="text"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              placeholder="e.g. Wheat, Tomato, Maize"
              value={formData.crop.crop_type}
              onChange={(e) => setFormData({ ...formData, crop: { ...formData.crop, crop_type: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Growth Stage</label>
            <select
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.crop.growth_stage}
              onChange={(e) => setFormData({ ...formData, crop: { ...formData.crop, growth_stage: e.target.value } })}
            >
              <option value="Initial">Initial / Germination (Kc ~0.4 - 0.7)</option>
              <option value="Vegetative">Vegetative (Kc ~0.8 - 1.15)</option>
              <option value="Flowering">Flowering / Fruit Formation (Kc ~1.15 - 1.25)</option>
              <option value="Mid-Season">Mid-Season Peak (Kc ~1.2)</option>
              <option value="Late-Season">Late-Season / Ripening (Kc ~0.65 - 0.8)</option>
              <option value="Harvest">Harvest Ready (Kc ~0.3)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Kc Coefficient</label>
            <input
              type="number"
              step="0.05"
              min="0.2"
              max="2.0"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.crop.kc_factor}
              onChange={(e) => setFormData({ ...formData, crop: { ...formData.crop, kc_factor: parseFloat(e.target.value) || 1.0 } })}
            />
          </div>
        </div>
      </div>

      <hr className="border-slate-100" />

      {/* 4. IoT Sensor Hardware Link */}
      <div>
        <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <span>📡</span> 4. IoT Sensor Hardware Association
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">Links incoming MQTT/REST telemetry to this registered field.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Sensor Identifier (Hardware ID)</label>
            <input
              type="text"
              required
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600 font-mono"
              placeholder="e.g. SEN-WHEAT-01"
              value={formData.sensor.sensor_id}
              onChange={(e) => setFormData({ ...formData, sensor: { ...formData.sensor, sensor_id: e.target.value } })}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Sensor Model</label>
            <input
              type="text"
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              value={formData.sensor.model_name}
              onChange={(e) => setFormData({ ...formData, sensor: { ...formData.sensor, model_name: e.target.value } })}
            />
          </div>
        </div>
      </div>

      <div className="pt-4 flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-medium rounded-xl shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
        >
          {loading ? 'Registering Field...' : 'Complete Field & Crop Registration'}
        </button>
      </div>
    </form>
  );
}
