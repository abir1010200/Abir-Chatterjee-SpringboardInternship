'use client';

import React, { useState } from 'react';
import { Field } from '@/types';
import { X, Droplets, Clock, FileText, CheckCircle2 } from 'lucide-react';

interface IrrigationLogModalProps {
  fields: Field[];
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess: () => void;
}

export default function IrrigationLogModal({
  fields,
  isOpen,
  onClose,
  onSaveSuccess,
}: IrrigationLogModalProps) {
  const [fieldId, setFieldId] = useState<number>(fields[0]?.id || 1);
  const [volumeLiters, setVolumeLiters] = useState<number>(1000);
  const [durationMinutes, setDurationMinutes] = useState<number>(30);
  const [triggerSource, setTriggerSource] = useState<'manual' | 'automated_ml' | 'rule_based'>('manual');
  const [notes, setNotes] = useState<string>('Manual watering via drip system.');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);

    try {
      const payload = {
        field_id: Number(fieldId),
        volume_liters: Number(volumeLiters),
        duration_minutes: Number(durationMinutes),
        trigger_source: triggerSource,
        status: 'completed',
        notes: notes || 'Manual irrigation log',
        start_time: new Date().toISOString(),
      };

      const res = await fetch('/api/fields/irrigation/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        onSaveSuccess();
        onClose();
      } else {
        const errData = await res.json();
        setErrorMsg(errData.detail || 'Failed to record irrigation event');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Network error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-emerald-800 text-white px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="w-5 h-5 text-emerald-300" />
            <h2 className="font-bold text-base">Record Irrigation Log</h2>
          </div>
          <button
            onClick={onClose}
            className="text-emerald-200 hover:text-white p-1 rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium rounded-xl">
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Select Field */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Target Field</label>
            <select
              value={fieldId}
              onChange={(e) => setFieldId(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 font-medium focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              {fields.map((f) => (
                <option key={f.id} value={f.id}>
                  🌾 {f.name} ({f.size_hectares} ha)
                </option>
              ))}
            </select>
          </div>

          {/* Water Volume */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Water Volume (Liters)
            </label>
            <div className="relative">
              <input
                type="number"
                min="50"
                step="50"
                value={volumeLiters}
                onChange={(e) => setVolumeLiters(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                required
              />
              <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-medium">Liters</span>
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Duration (Minutes)
            </label>
            <div className="relative">
              <input
                type="number"
                min="5"
                max="300"
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                required
              />
              <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-medium">Mins</span>
            </div>
          </div>

          {/* Trigger Source */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Irrigation Mode</label>
            <select
              value={triggerSource}
              onChange={(e) => setTriggerSource(e.target.value as any)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 font-medium focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="manual">🧑‍🌾 Manual Irrigation</option>
              <option value="automated_ml">🤖 Automated ML AI Pump</option>
              <option value="rule_based">⏱️ Scheduled Timer Rule</option>
            </select>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Notes / Remarks</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Morning drip irrigation cycle"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          {/* Submit & Cancel */}
          <div className="pt-2 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              {submitting ? 'Saving...' : 'Save Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
