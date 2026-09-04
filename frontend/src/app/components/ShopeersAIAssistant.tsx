"use client";

import { useState } from "react";

export default function ShopeersAIAssistant() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<string | null>(null);

  const handleSend = (text?: string) => {
    const prompt = text || query;
    if (!prompt.trim()) return;

    if (prompt.toLowerCase().includes("high") || prompt.toLowerCase().includes("ev")) {
      setResponse("Hero Case detected: Order pay_41b5dc97 Rahul Sharma (₹45,000.00). ML probability: 99.46%, EV: ₹44,757.00. Recommended Strategy: RETRY. Reason: Temporary gateway network failure.");
    } else if (prompt.toLowerCase().includes("network") || prompt.toLowerCase().includes("error")) {
      setResponse("Network Errors account for 55% of all payment drops. Downstream bank gateways timed out. 10 cases are eligible for automated retry with >90% recovery rate.");
    } else if (prompt.toLowerCase().includes("drift") || prompt.toLowerCase().includes("model")) {
      setResponse("Model PSI is 0.042 (well below 0.10 threshold). Probability calibration Brier score is 0.0753. No feature drift detected across payment channels.");
    } else {
      setResponse(`AI Recommendation: 7 transactions pending approval. Total predicted recoverable value: ₹2,37,256.00 across 20 active failure events.`);
    }
  };

  return (
    <div className="bg-gradient-to-b from-slate-900 via-slate-900 to-indigo-950 text-white rounded-3xl p-6 relative overflow-hidden border border-slate-800 shadow-xl flex flex-col justify-between min-h-[380px]">
      {/* Background Technical Dotted Grid */}
      <div
        className="absolute inset-0 opacity-15 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(#60a5fa 1px, transparent 1px)",
          backgroundSize: "20px 20px",
        }}
      ></div>

      {/* Top Header */}
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-white">Shopeers AI Assistant</span>
            <span className="block text-[10px] text-blue-300 font-mono">Autonomous Copilot</span>
          </div>
        </div>

        <span className="px-2.5 py-1 text-[10px] font-bold rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span>
          Live Diagnostics
        </span>
      </div>

      {/* Centerpiece 3D Glowing Orb & Dynamic Insight */}
      <div className="my-6 flex flex-col items-center text-center relative z-10">
        {/* Glowing Orb Animation */}
        <div className="relative mb-4">
          <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-600 via-cyan-400 to-indigo-400 shadow-lg shadow-cyan-500/50 flex items-center justify-center animate-pulse">
            <div className="w-16 h-16 rounded-full bg-slate-900/60 backdrop-blur-xs flex items-center justify-center border border-white/20">
              <svg className="w-8 h-8 text-cyan-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
          </div>
          {/* Ambient Outer Halo */}
          <div className="absolute inset-0 w-24 h-24 rounded-full bg-blue-500/30 blur-2xl -z-10 animate-ping"></div>
        </div>

        {/* AI Insight Readout */}
        <div className="max-w-md">
          {response ? (
            <div className="p-3.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-xs text-slate-100 text-left leading-relaxed">
              <span className="font-bold text-cyan-300 block mb-1">⚡ AI Copilot Analysis:</span>
              {response}
            </div>
          ) : (
            <>
              <p className="text-sm font-semibold text-white leading-relaxed">
                &ldquo;RecoverAI diagnosed 20 payment failures. 10 cases have &gt;90% recovery likelihood. 7 pending cases require human sign-off.&rdquo;
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                Estimated recoverable capital: <strong className="text-emerald-400">₹2,37,256.00</strong>
              </span>
            </>
          )}
        </div>
      </div>

      {/* Floating Pill Prompt Input Bar (Shopeers Signature) */}
      <div className="relative z-10 space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="w-full bg-white/10 hover:bg-white/15 focus-within:bg-white/20 backdrop-blur-md border border-white/20 rounded-full px-4 py-2 flex items-center gap-3 transition-all shadow-lg"
        >
          {/* Attachment Paperclip */}
          <button type="button" className="text-slate-400 hover:text-white transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>

          {/* Text Input */}
          <input
            type="text"
            placeholder="Ask Shopeers AI anything..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-xs text-white placeholder-slate-400 focus:outline-hidden"
          />

          {/* Microphone */}
          <button type="button" className="text-slate-400 hover:text-white transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>

          {/* Blue Send Button */}
          <button
            type="submit"
            className="w-7 h-7 rounded-full bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center transition-all shadow-md shadow-blue-500/50"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.4} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </form>

        {/* Suggested Quick Prompt Chips */}
        <div className="flex flex-wrap items-center gap-1.5 justify-center">
          <button
            type="button"
            onClick={() => handleSend("high ev case")}
            className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 text-[10px] text-slate-300 border border-white/10 transition-colors"
          >
            ⭐ Hero Case (₹45K)
          </button>
          <button
            type="button"
            onClick={() => handleSend("network errors")}
            className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 text-[10px] text-slate-300 border border-white/10 transition-colors"
          >
            📶 Network Timeouts
          </button>
          <button
            type="button"
            onClick={() => handleSend("model drift")}
            className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 text-[10px] text-slate-300 border border-white/10 transition-colors"
          >
            📊 Drift (PSI 0.042)
          </button>
        </div>
      </div>
    </div>
  );
}
