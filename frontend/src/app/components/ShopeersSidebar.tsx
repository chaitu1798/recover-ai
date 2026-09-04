"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function ShopeersSidebar() {
  const pathname = usePathname();
  const [financialOpen, setFinancialOpen] = useState(true);

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 min-h-screen flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-20 px-6 flex items-center gap-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.4} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <span className="font-extrabold text-xl tracking-tight text-slate-900">
              Recover<span className="text-blue-600">AI</span>
            </span>
            <span className="block text-[10px] font-medium text-slate-400 -mt-0.5">
              Autonomous Payment Recovery
            </span>
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="px-4 py-6 space-y-6">
          {/* Main Menu */}
          <div>
            <span className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Main Menu
            </span>
            <div className="mt-2 space-y-1">
              {/* Dashboard */}
              <Link
                href="/"
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  pathname === "/"
                    ? "bg-blue-50 text-blue-600 font-semibold shadow-2xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  <span>Dashboard</span>
                </div>
                {pathname === "/" && (
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                )}
              </Link>

              {/* ML Model Monitoring */}
              <Link
                href="/ml-monitoring"
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  pathname === "/ml-monitoring"
                    ? "bg-blue-50 text-blue-600 font-semibold shadow-2xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span>ML Monitoring</span>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-700">
                  AUC 0.96
                </span>
              </Link>

              {/* Recovery Cases */}
              <a
                href="/#cases-ledger"
                className="flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <span>Recovery Cases</span>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-600">
                  20
                </span>
              </a>

              {/* Financial Accordion */}
              <div>
                <button
                  onClick={() => setFinancialOpen(!financialOpen)}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Financial</span>
                  </div>
                  <svg
                    className={`w-4 h-4 text-slate-400 transition-transform ${financialOpen ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {financialOpen && (
                  <div className="pl-10 pr-3 py-1 space-y-1">
                    <a href="/#revenue-breakdown" className="block py-1.5 text-xs text-slate-500 hover:text-blue-600 font-medium">
                      Expected vs Actual
                    </a>
                    <a href="/#strategy-analytics" className="block py-1.5 text-xs text-slate-500 hover:text-blue-600 font-medium">
                      Strategy Analytics
                    </a>
                    <a href="/#cases-ledger" className="block py-1.5 text-xs text-slate-500 hover:text-blue-600 font-medium">
                      Transaction Ledger
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Integration & Settings */}
          <div>
            <span className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Integrations & Admin
            </span>
            <div className="mt-2 space-y-1">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <span>API Docs (FastAPI)</span>
                </div>
                <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>

              <div className="flex items-center justify-between px-3 py-2 rounded-xl text-xs text-slate-500 bg-slate-50">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Razorpay Mode
                </span>
                <span className="font-semibold text-slate-700 font-mono">TEST</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Promotional / Engine Banner */}
      <div className="p-4 m-4 rounded-2xl bg-slate-900 text-white relative overflow-hidden shadow-md">
        <div className="absolute -right-4 -bottom-4 w-20 h-20 bg-blue-500/20 rounded-full blur-xl pointer-events-none"></div>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 rounded-lg bg-blue-600 flex items-center justify-center text-white text-xs">
            ⚡
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
            Autonomous Engine
          </span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          AI-diagnosed recovery pipeline with 92.5% action precision and human-approval safety.
        </p>
        <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px]">
          <span className="text-emerald-400 font-semibold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            System Healthy
          </span>
          <span className="text-slate-400 font-mono">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
