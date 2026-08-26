'use client';

import React from 'react';
import Link from 'next/link';
import RegistrationForm from '@/components/RegistrationForm';

export default function RegisterPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/" className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1 mb-2">
            ← Back to Telemetry Dashboard
          </Link>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Register New Agricultural Sector</h2>
          <p className="text-sm text-slate-500 mt-1">
            Establish a field profile, map crop growth stages, and configure IoT sensor hardware telemetry.
          </p>
        </div>
      </div>

      <RegistrationForm />
    </div>
  );
}
