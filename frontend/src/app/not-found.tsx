import Link from 'next/link';
import { Sprout } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center text-3xl font-extrabold shadow-sm">
        🌾
      </div>
      <h2 className="text-xl font-bold text-slate-900">404 — Page Not Found</h2>
      <p className="text-xs text-slate-500 max-w-xs">
        The requested field page or module could not be found. Please navigate back to the main dashboard.
      </p>
      <Link
        href="/"
        className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold transition-all shadow-xs"
      >
        Return to Dashboard
      </Link>
    </div>
  );
}
