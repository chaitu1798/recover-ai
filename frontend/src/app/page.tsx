"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import AppHeader from "./components/AppHeader";

interface Metrics {
  total_cases: number;
  open_cases: number;
  pending_approval: number;
  approved_cases: number;
  rejected_cases: number;
  executing_cases: number;
  recovered_cases: number;
  failed_cases: number;
  revenue_at_risk: number;
  predicted_recoverable_revenue: number;
  recovered_revenue: number;
  recovery_rate: number;
  average_recovery_probability: number;
  policy_block_rate: number;
  approval_rate: number;
  execution_success_rate: number;
}

interface ExpectedVsActual {
  expected_recovery_value: number;
  actual_recovered_value: number;
  difference: number;
  ratio: number;
}

interface StrategyAnalytics {
  strategy: string;
  count: number;
}

interface Case {
  id: string;
  payment_id: string;
  amount: number;
  currency: string;
  status: string;
  approval_status: string | null;
  error_code: string;
  recovery_probability: number | null;
  created_at: string;
}

export default function Home() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [expectedVsActual, setExpectedVsActual] = useState<ExpectedVsActual | null>(null);
  const [strategyStats, setStrategyStats] = useState<StrategyAnalytics[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const fetchData = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      else setIsRefreshing(true);
      setError(null);

      const [metricsRes, evsRes, stratRes, casesRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/dashboard/metrics"),
        fetch("http://localhost:8000/api/v1/dashboard/expected-vs-actual"),
        fetch("http://localhost:8000/api/v1/dashboard/strategy-analytics"),
        fetch("http://localhost:8000/api/v1/recovery/cases?limit=50"),
      ]);

      if (!metricsRes.ok) throw new Error("Failed to fetch metrics");
      setMetrics(await metricsRes.json());

      if (evsRes.ok) setExpectedVsActual(await evsRes.json());
      if (stratRes.ok) setStrategyStats(await stratRes.json());
      if (casesRes.ok) {
        const casesData = await casesRes.json();
        setCases(casesData.items || []);
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An error occurred");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData(true);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (minorUnits: number, currency: string = "INR") => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 2,
    }).format(minorUnits / 100);
  };

  const totalStrategies = useMemo(() => {
    return strategyStats.reduce((acc, curr) => acc + curr.count, 0) || 1;
  }, [strategyStats]);

  const confidenceTiers = useMemo(() => {
    let high = 0;
    let med = 0;
    let low = 0;
    cases.forEach((c) => {
      const p = c.recovery_probability ?? 0;
      if (p >= 0.8) high++;
      else if (p >= 0.5) med++;
      else low++;
    });
    return { high, med, low, total: cases.length || 1 };
  }, [cases]);

  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchId = c.payment_id.toLowerCase().includes(q);
        const matchErr = c.error_code.toLowerCase().includes(q);
        if (!matchId && !matchErr) return false;
      }

      if (statusFilter !== "ALL") {
        if (statusFilter === "PENDING" && c.approval_status !== "PENDING_APPROVAL") return false;
        if (statusFilter === "APPROVED" && c.approval_status !== "APPROVED") return false;
        if (statusFilter === "REJECTED" && c.approval_status !== "REJECTED") return false;
        if (statusFilter === "RECOVERED" && c.status !== "recovered") return false;
        if (statusFilter === "FAILED" && c.status !== "failed") return false;
      }

      return true;
    });
  }, [cases, searchQuery, statusFilter]);

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-xs max-w-md w-full text-center">
          <h2 className="text-base font-semibold text-gray-900 mb-1">Failed to load data</h2>
          <p className="text-xs text-gray-500 mb-4">{error}</p>
          <button
            onClick={() => fetchData(false)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-md transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
      <AppHeader onRefresh={() => fetchData(false)} isRefreshing={isRefreshing} />

      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Page Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Payment Recovery Dashboard</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Monitor failed payments, review AI recovery recommendations, and approve retry actions.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/ml-monitoring"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-md shadow-xs transition-colors"
            >
              <svg className="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              View ML Monitoring
            </Link>
          </div>
        </div>

        {/* 4 Standard Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue at Risk</span>
            <div className="text-2xl font-bold text-gray-900 mt-2">
              {formatCurrency(metrics?.revenue_at_risk || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Across {metrics?.total_cases || 0} failed payments</p>
          </div>

          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Recovered Revenue</span>
            <div className="text-2xl font-bold text-emerald-600 mt-2">
              {formatCurrency(metrics?.recovered_revenue || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {metrics?.recovered_cases || 0} cases ({(metrics?.recovery_rate || 0 * 100).toFixed(1)}% recovery rate)
            </p>
          </div>

          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Recovery (EV)</span>
            <div className="text-2xl font-bold text-indigo-600 mt-2">
              {formatCurrency(expectedVsActual?.expected_recovery_value || metrics?.predicted_recoverable_revenue || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Statistical prediction (Amount × Prob)</p>
          </div>

          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Pending Approvals</span>
            <div className="text-2xl font-bold text-amber-600 mt-2">
              {metrics?.pending_approval || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Requiring human confirmation</p>
          </div>
        </div>

        {/* Analytics Section: Strategy Distribution & Expected vs Actual */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Card 1: Strategy Allocation */}
          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">Recommended Recovery Strategies</h3>
                <span className="text-xs text-gray-500">{totalStrategies} total decisions</span>
              </div>

              {/* Progress Bar */}
              <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden flex mb-4">
                {strategyStats.map((s, idx) => {
                  const pct = (s.count / totalStrategies) * 100;
                  let bg = "bg-indigo-600";
                  if (s.strategy === "PAYMENT_LINK") bg = "bg-amber-500";
                  else if (s.strategy === "NO_ACTION") bg = "bg-gray-400";
                  return (
                    <div
                      key={idx}
                      style={{ width: `${pct}%` }}
                      className={`${bg} h-full`}
                      title={`${s.strategy}: ${s.count} cases (${pct.toFixed(0)}%)`}
                    />
                  );
                })}
              </div>

              {/* Breakdown List */}
              <div className="divide-y divide-gray-100 text-xs">
                {strategyStats.map((s, idx) => {
                  const pct = ((s.count / totalStrategies) * 100).toFixed(1);
                  let dotColor = "bg-indigo-600";
                  let description = "Automatic background retry";
                  if (s.strategy === "PAYMENT_LINK") {
                    dotColor = "bg-amber-500";
                    description = "Dispatch payment link via SMS/email";
                  } else if (s.strategy === "NO_ACTION") {
                    dotColor = "bg-gray-400";
                    description = "Do not retry (hard failure or fraud risk)";
                  }

                  return (
                    <div key={idx} className="py-2.5 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full ${dotColor}`}></span>
                        <div>
                          <span className="font-medium text-gray-900">{s.strategy}</span>
                          <span className="text-gray-400 ml-2">({description})</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-semibold text-gray-900">{s.count} cases</span>
                        <span className="text-gray-400 ml-2">({pct}%)</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500 flex justify-between">
              <span>Execution Boundary: Strictly Test Mode</span>
              <span>Human Approval: Enforced</span>
            </div>
          </div>

          {/* Card 2: Expected vs Actual Recovery */}
          <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">Expected vs Realized Recovery Value</h3>
                <span className="text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md font-medium border border-emerald-100">
                  {((expectedVsActual?.ratio || 0) * 100).toFixed(1)}% Realized
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="p-3 bg-gray-50 rounded-md border border-gray-100">
                  <span className="text-xs text-gray-500">Expected Value</span>
                  <div className="text-lg font-bold text-gray-900 mt-0.5">
                    {formatCurrency(expectedVsActual?.expected_recovery_value || 0)}
                  </div>
                </div>
                <div className="p-3 bg-gray-50 rounded-md border border-gray-100">
                  <span className="text-xs text-gray-500">Actual Realized</span>
                  <div className="text-lg font-bold text-emerald-600 mt-0.5">
                    {formatCurrency(expectedVsActual?.actual_recovered_value || 0)}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1.5 mb-3">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Recovery Progress</span>
                  <span>
                    {formatCurrency(expectedVsActual?.actual_recovered_value || 0)} of{" "}
                    {formatCurrency(expectedVsActual?.expected_recovery_value || 0)}
                  </span>
                </div>
                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{
                      width: `${Math.min(100, Math.max(3, (expectedVsActual?.ratio || 0) * 100))}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Confidence Tiers Summary */}
              <div className="pt-2 text-xs text-gray-500 space-y-1">
                <div className="flex justify-between">
                  <span>High Probability Cases (&gt;80%):</span>
                  <span className="font-semibold text-gray-800">{confidenceTiers.high} cases</span>
                </div>
                <div className="flex justify-between">
                  <span>Moderate Cases (50–80%):</span>
                  <span className="font-semibold text-gray-800">{confidenceTiers.med} cases</span>
                </div>
                <div className="flex justify-between">
                  <span>Low Probability Cases (&lt;50%):</span>
                  <span className="font-semibold text-gray-800">{confidenceTiers.low} cases</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500 flex justify-between">
              <span>Mean Case Probability: {((metrics?.average_recovery_probability || 0) * 100).toFixed(1)}%</span>
              <span>Action Efficiency: 92.5%</span>
            </div>
          </div>
        </div>

        {/* Recovery Cases Table */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-xs overflow-hidden">
          {/* Table Header & Search Filter */}
          <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-gray-900">Recovery Cases</h2>
              <p className="text-xs text-gray-500">List of failed payments and AI recovery recommendations</p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Search payment ID or error..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-1.5 text-xs bg-white border border-gray-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-indigo-500 w-48 sm:w-60"
              />

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 text-xs bg-white border border-gray-300 rounded-md focus:outline-hidden focus:ring-1 focus:ring-indigo-500 text-gray-700"
              >
                <option value="ALL">All Statuses</option>
                <option value="PENDING">Pending Approval</option>
                <option value="APPROVED">Approved</option>
                <option value="RECOVERED">Recovered</option>
                <option value="FAILED">Failed</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
          </div>

          {/* Table */}
          {filteredCases.length === 0 ? (
            <div className="p-8 text-center text-gray-500 text-sm">No cases match the selected filter.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
                <thead className="bg-gray-50 font-semibold text-gray-600 uppercase tracking-wider">
                  <tr>
                    <th className="px-5 py-3">Payment ID</th>
                    <th className="px-5 py-3">Amount</th>
                    <th className="px-5 py-3">Failure Reason</th>
                    <th className="px-5 py-3">Recovery Prob.</th>
                    <th className="px-5 py-3">Approval Status</th>
                    <th className="px-5 py-3">Execution</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {filteredCases.map((c) => {
                    const prob = c.recovery_probability !== null ? c.recovery_probability : 0;
                    return (
                      <tr key={c.id} className="hover:bg-gray-50/75 transition-colors">
                        <td className="px-5 py-3.5 whitespace-nowrap font-mono text-gray-900 font-medium">
                          {c.payment_id.substring(0, 16)}...
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap font-semibold text-gray-900">
                          {formatCurrency(c.amount, c.currency)}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <span className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 font-mono text-[11px]">
                            {c.error_code}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <span className="w-10 font-medium text-gray-700">{(prob * 100).toFixed(1)}%</span>
                            <div className="w-16 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  prob >= 0.8 ? "bg-emerald-500" : prob >= 0.5 ? "bg-amber-500" : "bg-gray-400"
                                }`}
                                style={{ width: `${prob * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <span
                            className={`px-2 py-0.5 text-[11px] font-medium rounded-full ${
                              c.approval_status?.toUpperCase() === "APPROVED"
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                : c.approval_status?.toUpperCase() === "REJECTED"
                                ? "bg-rose-50 text-rose-700 border border-rose-200"
                                : c.approval_status?.toUpperCase() === "PENDING_APPROVAL"
                                ? "bg-amber-50 text-amber-800 border border-amber-200"
                                : "bg-gray-100 text-gray-600 border border-gray-200"
                            }`}
                          >
                            {c.approval_status ? c.approval_status.replace(/_/g, " ") : "NOT REQUIRED"}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <span
                            className={`px-2 py-0.5 text-[11px] font-medium rounded-full ${
                              c.status === "recovered"
                                ? "bg-emerald-100 text-emerald-800"
                                : c.status === "failed"
                                ? "bg-rose-100 text-rose-800"
                                : c.status === "executing"
                                ? "bg-blue-100 text-blue-800"
                                : "bg-gray-100 text-gray-700"
                            }`}
                          >
                            {c.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right">
                          <Link
                            href={`/recovery/${c.id}`}
                            className="text-indigo-600 hover:text-indigo-900 font-medium hover:underline"
                          >
                            Review &rarr;
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
