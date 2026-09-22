'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Farmer, AuthResponse } from '@/types';

export type SupportedLanguage = 'en' | 'hi' | 'kn' | 'bn' | 'pa' | 'mr' | 'te' | 'ta';
export type FontSizeOption = 'normal' | 'large' | 'xlarge';
export type ThemeMode = 'light' | 'dark';

export interface Translations {
  appName: string;
  tagline: string;
  welcomeFarmer: string;
  aiAssistantSubtitle: string;
  addField: string;
  fields: string;
  schedule: string;
  history: string;
  trends: string;
  profile: string;
  registeredFields: string;
  manageAll: string;
  soilMoisture: string;
  rainProbability: string;
  airTemp: string;
  humidity: string;
  cropAndKc: string;
  todaysIrrigationPlan: string;
  recommendedTime: string;
  waterVolumeDuration: string;
  startPumpNow: string;
  pumpStarted: string;
  dispatchingPump: string;
  listenAudio: string;
  speakToKrishiPals: string;
  rainShieldActive: string;
  actionRecommended: string;
  optimalHydration: string;
  clearSkies: string;
  morningCoolWindow: string;
  whatIfSimulatorTitle: string;
  simulateScenario: string;
  resetDefaults: string;
  modelAccuracy: string;
  waterSavedThisMonth: string;
  proPlanActive: string;
  notifications: string;
  alerts: string;
  lowMoistureAlert: string;
  overWateringAlert: string;
  heavyRainAlert: string;
  irrigationReminder: string;
  sensorFailureAlert: string;
  noAlerts: string;
  markAllRead: string;
  farmerProfile: string;
  personalDetails: string;
  phoneNumber: string;
  location: string;
  accessibilityOptions: string;
  fontSize: string;
  themeMode: string;
  notificationPreferences: string;
  pushNotifications: string;
  smsAlerts: string;
  emailNotifications: string;
  savePreferences: string;
  downloadPdfReport: string;
  exportCsvData: string;
  soilMoistureTrend: string;
  weatherTrend: string;
  waterSavings: string;
  audioExplanation: string;
  speakQuery: string;
  listening: string;
  fieldName: string;
  soilType: string;
  cropType: string;
  growthStage: string;
  landSize: string;
  registerFieldBtn: string;
  fieldRegisteredSuccess: string;
  login: string;
  logout: string;
  loginTitle: string;
  loginSubtitle: string;
  enterEmailOrPhone: string;
  enterPassword: string;
  rememberMe: string;
  quickDemoLogin: string;
  dontHaveAccount: string;
  registerFarmerAccount: string;
  loggedInAs: string;
  logoutConfirmTitle: string;
  logoutConfirmSubtitle: string;
  confirmLogoutBtn: string;
  cancelBtn: string;
}

const enTranslations: Translations = {
  appName: 'KrishiPals',
  tagline: 'AI Farming & Precision Irrigation Companion',
  welcomeFarmer: 'Namaste, Farmer Friend',
  aiAssistantSubtitle: 'Real-time soil telemetry & physics-informed AI water advice',
  addField: 'Add Field',
  fields: 'Fields',
  schedule: 'Schedule',
  history: 'History',
  trends: 'Trends',
  profile: 'Profile',
  registeredFields: 'Registered Fields',
  manageAll: 'Manage All',
  soilMoisture: 'Soil Moisture',
  rainProbability: 'Rain Prob',
  airTemp: 'Air Temp',
  humidity: 'Humidity',
  cropAndKc: 'Crop & Kc',
  todaysIrrigationPlan: "Today's Irrigation Plan",
  recommendedTime: 'Recommended Time',
  waterVolumeDuration: 'Water Volume & Runtime',
  startPumpNow: 'Start Water Pump Now',
  pumpStarted: 'Pump Started Successfully!',
  dispatchingPump: 'Dispatching Pump Signal...',
  listenAudio: 'Listen in Audio',
  speakToKrishiPals: 'Speak to KrishiPals',
  rainShieldActive: 'Rain Shield Active',
  actionRecommended: 'Action Recommended',
  optimalHydration: 'Optimal Soil Hydration',
  clearSkies: 'Clear Skies',
  morningCoolWindow: 'Morning cool window (6-8 AM)',
  whatIfSimulatorTitle: 'Farmer What-If Scenario Simulator',
  simulateScenario: 'Simulate Scenario',
  resetDefaults: 'Reset Defaults',
  modelAccuracy: 'AI Model Accuracy',
  waterSavedThisMonth: 'Water Saved This Month',
  proPlanActive: 'Pro AI Plan Active',
  notifications: 'Notifications',
  alerts: 'Alerts',
  lowMoistureAlert: 'Low Soil Moisture Warning',
  overWateringAlert: 'Over-Watering Risk Alert',
  heavyRainAlert: 'Heavy Rainfall Warning',
  irrigationReminder: 'Irrigation Schedule Reminder',
  sensorFailureAlert: 'Sensor Data Missing Alert',
  noAlerts: 'No active alerts. All fields optimal!',
  markAllRead: 'Mark all as read',
  farmerProfile: 'Farmer Profile',
  personalDetails: 'Personal Details',
  phoneNumber: 'Phone Number',
  location: 'Farm Location',
  accessibilityOptions: 'Elderly Accessibility & Display',
  fontSize: 'Text Font Size',
  themeMode: 'Theme Color',
  notificationPreferences: 'Notification Channels',
  pushNotifications: 'Web Push Notifications',
  smsAlerts: 'SMS Alerts (Twilio)',
  emailNotifications: 'Email Reports (SendGrid)',
  savePreferences: 'Save Preferences',
  downloadPdfReport: 'Download PDF Irrigation Summary',
  exportCsvData: 'Export Sensor Data (CSV)',
  soilMoistureTrend: 'Soil Moisture Trend',
  weatherTrend: 'Rainfall & Weather Trend',
  waterSavings: 'Water Usage & Savings',
  audioExplanation: 'Tap for Voice Audio Explanation',
  speakQuery: 'Tap microphone and ask your question',
  listening: 'Listening to your voice...',
  fieldName: 'Field Name',
  soilType: 'Soil Type',
  cropType: 'Crop Type',
  growthStage: 'Growth Stage',
  landSize: 'Field Size (Hectares)',
  registerFieldBtn: 'Register New Field',
  fieldRegisteredSuccess: 'Field Registered Successfully!',
  login: 'Sign In',
  logout: 'Sign Out',
  loginTitle: 'Farmer Sign In',
  loginSubtitle: 'Access AI telemetry, pump control & personalized irrigation recommendations.',
  enterEmailOrPhone: 'Email or Mobile Number',
  enterPassword: 'Password / Security PIN',
  rememberMe: 'Stay signed in on this device',
  quickDemoLogin: 'Quick Demo Farmer Accounts',
  dontHaveAccount: "Don't have an account?",
  registerFarmerAccount: 'Register as a New Farmer',
  loggedInAs: 'Logged in as',
  logoutConfirmTitle: 'Sign Out of KrishiPals',
  logoutConfirmSubtitle: 'Are you sure you want to end your active farming session?',
  confirmLogoutBtn: 'Yes, Sign Out',
  cancelBtn: 'Cancel',
};

const translations: Record<SupportedLanguage, Translations> = {
  en: enTranslations,
  hi: {
    appName: 'कृषि पाल्स (KrishiPals)',
    tagline: 'AI खेती और सटीक सिंचाई साथी',
    welcomeFarmer: 'नमस्ते, किसान मित्र',
    aiAssistantSubtitle: 'वास्तविक समय मिट्टी टेलीमेट्री और भौतिकी-आधारित AI जल सलाह',
    addField: 'खेत जोड़ें',
    fields: 'खेत',
    schedule: 'अनुसूची',
    history: 'इतिहास',
    trends: 'रुझान',
    profile: 'प्रोफाइल',
    registeredFields: 'पंजीकृत खेत',
    manageAll: 'सभी प्रबंधित करें',
    soilMoisture: 'मिट्टी की नमी',
    rainProbability: 'वर्षा संभावना',
    airTemp: 'वायु तापमान',
    humidity: 'आर्द्रता',
    cropAndKc: 'फसल और Kc',
    todaysIrrigationPlan: 'आज की सिंचाई योजना',
    recommendedTime: 'अनुशंसित समय',
    waterVolumeDuration: 'जल मात्रा और अवधि',
    startPumpNow: 'अभी पानी का पंप चालू करें',
    pumpStarted: 'पंप सफलतापूर्वक चालू हो गया!',
    dispatchingPump: 'पंप सिग्नल भेजा जा रहा है...',
    listenAudio: 'ऑडियो सुनें',
    speakToKrishiPals: 'कृषि पाल्स से बात करें',
    rainShieldActive: 'वर्षा ढाल सक्रिय',
    actionRecommended: 'कार्रवाई अनुशंसित',
    optimalHydration: 'इष्टतम मिट्टी जलयोजन',
    clearSkies: 'साफ आसमान',
    morningCoolWindow: 'सुबह की ठंडी खिड़की (6-8 AM)',
    whatIfSimulatorTitle: 'किसान क्या-अगर परिदृश्य सिम्युलेटर',
    simulateScenario: 'परिदृश्य सिमुलेट करें',
    resetDefaults: 'डिफॉल्ट रीसेट करें',
    modelAccuracy: 'AI मॉडल सटीकता',
    waterSavedThisMonth: 'इस महीने बचाया गया पानी',
    proPlanActive: 'प्रो AI योजना सक्रिय',
    notifications: 'सूचनाएं',
    alerts: 'चेतावनी',
    lowMoistureAlert: 'कम मिट्टी की नमी चेतावनी',
    overWateringAlert: 'अतिरिक्त सिंचाई जोखिम चेतावनी',
    heavyRainAlert: 'भारी वर्षा चेतावनी',
    irrigationReminder: 'सिंचाई अनुसूची अनुस्मारक',
    sensorFailureAlert: 'सेंसर डेटा गुम चेतावनी',
    noAlerts: 'कोई सक्रिय चेतावनी नहीं। सभी खेत इष्टतम हैं!',
    markAllRead: 'सभी को पढ़ा हुआ चिह्नित करें',
    farmerProfile: 'किसान प्रोफाइल',
    personalDetails: 'व्यक्तिगत विवरण',
    phoneNumber: 'फ़ोन नंबर',
    location: 'फार्म स्थान',
    accessibilityOptions: 'बुजुर्ग पहुंच और प्रदर्शन',
    fontSize: 'पाठ फ़ॉन्ट आकार',
    themeMode: 'थीम रंग',
    notificationPreferences: 'अधिसूचना चैनल',
    pushNotifications: 'वेब पुश सूचनाएं',
    smsAlerts: 'एसएमएस अलर्ट (Twilio)',
    emailNotifications: 'ईमेल रिपोर्ट (SendGrid)',
    savePreferences: 'प्राथमिकताएं सहेजें',
    downloadPdfReport: 'पीडीएफ सिंचाई सारांश डाउनलोड करें',
    exportCsvData: 'सेंसर डेटा निर्यात करें (CSV)',
    soilMoistureTrend: 'मिट्टी की नमी का रुझान',
    weatherTrend: 'वर्षा और मौसम का रुझान',
    waterSavings: 'जल उपयोग और बचत',
    audioExplanation: 'आवाज ऑडियो स्पष्टीकरण के लिए टैप करें',
    speakQuery: 'माइक्रोफोन टैप करें और अपना प्रश्न पूछें',
    listening: 'आपकी आवाज़ सुन रहे हैं...',
    fieldName: 'खेत का नाम',
    soilType: 'मिट्टी का प्रकार',
    cropType: 'फसल का प्रकार',
    growthStage: 'विकास चरण',
    landSize: 'खेत का आकार (हेक्टेयर)',
    registerFieldBtn: 'नया खेत पंजीकृत करें',
    fieldRegisteredSuccess: 'खेत सफलतापूर्वक पंजीकृत हुआ!',
    login: 'लॉग इन करें',
    logout: 'लॉग आउट',
    loginTitle: 'किसान साइन इन',
    loginSubtitle: 'AI टेलीमेट्री, पंप नियंत्रण और व्यक्तिगत सिंचाई सलाह प्राप्त करें।',
    enterEmailOrPhone: 'ईमेल या मोबाइल नंबर',
    enterPassword: 'पासवर्ड / सुरक्षा पिन',
    rememberMe: 'मुझे इस डिवाइस पर साइन इन रखें',
    quickDemoLogin: 'त्वरित डेमो किसान खाते',
    dontHaveAccount: 'खाता नहीं है?',
    registerFarmerAccount: 'नए किसान के रूप में पंजीकरण करें',
    loggedInAs: 'के रूप में लॉग इन हैं',
    logoutConfirmTitle: 'कृषि पाल्स से लॉग आउट करें',
    logoutConfirmSubtitle: 'क्या आप वाकई अपना सक्रिय सत्र समाप्त करना चाहते हैं?',
    confirmLogoutBtn: 'हाँ, लॉग आउट करें',
    cancelBtn: 'रद्द करें',
  },
  kn: enTranslations,
  bn: enTranslations,
  pa: enTranslations,
  mr: enTranslations,
  te: enTranslations,
  ta: enTranslations,
};

interface KrishiPalsContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  fontSize: FontSizeOption;
  setFontSize: (size: FontSizeOption) => void;
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
  t: Translations;
  speakText: (text: string) => void;
  stopSpeaking: () => void;
  isSpeaking: boolean;
  isAssistantOpen: boolean;
  setIsAssistantOpen: (open: boolean) => void;
  selectedFieldId: number;
  setSelectedFieldId: (id: number) => void;
  // Auth state
  currentUser: Farmer | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<{ success: boolean; message: string; farmer?: Farmer }>;
  logout: () => Promise<void>;
  registerFarmer: (data: { name: string; email: string; phone?: string; password: string; address?: string }) => Promise<{ success: boolean; message: string }>;
}

const KrishiPalsContext = createContext<KrishiPalsContextType | undefined>(undefined);

export const KrishiPalsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<SupportedLanguage>('en');
  const [fontSize, setFontSize] = useState<FontSizeOption>('normal');
  const [theme, setTheme] = useState<ThemeMode>('light');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [selectedFieldId, setSelectedFieldId] = useState<number>(1);
  const [currentUser, setCurrentUser] = useState<Farmer | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    try {
      const savedLang = localStorage.getItem('krishipals_lang') as SupportedLanguage;
      if (savedLang && translations[savedLang]) setLanguage(savedLang);

      const savedFont = localStorage.getItem('krishipals_font') as FontSizeOption;
      if (savedFont) setFontSize(savedFont);

      const savedTheme = localStorage.getItem('krishipals_theme') as ThemeMode;
      if (savedTheme) setTheme(savedTheme);

      // Hydrate stored user session
      const savedToken = localStorage.getItem('krishipals_token');
      const savedUserJson = localStorage.getItem('krishipals_user');
      if (savedToken && savedUserJson) {
        setToken(savedToken);
        setCurrentUser(JSON.parse(savedUserJson));
      } else {
        // Default to Demo Farmer Rajesh Patel if no session exists
        const defaultFarmer: Farmer = {
          id: 1,
          name: 'Rajesh Patel',
          email: 'rajesh.patel@agrofarm.io',
          phone: '+91-98765-43210',
          address: 'Plot 42, Green Valley Agricultural Zone, Pune, India',
          created_at: '2026-08-26T17:28:03.516844',
        };
        setCurrentUser(defaultFarmer);
      }
    } catch (e) {
      console.warn('LocalStorage unavailable:', e);
    }
  }, []);

  const handleSetLanguage = (lang: SupportedLanguage) => {
    setLanguage(lang);
    try {
      localStorage.setItem('krishipals_lang', lang);
    } catch (e) {}
  };

  const handleSetFontSize = (size: FontSizeOption) => {
    setFontSize(size);
    try {
      localStorage.setItem('krishipals_font', size);
    } catch (e) {}
  };

  const handleSetTheme = (newTheme: ThemeMode) => {
    setTheme(newTheme);
    try {
      localStorage.setItem('krishipals_theme', newTheme);
    } catch (e) {}
  };

  const login = async (usernameOrEmail: string, password: string): Promise<{ success: boolean; message: string; farmer?: Farmer }> => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
      });

      const data: AuthResponse = await res.json();
      if (res.ok && data.success && data.farmer) {
        setCurrentUser(data.farmer);
        setToken(data.access_token || null);
        try {
          if (data.access_token) localStorage.setItem('krishipals_token', data.access_token);
          localStorage.setItem('krishipals_user', JSON.stringify(data.farmer));
        } catch (e) {}
        return { success: true, message: data.message, farmer: data.farmer };
      } else {
        return { success: false, message: data.message || 'Authentication failed.' };
      }
    } catch (err: any) {
      return { success: false, message: err?.message || 'Network error connecting to auth server.' };
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {}
    setCurrentUser(null);
    setToken(null);
    try {
      localStorage.removeItem('krishipals_token');
      localStorage.removeItem('krishipals_user');
    } catch (e) {}
  };

  const registerFarmer = async (data: {
    name: string;
    email: string;
    phone?: string;
    password: string;
    address?: string;
  }): Promise<{ success: boolean; message: string }> => {
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const resData: AuthResponse = await res.json();
      if (res.ok && resData.success && resData.farmer) {
        setCurrentUser(resData.farmer);
        setToken(resData.access_token || null);
        try {
          if (resData.access_token) localStorage.setItem('krishipals_token', resData.access_token);
          localStorage.setItem('krishipals_user', JSON.stringify(resData.farmer));
        } catch (e) {}
        return { success: true, message: resData.message };
      } else {
        return { success: false, message: resData.message || 'Registration failed.' };
      }
    } catch (err: any) {
      return { success: false, message: err?.message || 'Network error during registration.' };
    }
  };

  const speakText = (text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Text-to-speech audio is not supported in this browser.');
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);

    const langMap: Record<SupportedLanguage, string> = {
      en: 'en-IN',
      hi: 'hi-IN',
      kn: 'kn-IN',
      bn: 'bn-IN',
      pa: 'pa-IN',
      mr: 'mr-IN',
      te: 'te-IN',
      ta: 'ta-IN',
    };
    utterance.lang = langMap[language] || 'en-IN';
    utterance.rate = 0.95;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const currentTranslations = translations[language] || translations.en;

  return (
    <KrishiPalsContext.Provider
      value={{
        language,
        setLanguage: handleSetLanguage,
        fontSize,
        setFontSize: handleSetFontSize,
        theme,
        setTheme: handleSetTheme,
        t: currentTranslations,
        speakText,
        stopSpeaking,
        isSpeaking,
        isAssistantOpen,
        setIsAssistantOpen,
        selectedFieldId,
        setSelectedFieldId,
        currentUser,
        token,
        isAuthenticated: !!currentUser,
        login,
        logout,
        registerFarmer,
      }}
    >
      <div suppressHydrationWarning className={`krishipals-wrapper theme-${theme} font-size-${fontSize}`}>
        {children}
      </div>
    </KrishiPalsContext.Provider>
  );
};

const defaultFallbackContext: KrishiPalsContextType = {
  language: 'en',
  setLanguage: () => {},
  fontSize: 'normal',
  setFontSize: () => {},
  theme: 'light',
  setTheme: () => {},
  t: translations.en,
  speakText: () => {},
  stopSpeaking: () => {},
  isSpeaking: false,
  isAssistantOpen: false,
  setIsAssistantOpen: () => {},
  selectedFieldId: 1,
  setSelectedFieldId: () => {},
  currentUser: null,
  token: null,
  isAuthenticated: false,
  login: async () => ({ success: false, message: 'Default context' }),
  logout: async () => {},
  registerFarmer: async () => ({ success: false, message: 'Default context' }),
};

export const useKrishiPals = () => {
  const context = useContext(KrishiPalsContext);
  return context || defaultFallbackContext;
};
