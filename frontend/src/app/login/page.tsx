'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import {
  Lock,
  Mail,
  UserCheck,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Volume2,
  Phone,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { t, login, speakText, currentUser, isAuthenticated } = useKrishiPals();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier || !password) {
      setErrorMsg('Please enter your mobile number or email and password.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const result = await login(identifier, password);
    setLoading(false);

    if (result.success) {
      setSuccessMsg(result.message || 'Login successful!');
      speakText(`Welcome back ${result.farmer?.name || 'Farmer Friend'}! Accessing your farm dashboard.`);
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } else {
      setErrorMsg(result.message || 'Invalid credentials. Please try again.');
      speakText('Sign in failed. Please check your credentials.');
    }
  };

  const handleDemoLogin = async (email: string) => {
    setIdentifier(email);
    setPassword('krishi123');
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const result = await login(email, 'krishi123');
    setLoading(false);

    if (result.success) {
      setSuccessMsg(`Logged in as ${result.farmer?.name}! Redirecting...`);
      speakText(`Logged in as ${result.farmer?.name}. Opening telemetry dashboard.`);
      setTimeout(() => {
        router.push('/');
      }, 900);
    } else {
      setErrorMsg(result.message || 'Demo login failed.');
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6 pt-2 pb-8 animate-in fade-in duration-300">
      {/* Brand Header Banner */}
      <div className="bg-gradient-to-br from-emerald-950 via-teal-900 to-slate-950 rounded-3xl p-6 text-white shadow-2xl relative overflow-hidden border border-emerald-500/30 text-center">
        <div className="absolute -right-10 -bottom-10 w-44 h-44 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="w-14 h-14 bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 rounded-2xl mx-auto shadow-xl mb-3">
          <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-3xl">
            🌾
          </div>
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[11px] font-extrabold rounded-full mb-2">
          <Sparkles className="w-3 h-3 text-emerald-400" />
          <span>KrishiPals Farmer Portal</span>
        </div>

        <h1 className="text-2xl font-black tracking-tight text-white">{t.loginTitle}</h1>
        <p className="text-xs text-emerald-200/90 mt-1 max-w-xs mx-auto font-medium leading-relaxed">
          {t.loginSubtitle}
        </p>

        <button
          type="button"
          onClick={() => speakText('Farmer Sign In. Please enter your email or registered phone number, and password, or tap one of the quick demo farmer accounts.')}
          className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-300 hover:text-emerald-100 bg-emerald-900/60 px-3 py-1 rounded-xl border border-emerald-700/50 transition-all"
        >
          <Volume2 className="w-3.5 h-3.5" />
          <span>Hear Instructions</span>
        </button>
      </div>

      {/* Feedback Alerts */}
      {errorMsg && (
        <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200 p-3.5 rounded-2xl text-xs flex items-center gap-2.5 shadow-sm">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span className="font-medium">{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 p-3.5 rounded-2xl text-xs flex items-center gap-2.5 shadow-sm">
          <CheckCircle className="w-4 h-4 shrink-0 text-emerald-600" />
          <span className="font-bold">{successMsg}</span>
        </div>
      )}

      {/* Main Login Card */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-xl space-y-5">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Identifier Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>{t.enterEmailOrPhone}</span>
            </label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="e.g. rajesh.patel@agrofarm.io or +91-98765-43210"
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs font-medium text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
              required
            />
          </div>

          {/* Password Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>{t.enterPassword}</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password (e.g. krishi123)"
                className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs font-medium text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 pr-10 transition-all"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember Me */}
          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-2 cursor-pointer text-slate-600 dark:text-slate-400 font-medium">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 rounded-md"
              />
              <span>{t.rememberMe}</span>
            </label>
            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold cursor-pointer">
              PIN / Password Help
            </span>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold text-xs rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <span>{t.login}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>

        {/* 1-Click Demo Farmer Accounts */}
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2.5">
          <div className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400 text-center flex items-center justify-center gap-2">
            <span className="h-px bg-slate-200 dark:bg-slate-800 flex-1"></span>
            <span>{t.quickDemoLogin}</span>
            <span className="h-px bg-slate-200 dark:bg-slate-800 flex-1"></span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleDemoLogin('rajesh.patel@agrofarm.io')}
              className="text-left p-3 rounded-2xl bg-emerald-50/70 hover:bg-emerald-100/70 dark:bg-emerald-950/40 dark:hover:bg-emerald-900/50 border border-emerald-200/80 dark:border-emerald-800/60 transition-all group"
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">🌾</span>
                <div>
                  <div className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-emerald-700 dark:group-hover:text-emerald-300 flex items-center gap-1">
                    <span>Rajesh Patel</span>
                    <span className="text-[9px] bg-emerald-200/60 dark:bg-emerald-800 text-emerald-800 dark:text-emerald-200 px-1 rounded">Pune</span>
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                    Wheat Sector (4.5 ha)
                  </div>
                </div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => handleDemoLogin('amit.sharma@farmtech.io')}
              className="text-left p-3 rounded-2xl bg-teal-50/70 hover:bg-teal-100/70 dark:bg-teal-950/40 dark:hover:bg-teal-900/50 border border-teal-200/80 dark:border-teal-800/60 transition-all group"
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">🍅</span>
                <div>
                  <div className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-teal-700 dark:group-hover:text-teal-300 flex items-center gap-1">
                    <span>Amit Sharma</span>
                    <span className="text-[9px] bg-teal-200/60 dark:bg-teal-800 text-teal-800 dark:text-teal-200 px-1 rounded">Nashik</span>
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                    Tomato Sector (2.2 ha)
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="text-center pt-2 text-xs text-slate-500 dark:text-slate-400">
          <span>{t.dontHaveAccount} </span>
          <Link href="/register" className="font-bold text-emerald-600 dark:text-emerald-400 hover:underline">
            {t.registerFarmerAccount}
          </Link>
        </div>
      </div>

      {/* Security Assurance Badge */}
      <div className="flex items-center justify-center gap-2 text-[11px] text-slate-400 text-center">
        <ShieldCheck className="w-4 h-4 text-emerald-500" />
        <span>Secured with physics-informed AI credentials & PBKDF2 encryption</span>
      </div>
    </div>
  );
}
