import type { Metadata, Viewport } from 'next';
import './globals.css';
import ServiceWorkerRegister from '@/components/ServiceWorkerRegister';
import Header from '@/components/Header';
import BottomNav from '@/components/BottomNav';
import Providers from '@/components/Providers';
import KrishiPalsVoiceAssistant from '@/components/KrishiPalsVoiceAssistant';

export const metadata: Metadata = {
  title: 'KrishiPals — AI Smart Farming & Precision Irrigation Companion',
  description: 'Ultra HD AI-Powered Precision Irrigation & Farm Telemetry Ecosystem for Farmers',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'KrishiPals',
  },
  icons: {
    icon: '/icon-192.png',
    apple: '/apple-touch-icon.png',
  },
};

export const viewport: Viewport = {
  themeColor: '#064e3b',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body suppressHydrationWarning className="bg-slate-100 text-slate-900 font-sans antialiased min-h-screen flex flex-col selection:bg-emerald-200">
        <Providers>
          <ServiceWorkerRegister />
          <div suppressHydrationWarning className="flex-1 flex flex-col max-w-md sm:max-w-2xl mx-auto w-full min-h-screen shadow-2xl bg-slate-50 dark:bg-slate-950 relative pb-16 transition-colors duration-200">
            <Header />
            <main className="flex-1 p-4 sm:p-6 space-y-6">
              {children}
            </main>
            <KrishiPalsVoiceAssistant />
            <BottomNav />
          </div>
        </Providers>
      </body>
    </html>
  );
}
