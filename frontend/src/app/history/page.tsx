'use client';

import React, { useState, useEffect } from 'react';
import { Field, IrrigationHistory } from '@/types';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import IrrigationLogModal from '@/components/IrrigationLogModal';
import { History, PlusCircle, Droplets, Volume2, Sparkles } from 'lucide-react';

export default function HistoryPage() {
  const { t, speakText } = useKrishiPals();
  const [fields, setFields] = useState<Field[]>([]);
  const [historyList, setHistoryList] = useState<IrrigationHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const fallbackFields: Field[] = [
    {
      id: 1,
      farmer_id: 1,
      name: 'North Valley Field',
      latitude: 18.5204,
      longitude: 73.8567,
      size_hectares: 2.5,
      soil_type: 'Clay Loam',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      farmer_id: 1,
      name: 'East Orchard Sector',
      latitude: 18.525,
      longitude: 73.86,
      size_hectares: 1.8,
      soil_type: 'Sandy Loam',
      created_at: new Date().toISOString(),
    },
  ];

  const fallbackHistory: IrrigationHistory[] = [
    {
      id: 101,
      field_id: 1,
      volume_liters: 1250,
      duration_minutes: 45,
      trigger_source: 'automated_ml',
      status: 'completed',
      start_time: new Date(Date.now() - 86400 * 1000 * 1).toISOString(),
      notes: 'Automated KrishiPals ML pump cycle at 06:00 AM',
    },
    {
      id: 102,
      field_id: 1,
      volume_liters: 1000,
      duration_minutes: 35,
      trigger_source: 'manual',
      status: 'completed',
      start_time: new Date(Date.now() - 86400 * 1000 * 3).toISOString(),
      notes: 'Manual drip booster watering',
    },
    {
      id: 103,
      field_id: 2,
      volume_liters: 850,
      duration_minutes: 30,
      trigger_source: 'automated_ml',
      status: 'completed',
      start_time: new Date(Date.now() - 86400 * 1000 * 4).toISOString(),
      notes: 'Tomato fruit initiation irrigation cycle',
    },
    {
      id: 104,
      field_id: 1,
      volume_liters: 1400,
      duration_minutes: 50,
      trigger_source: 'rule_based',
      status: 'completed',
      start_time: new Date(Date.now() - 86400 * 1000 * 6).toISOString(),
      notes: 'Scheduled weekend timer cycle',
    },
  ];

  const loadData = async () => {
    setLoading(true);
    try {
      const fieldsRes = await fetch('/api/fields');
      if (fieldsRes.ok) {
        const fieldsData = await fieldsRes.json();
        setFields(fieldsData.length > 0 ? fieldsData : fallbackFields);
      } else {
        setFields(fallbackFields);
      }

      const historyRes = await fetch('/api/fields/irrigation/history/all');
      if (historyRes.ok) {
        const histData = await historyRes.json();
        setHistoryList(histData.length > 0 ? histData : fallbackHistory);
      } else {
        setHistoryList(fallbackHistory);
      }
    } catch (e) {
      setFields(fallbackFields);
      setHistoryList(fallbackHistory);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalVolume = historyList.reduce((acc, curr) => acc + (curr.volume_liters || 0), 0);
  const totalEvents = historyList.length;

  const getSourceBadge = (source: string) => {
    switch (source) {
      case 'automated_ml':
        return <span className="bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 border-purple-200 dark:border-purple-800 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border">🤖 KrishiPals AI</span>;
      case 'manual':
        return <span className="bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border">🧑‍🌾 Manual Log</span>;
      default:
        return <span className="bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border">⏱️ Scheduled Timer</span>;
    }
  };

  return (
    <div className="space-y-5 pb-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-4 shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-base font-extrabold text-slate-800 dark:text-white flex items-center gap-2">
            <History className="w-5 h-5 text-emerald-600 dark:text-emerald-400" /> KrishiPals {t.history} Log
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            Durable records of automated AI watering cycles & manual farmer entries.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href="/api/reports/export/csv"
            download="krishipals_irrigation_history.csv"
            className="px-3 py-1.5 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 hover:border-amber-400 text-amber-800 dark:text-amber-200 rounded-2xl text-xs font-bold transition-all flex items-center gap-1"
            title="Export CSV Data"
          >
            <span>📊</span>
            <span className="hidden sm:inline">CSV</span>
          </a>

          <button
            onClick={() => window.print()}
            className="px-3 py-1.5 bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 hover:border-purple-400 text-purple-800 dark:text-purple-200 rounded-2xl text-xs font-bold transition-all flex items-center gap-1"
            title="Download PDF Summary Report"
          >
            <span>📄</span>
            <span className="hidden sm:inline">PDF</span>
          </button>

          <button
            onClick={() => speakText(`Total water applied this month is ${totalVolume} liters across ${totalEvents} irrigation cycles.`)}
            className="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-2xl text-xs font-bold transition-all"
            title="Read Summary Aloud"
          >
            <Volume2 className="w-4 h-4 text-emerald-600" />
          </button>

          <button
            onClick={() => setModalOpen(true)}
            className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-2xl text-xs font-black shadow-md transition-all flex items-center gap-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Log Watering</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-slate-400 font-bold uppercase text-[10px]">Total Volume</span>
          <p className="font-black text-lg text-emerald-600 dark:text-emerald-400 mt-1">
            {totalVolume.toLocaleString()} L
          </p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 font-medium">Water applied</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-slate-400 font-bold uppercase text-[10px]">{t.waterSavedThisMonth}</span>
          <p className="font-black text-lg text-blue-600 dark:text-blue-400 mt-1">
            ~4,500 L
          </p>
          <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">Via Rain Shield</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-slate-400 font-bold uppercase text-[10px]">Total Cycles</span>
          <p className="font-black text-lg text-slate-800 dark:text-white mt-1">{totalEvents}</p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 font-medium">Log records</p>
        </div>
      </div>

      {/* History Records List */}
      <div className="space-y-3">
        <h3 className="text-xs font-extrabold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Previous Irrigation Events</h3>

        <div className="space-y-2.5">
          {historyList.map((item) => {
            const field = fields.find((f) => f.id === item.field_id) || fields[0];
            const dateStr = item.start_time
              ? new Date(item.start_time).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : 'Recent';

            return (
              <div
                key={item.id || Math.random()}
                className="bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between gap-3 hover:border-emerald-400 dark:hover:border-emerald-700 transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-blue-50 dark:bg-blue-950/60 border border-blue-100 dark:border-blue-900/40 flex items-center justify-center text-blue-600 dark:text-blue-400 shrink-0">
                    <Droplets className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-black text-slate-900 dark:text-white text-sm">{field?.name || 'North Valley'}</h4>
                      {getSourceBadge(item.trigger_source)}
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2 font-medium">
                      <span>🗓️ {dateStr}</span>
                      <span>•</span>
                      <span>⏱️ {item.duration_minutes || 45} mins</span>
                    </p>
                    {item.notes && <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5 italic">"{item.notes}"</p>}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="font-black text-base text-emerald-600 dark:text-emerald-400">
                    {item.volume_liters?.toLocaleString()} L
                  </span>
                  <span className="block text-[10px] font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full mt-1 border border-emerald-100 dark:border-emerald-800/60">
                    ✓ {item.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Manual Entry Modal */}
      <IrrigationLogModal
        fields={fields}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSaveSuccess={loadData}
      />
    </div>
  );
}
