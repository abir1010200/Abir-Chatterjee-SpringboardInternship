'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Field } from '@/types';
import { useKrishiPals, SupportedLanguage, FontSizeOption } from '@/context/KrishiPalsContext';
import NotificationCenter from '@/components/NotificationCenter';
import { Wifi, WifiOff, Download, User, Sprout, Globe, Sun, Moon, Type, Volume2, LogIn, LogOut } from 'lucide-react';

interface HeaderProps {
  fields?: Field[];
  selectedFieldId?: number | null;
  onSelectField?: (fieldId: number) => void;
}

export default function Header({ fields = [], selectedFieldId, onSelectField }: HeaderProps) {
  const { language, setLanguage, fontSize, setFontSize, theme, setTheme, setIsAssistantOpen, speakText, currentUser, isAuthenticated } = useKrishiPals();
  const [mounted, setMounted] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showInstallBtn, setShowInstallBtn] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsOnline(navigator.onLine);
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const handleBeforeInstallPrompt = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallBtn(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setShowInstallBtn(false);
    }
    setDeferredPrompt(null);
  };

  const languagesList: Array<{ code: SupportedLanguage; label: string; flag: string }> = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'hi', label: 'हिंदी', flag: '🇮🇳' },
    { code: 'kn', label: 'ಕನ್ನಡ', flag: '🇮🇳' },
    { code: 'bn', label: 'বাংলা', flag: '🇮🇳' },
    { code: 'pa', label: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
    { code: 'mr', label: 'मराठी', flag: '🇮🇳' },
    { code: 'te', label: 'తెలుగు', flag: '🇮🇳' },
    { code: 'ta', label: 'தமிழ்', flag: '🇮🇳' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-gradient-to-r from-emerald-950 via-teal-900 to-slate-950 text-white shadow-xl border-b border-emerald-700/40 backdrop-blur-md">
      <div className="max-w-md sm:max-w-2xl mx-auto px-4 py-2.5 flex items-center justify-between">
        {/* KrishiPals Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 shadow-lg group-hover:scale-105 transition-all block">
            <span className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-emerald-400 font-extrabold text-lg">
              🌾
            </span>
          </span>
          <span className="block">
            <span className="flex items-center gap-1.5">
              <span className="font-black text-lg tracking-tight leading-none bg-gradient-to-r from-white via-emerald-100 to-teal-200 bg-clip-text text-transparent">
                KrishiPals
              </span>
              <span className="bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[10px] font-extrabold px-1.5 py-0.2 rounded-md">
                HD AI
              </span>
            </span>
            <span className="block text-[10px] text-emerald-300/80 font-medium tracking-wide">
              Smart AI Farming Companion
            </span>
          </span>
        </Link>

        {/* Right Toolbar Controls */}
        <div className="flex items-center gap-1.5">
          {/* Quick Audio Readout Trigger */}
          <button
            onClick={() => speakText('Welcome to KrishiPals. Smart AI Farm Irrigation System is online and active.')}
            className="p-1.5 rounded-xl bg-emerald-900/60 hover:bg-emerald-800 text-emerald-300 hover:text-white transition-all border border-emerald-700/50"
            title="Hear Audio Guidance"
          >
            <Volume2 className="w-4 h-4" />
          </button>

          {/* Multi-Language Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="flex items-center gap-1 bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 text-xs font-bold px-2 py-1.5 rounded-xl border border-emerald-700/60 transition-all"
              title="Change Language"
            >
              <Globe className="w-3.5 h-3.5 text-emerald-400" />
              <span className="uppercase text-[11px]">{language}</span>
            </button>

            {showLangMenu && (
              <div className="absolute right-0 mt-2 w-36 bg-slate-900 border border-emerald-600/40 rounded-2xl shadow-2xl p-1.5 z-50 animate-in fade-in slide-in-from-top-2">
                {languagesList.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setShowLangMenu(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center justify-between transition-all ${
                      language === lang.code
                        ? 'bg-emerald-600 text-white font-bold'
                        : 'text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <span>{lang.label}</span>
                    <span>{lang.flag}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Theme Switcher Toggle */}
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="p-1.5 rounded-xl bg-emerald-900/60 hover:bg-emerald-800 text-emerald-300 hover:text-white transition-all border border-emerald-700/50"
            title="Toggle Light/Dark Theme"
          >
            {theme === 'light' ? <Moon className="w-4 h-4 text-emerald-300" /> : <Sun className="w-4 h-4 text-amber-400" />}
          </button>

          {/* Font Size Scaling Toggle */}
          <button
            onClick={() => {
              const next: Record<FontSizeOption, FontSizeOption> = {
                normal: 'large',
                large: 'xlarge',
                xlarge: 'normal',
              };
              setFontSize(next[fontSize]);
            }}
            className="px-2 py-1 bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 text-[11px] font-black rounded-xl border border-emerald-700/50 transition-all flex items-center gap-0.5"
            title="Adjust Text Size (Accessibility)"
          >
            <Type className="w-3 h-3 text-emerald-400" />
            <span>{fontSize === 'normal' ? 'A' : fontSize === 'large' ? 'A+' : 'A++'}</span>
          </button>

          {/* PWA Install Button */}
          {mounted && showInstallBtn && (
            <button
              onClick={handleInstallClick}
              className="flex items-center gap-1 text-xs font-extrabold bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 px-2.5 py-1.5 rounded-xl shadow-md transition-all animate-pulse"
              title="Install KrishiPals PWA"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden xs:inline">App</span>
            </button>
          )}

          {/* In-App Notifications Drawer */}
          <NotificationCenter />

          {/* Farmer Profile & Auth Controls */}
          {isAuthenticated && currentUser ? (
            <div className="flex items-center gap-1">
              <Link
                href="/profile"
                className="flex items-center gap-1.5 px-2 py-1 rounded-xl bg-emerald-800/80 hover:bg-emerald-700 text-emerald-200 hover:text-white transition-colors border border-emerald-700/60 text-xs font-bold"
                title={`Profile: ${currentUser.name}`}
              >
                <div className="w-4 h-4 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center text-[10px] font-black">
                  {currentUser.name.charAt(0)}
                </div>
                <span className="hidden sm:inline max-w-[80px] truncate">{currentUser.name.split(' ')[0]}</span>
              </Link>
              <Link
                href="/logout"
                className="p-1.5 rounded-xl bg-rose-950/60 hover:bg-rose-900 text-rose-300 hover:text-white transition-colors border border-rose-800/50"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : (
            <Link
              href="/login"
              className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 text-xs font-black shadow-md transition-all"
              title="Sign In"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Login</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
