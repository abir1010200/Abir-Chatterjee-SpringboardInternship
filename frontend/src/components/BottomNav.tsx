'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { Home, Sprout, Calendar, History, BarChart3, User } from 'lucide-react';

export default function BottomNav() {
  const pathname = usePathname();
  const { t } = useKrishiPals();

  const navItems = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/fields', label: t.fields, icon: Sprout },
    { href: '/schedule', label: t.schedule, icon: Calendar },
    { href: '/history', label: t.history, icon: History },
    { href: '/analytics', label: t.trends, icon: BarChart3 },
    { href: '/profile', label: t.profile, icon: User },
  ];

  return (
    <nav className="sticky bottom-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-t border-slate-200 dark:border-slate-800 shadow-2xl transition-colors duration-200">
      <div className="max-w-md sm:max-w-2xl mx-auto px-2 py-1.5 flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center py-1 px-2.5 rounded-2xl transition-all duration-200 ${
                isActive
                  ? 'text-emerald-600 dark:text-emerald-400 font-extrabold bg-emerald-50 dark:bg-emerald-950/60 shadow-xs scale-105 border border-emerald-200/50 dark:border-emerald-800/50'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 font-medium hover:bg-slate-50 dark:hover:bg-slate-800'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform ${isActive ? 'text-emerald-600 dark:text-emerald-400 scale-110' : 'text-slate-400'}`} />
              <span className="text-[10px] mt-0.5 tracking-tight">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
