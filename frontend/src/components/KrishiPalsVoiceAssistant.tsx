'use client';

import React, { useState } from 'react';
import { useKrishiPals } from '@/context/KrishiPalsContext';
import { Mic, MicOff, Volume2, X, Sparkles, Send, Bot, MessageSquare } from 'lucide-react';

export default function KrishiPalsVoiceAssistant() {
  const { isAssistantOpen, setIsAssistantOpen, t, language, speakText, stopSpeaking, isSpeaking } = useKrishiPals();
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: `Namaste! I am your KrishiPals AI Farm Assistant. You can ask me about soil moisture, weather forecast, water pump timing, or crop fertilizer!`,
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isListening, setIsListening] = useState(false);

  const predefinedQuestions = [
    '💧 When should I water my wheat field?',
    '🌧️ Will it rain today in Pune?',
    '🌾 How much water does Tomato need in flowering stage?',
    '⚡ How to save electricity during irrigation?',
  ];

  const handleSend = (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim()) return;

    // Add User Message
    setMessages((prev) => [...prev, { sender: 'user', text: query }]);
    if (!textToSend) setInputQuery('');

    // Generate AI Response based on query
    setTimeout(() => {
      let responseText = '';
      const qLower = query.toLowerCase();

      if (qLower.includes('water') || qLower.includes('irrigate') || qLower.includes('सिंचाई') || qLower.includes('сеচ')) {
        responseText = `Based on current soil moisture (38.4%) and dry weather, KrishiPals recommends watering your field tomorrow at 06:00 AM with 1,250 Liters. Morning watering reduces evaporation loss by 25%!`;
      } else if (qLower.includes('rain') || qLower.includes('weather') || qLower.includes('बारिश') || qLower.includes('বৃষ্টি')) {
        responseText = `Current weather shows 15% rain probability with 27.4°C air temperature. Skies are clear for the next 48 hours, so regular irrigation schedule is safe to execute.`;
      } else if (qLower.includes('tomato') || qLower.includes('fertilizer') || qLower.includes('टमाटर') || qLower.includes('টমেটো')) {
        responseText = `For Tomato crops in flowering stage, maintain soil moisture between 40%-60%. Apply Potassium and Phosphorus fertilizers in small split doses for maximum yield.`;
      } else {
        responseText = `KrishiPals AI is continuously monitoring your farm sensors. Your current crop health status is optimal, and no emergency action is required today!`;
      }

      setMessages((prev) => [...prev, { sender: 'ai', text: responseText }]);
      speakText(responseText);
    }, 600);
  };

  const handleVoiceInput = () => {
    if (typeof window === 'undefined' || !('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser version. You can type your query below!');
      return;
    }

    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      const langMap: Record<string, string> = {
        en: 'en-IN',
        hi: 'hi-IN',
        kn: 'kn-IN',
        bn: 'bn-IN',
        pa: 'pa-IN',
        mr: 'mr-IN',
        te: 'te-IN',
        ta: 'ta-IN',
      };
      recognition.lang = langMap[language] || 'en-IN';

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputQuery(transcript);
        handleSend(transcript);
      };

      recognition.start();
    } catch (e) {
      console.error('Speech recognition error:', e);
      setIsListening(false);
    }
  };

  if (!isAssistantOpen) {
    return (
      <button
        onClick={() => setIsAssistantOpen(true)}
        className="fixed bottom-20 right-4 z-50 bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-4 py-3 rounded-full shadow-2xl flex items-center gap-2.5 hover:scale-105 transition-all glow-border font-bold text-xs group animate-bounce"
        title="Open KrishiPals AI Assistant"
      >
        <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-emerald-200 animate-spin" style={{ animationDuration: '6s' }} />
        </div>
        <span>Ask KrishiPals AI</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-t-3xl sm:rounded-3xl shadow-2xl border border-emerald-500/30 overflow-hidden flex flex-col max-h-[85vh] animate-in slide-in-from-bottom">
        {/* Modal Header */}
        <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 p-4 text-white flex items-center justify-between border-b border-emerald-700/50">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center">
              <Bot className="w-5 h-5 text-emerald-300" />
            </div>
            <div>
              <h3 className="font-extrabold text-sm tracking-wide text-white">KrishiPals Voice AI</h3>
              <p className="text-[10px] text-emerald-300/80">Hands-Free Agricultural Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className="px-2 py-1 bg-amber-500/30 border border-amber-400/40 text-amber-200 text-[10px] font-bold rounded-lg flex items-center gap-1"
              >
                <Volume2 className="w-3 h-3 animate-pulse text-amber-400" />
                <span>Stop Voice</span>
              </button>
            )}
            <button
              onClick={() => {
                stopSpeaking();
                setIsAssistantOpen(false);
              }}
              className="p-1.5 rounded-full hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Chat History Messages */}
        <div className="flex-1 p-4 space-y-3 overflow-y-auto bg-slate-50 dark:bg-slate-950 min-h-[250px]">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'ai' && (
                <div className="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0 text-xs">
                  🌾
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl p-3 text-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-emerald-700 text-white font-medium rounded-tr-none'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none shadow-xs'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        {/* Quick Question Chips */}
        <div className="px-4 py-2 bg-slate-100 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 overflow-x-auto flex gap-1.5 no-scrollbar">
          {predefinedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q.replace(/^[^\s]+\s/, ''))}
              className="shrink-0 text-[10px] font-semibold bg-white dark:bg-slate-800 hover:bg-emerald-50 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 px-2.5 py-1 rounded-full shadow-2xs transition-all"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Query Input & Voice Button */}
        <div className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2">
          <button
            onClick={handleVoiceInput}
            className={`p-2.5 rounded-xl border transition-all ${
              isListening
                ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                : 'bg-emerald-50 dark:bg-slate-800 border-emerald-300 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100'
            }`}
            title="Click to speak your question"
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isListening ? 'Listening to your voice...' : 'Ask KrishiPals AI anything...'}
            className="flex-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />

          <button
            onClick={() => handleSend()}
            className="p-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-xs transition-all font-bold text-xs"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
