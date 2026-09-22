'use client';

import React from 'react';
import { KrishiPalsProvider } from '@/context/KrishiPalsContext';

export default function Providers({ children }: { children: React.ReactNode }) {
  return <KrishiPalsProvider>{children}</KrishiPalsProvider>;
}
