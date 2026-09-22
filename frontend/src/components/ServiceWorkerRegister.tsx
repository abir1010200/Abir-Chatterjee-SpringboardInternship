'use client';

import { useEffect, useState } from 'react';
import { Download, WifiOff } from 'lucide-react';

export default function ServiceWorkerRegister() {
  const [mounted, setMounted] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    setMounted(true);

    // 1. Service Worker registration
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('[PWA] Service Worker registered successfully:', reg.scope);
        })
        .catch((err) => {
          console.error('[PWA] Service Worker registration failed:', err);
        });
    }

    // Register SW in development too for PWA testing if available
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'development') {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('[PWA Dev] Service Worker registered:', reg.scope);
        })
        .catch(() => {});
    }

    // 2. Install prompt listener
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // 3. Online / Offline status
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    if (typeof window !== 'undefined') {
      setIsOffline(!navigator.onLine);
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setIsInstalled(true);
      setIsInstallable(false);
    }
    setDeferredPrompt(null);
  };

  if (!mounted) return null;

  return (
    <>
      {/* Offline Alert Banner */}
      {isOffline && (
        <div className="bg-amber-600 text-white px-4 py-2 text-center text-sm font-bold flex items-center justify-center gap-2 shadow-md">
          <WifiOff className="w-5 h-5 animate-pulse" />
          <span>You are currently offline. Using saved field data.</span>
        </div>
      )}

      {/* PWA Install Banner */}
      {isInstallable && !isInstalled && (
        <div className="bg-emerald-800 text-white p-4 sticky top-0 z-50 shadow-lg border-b-2 border-emerald-600 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-2xl">
              🌱
            </div>
            <div>
              <p className="font-bold text-base leading-tight">Install Farmer App</p>
              <p className="text-xs text-emerald-200">Tap to add to phone home screen</p>
            </div>
          </div>
          <button
            onClick={handleInstallClick}
            className="bg-emerald-400 hover:bg-emerald-300 text-emerald-950 font-extrabold px-4 py-2.5 rounded-xl text-sm flex items-center gap-2 shadow-md active:scale-95 transition-all"
          >
            <Download className="w-5 h-5" />
            Install
          </button>
        </div>
      )}
    </>
  );
}
