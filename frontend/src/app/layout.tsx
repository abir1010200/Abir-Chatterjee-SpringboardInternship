import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SmartIrrigate AI — Predictive Water Management',
  description: 'AI-Powered Smart Irrigation System for predictive water management and crop optimization.',
  manifest: '/manifest.json',
  themeColor: '#16a34a',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#16a34a" />
      </head>
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="bg-emerald-800 text-white shadow-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🌱</span>
                <div>
                  <h1 className="text-lg font-bold tracking-tight">SmartIrrigate AI</h1>
                  <p className="text-xs text-emerald-200">Milestone 1: Data Ingestion & Weather Telemetry</p>
                </div>
              </div>
              <div className="flex items-center space-x-4 text-sm font-medium">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  ● Telemetry Live
                </span>
              </div>
            </div>
          </header>
          <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
            {children}
          </main>
          <footer className="bg-slate-900 text-slate-400 py-4 text-center text-xs">
            SmartIrrigate AI &copy; 2026 — Milestone 1 Production Pipeline
          </footer>
        </div>
      </body>
    </html>
  );
}
