'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { LogOut, CheckCircle, ArrowRight, Shield, Home, UserCheck, AlertTriangle } from 'lucide-react';

export default function LogoutPage() {
  const router = useRouter();
  const { t, logout, currentUser, isAuthenticated, speakText } = useKrishiPals();
  const [loggedOutSuccess, setLoggedOutSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleConfirmLogout = async () => {
    setLoading(true);
    await logout();
    setLoading(false);
    setLoggedOutSuccess(true);
    speakText('You have been safely logged out of KrishiPals. Have a great day.');
  };

  return (
    <div className="max-w-md mx-auto space-y-6 pt-6 pb-12 animate-in fade-in duration-300">
      {loggedOutSuccess ? (
        /* Logout Success State */
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-2xl text-center space-y-5">
          <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-950/60 rounded-3xl mx-auto flex items-center justify-center text-emerald-600 dark:text-emerald-400 shadow-inner">
            <CheckCircle className="w-9 h-9" />
          </div>

          <div className="space-y-1.5">
            <h1 className="text-xl font-black text-slate-900 dark:text-white">
              Safely Signed Out
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
              Your farming session has been terminated safely. Your IoT telemetry and automated irrigation schedules will continue running in the background.
            </p>
          </div>

          <div className="pt-2 flex flex-col gap-2.5">
            <Link
              href="/login"
              className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold text-xs rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <span>{t.login}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/"
              className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-xs rounded-2xl transition-all flex items-center justify-center gap-1.5"
            >
              <Home className="w-4 h-4" />
              <span>Return to Dashboard</span>
            </Link>
          </div>
        </div>
      ) : (
        /* Confirmation State */
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 bg-rose-100 dark:bg-rose-950/50 rounded-3xl mx-auto flex items-center justify-center text-rose-600 dark:text-rose-400 shadow-inner">
            <LogOut className="w-8 h-8 -ml-1" />
          </div>

          <div className="space-y-2">
            <h1 className="text-xl font-black text-slate-900 dark:text-white">
              {t.logoutConfirmTitle}
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto leading-relaxed">
              {t.logoutConfirmSubtitle}
            </p>

            {currentUser && (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 mt-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>{t.loggedInAs}: <strong>{currentUser.name}</strong></span>
              </div>
            )}
          </div>

          <div className="space-y-2.5 pt-2">
            <button
              onClick={handleConfirmLogout}
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-700 hover:to-rose-800 text-white font-extrabold text-xs rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <LogOut className="w-4 h-4" />
                  <span>{t.confirmLogoutBtn}</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => router.back()}
              className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs rounded-2xl transition-all"
            >
              {t.cancelBtn}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
