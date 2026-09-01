"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

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
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const metricsRes = await fetch("http://localhost:8000/api/v1/dashboard/metrics");
      if (!metricsRes.ok) throw new Error("Failed to fetch metrics");
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);

      const casesRes = await fetch("http://localhost:8000/api/v1/recovery/cases");
      if (!casesRes.ok) throw new Error("Failed to fetch cases");
      const casesData = await casesRes.json();
      setCases(casesData.items);
      
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (minorUnits: number, currency: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
    }).format(minorUnits / 100);
  };

  if (loading) return <div className="p-12 text-center text-gray-500">Loading Dashboard...</div>;
  if (error) return <div className="p-12 text-center text-red-500">Error: {error}</div>;

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50">
      <div className="w-full max-w-6xl mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight">RecoverAI Dashboard</h1>
          <h2 className="text-lg text-gray-600 mt-2">Operations & Human Approval Layer</h2>
        </div>
        <button onClick={fetchData} className="px-4 py-2 bg-indigo-600 text-white rounded-md shadow hover:bg-indigo-700">
          Refresh Data
        </button>
      </div>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Revenue at Risk</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {formatCurrency(metrics?.revenue_at_risk || 0, 'INR')}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Recovered Revenue</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">
            {formatCurrency(metrics?.recovered_revenue || 0, 'INR')}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Pending Approvals</h3>
          <p className="text-3xl font-bold text-orange-600 mt-2">
            {metrics?.pending_approval || 0}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Total Cases</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {metrics?.total_cases || 0}
          </p>
        </div>
      </div>

      <div className="w-full max-w-6xl">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Recovery Cases</h3>

        {cases.length === 0 ? (
          <p className="text-gray-500">No cases found.</p>
        ) : (
          <div className="overflow-hidden bg-white shadow sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prob.</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Approval</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exec Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                      {c.payment_id.substring(0, 8)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(c.amount, c.currency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {c.error_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {c.recovery_probability !== null ? (c.recovery_probability * 100).toFixed(1) + '%' : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${c.approval_status === 'APPROVED' ? 'bg-green-100 text-green-800' : 
                          c.approval_status === 'REJECTED' ? 'bg-red-100 text-red-800' : 
                          c.approval_status === 'PENDING_APPROVAL' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-gray-100 text-gray-800'}`}>
                        {c.approval_status || 'NONE'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${c.status === 'recovered' ? 'bg-green-100 text-green-800' : 
                          c.status === 'failed' ? 'bg-red-100 text-red-800' : 
                          c.status === 'executing' ? 'bg-blue-100 text-blue-800' : 
                          'bg-gray-100 text-gray-800'}`}>
                        {c.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link href={`/recovery/${c.id}`} className="text-indigo-600 hover:text-indigo-900">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
