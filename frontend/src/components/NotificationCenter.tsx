'use client';

import React, { useState, useEffect } from 'react';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { Bell, AlertTriangle, CloudRain, Droplets, Clock, WifiOff, CheckCircle2, Volume2, X } from 'lucide-react';

export interface AlertNotification {
  id: string;
  type: 'low_moisture' | 'over_watering' | 'heavy_rain' | 'reminder' | 'sensor_failure';
  title: string;
  message: string;
  timestamp: string;
  severity: 'high' | 'medium' | 'info';
  isRead: boolean;
  fieldId?: number;
}

export default function NotificationCenter() {
  const { t, language, speakText } = useKrishiPals();
  const [isOpen, setIsOpen] = useState(false);
  const [alerts, setAlerts] = useState<AlertNotification[]>([]);

  useEffect(() => {
    // Generate dynamic rule-based & ML prediction alerts
    const initialAlerts: AlertNotification[] = [
      {
        id: '1',
        type: 'low_moisture',
        title: language === 'hi' ? 'कम मिट्टी नमी चेतावनी' : language === 'kn' ? 'ಕಡಿಮೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಎಚ್ಚರಿಕೆ' : 'Low Soil Moisture Warning',
        message: language === 'hi' ? 'उत्तर घाटी खेत (North Valley) की नमी 22.5% है। 45 मिनट सिंचाई आवश्यक है।' : language === 'kn' ? 'ಉತ್ತರ ಕಣಿವೆ ಜಮೀನಿನ ತೇವಾಂಶ ೨೨.೫% ಇದೆ. ೪೫ ನಿಮಿಷ ನೀರಾವರಿ ಅಗತ್ಯವಿದೆ.' : 'North Valley Field moisture dropped to 22.5%. Recommended 45 mins pump runtime.',
        timestamp: '10 mins ago',
        severity: 'high',
        isRead: false,
        fieldId: 1,
      },
      {
        id: '2',
        type: 'heavy_rain',
        title: language === 'hi' ? 'बारिश अलर्ट - सिंचाई स्थगित' : language === 'kn' ? 'ಮಳೆ ಎಚ್ಚರಿಕೆ - ನೀರಾವರಿ ಮುಂದೂಡಲಾಗಿದೆ' : 'Rain Shield — Irrigation Postponed',
        message: language === 'hi' ? 'अगले 24 घंटों में 75% बारिश की संभावना है। 1,250L पानी की बचत होगी।' : language === 'kn' ? 'ಮುಂದಿನ ೨೪ ಗಂಟೆಗಳಲ್ಲಿ ೭೫% ಮಳೆಯ ಸಾಧ್ಯತೆಯಿದೆ. ೧,೨೫೦L ನೀರು ಉಳಿತಾಯವಾಗಿದೆ.' : '75% rain probability detected. Automated irrigation delay enabled to prevent water waste.',
        timestamp: '1 hour ago',
        severity: 'medium',
        isRead: false,
        fieldId: 2,
      },
      {
        id: '3',
        type: 'reminder',
        title: language === 'hi' ? 'सुबह की सिंचाई का समय' : language === 'kn' ? 'ಬೆಳಗಿನ ನೀರಾವರಿ ಸಮಯ' : 'Morning Irrigation Window',
        message: language === 'hi' ? 'सुबह 6:00 बजे ठंडे वातावरण में सिंचाई शुरू करने का अनुशंसित समय है।' : language === 'kn' ? 'ಬೆಳಿಗ್ಗೆ ೬:೦೦ ಗಂಟೆಗೆ ತಂಪಾದ ವಾತಾವರಣದಲ್ಲಿ ನೀರಾವರಿ ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.' : 'Optimal morning window is 6:00 AM - 8:00 AM for reduced water evaporation.',
        timestamp: '3 hours ago',
        severity: 'info',
        isRead: true,
      },
      {
        id: '4',
        type: 'sensor_failure',
        title: language === 'hi' ? 'सेंसर ऑनलाइन स्थिति' : language === 'kn' ? 'ಸಂವೇದಕ ಆನ್‌ಲೈನ್ ಸ್ಥಿತಿ' : 'Sensor Telemetry Check',
        message: language === 'hi' ? 'सेंसर नोड SN-102 ठीक से डेटा भेज रहा है।' : language === 'kn' ? 'ಸಂವೇದಕ ನೋಡ್ SN-102 ಸರಿಯಾಗಿ ಡೇಟಾ ಕಳುಹಿಸುತ್ತಿದೆ.' : 'Sensor Node SN-102 online and sending valid soil moisture packets.',
        timestamp: 'Yesterday',
        severity: 'info',
        isRead: true,
      }
    ];

    setAlerts(initialAlerts);
  }, [language]);

  const unreadCount = alerts.filter(a => !a.isRead).length;

  const markAllRead = () => {
    setAlerts(alerts.map(a => ({ ...a, isRead: true })));
  };

  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const getAlertIcon = (type: AlertNotification['type']) => {
    switch (type) {
      case 'low_moisture':
        return <Droplets className="w-5 h-5 text-red-500" />;
      case 'over_watering':
        return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'heavy_rain':
        return <CloudRain className="w-5 h-5 text-sky-500" />;
      case 'reminder':
        return <Clock className="w-5 h-5 text-emerald-500" />;
      case 'sensor_failure':
        return <WifiOff className="w-5 h-5 text-purple-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-emerald-500" />;
    }
  };

  return (
    <div className="relative">
      {/* Header Notification Bell Icon */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-2xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700/60 transition-all"
        aria-label="Toggle Notifications"
      >
        <Bell className="w-5 h-5 text-emerald-400" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white font-black text-[10px] rounded-full flex items-center justify-center animate-bounce">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Slide-out Notification Drawer */}
      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-slate-900 border border-emerald-500/40 rounded-3xl shadow-2xl z-50 p-4 space-y-3 animate-in fade-in slide-in-from-top-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-emerald-400" />
              <h3 className="font-extrabold text-sm text-white">{t.notifications || 'Alerts & Notifications'}</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 bg-red-500/20 text-red-400 border border-red-500/40 text-[10px] font-black rounded-full">
                  {unreadCount} new
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-[11px] font-bold text-emerald-400 hover:underline"
                >
                  {t.markAllRead || 'Mark all read'}
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-full text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar">
            {alerts.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-xs font-medium">
                {t.noAlerts || 'No active alerts. All fields optimal!'}
              </div>
            ) : (
              alerts.map((item) => (
                <div
                  key={item.id}
                  className={`p-3.5 rounded-2xl border transition-all relative ${
                    item.isRead
                      ? 'bg-slate-950/60 border-slate-800/80 text-slate-400'
                      : 'bg-slate-850 border-emerald-500/50 text-slate-100 shadow-md'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 p-1.5 rounded-xl bg-slate-800">{getAlertIcon(item.type)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="font-extrabold text-xs text-white truncate">{item.title}</h4>
                        <span className="text-[10px] text-slate-500 font-medium">{item.timestamp}</span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 font-medium leading-snug">{item.message}</p>
                      
                      <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-slate-800/80">
                        <button
                          onClick={() => speakText(`${item.title}. ${item.message}`)}
                          className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 hover:text-emerald-300"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>Audio</span>
                        </button>
                        <button
                          onClick={() => deleteAlert(item.id)}
                          className="text-[10px] text-slate-500 hover:text-slate-300 font-semibold"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
