"use client";

import { useEffect, useState } from "react";

interface Case {
  id: string;
  payment_id: string;
  amount: number;
  currency: string;
  status: string;
  error_code: string;
  created_at: string;
}

export default function Home() {
  const [cases, setCases] = useState<Case[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/recovery/cases")
      .then((res) => res.json())
      .then((data) => setCases(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
          RecoverAI
        </h1>
        <h2 className="text-xl font-medium text-gray-600">
          Recovery Execution Simulator
        </h2>
      </div>

      <div className="w-full max-w-5xl">
        <h3 className="text-2xl font-semibold mb-4 text-gray-800">Recent Recovery Cases</h3>

        {cases.length === 0 ? (
          <p className="text-gray-500">No cases found.</p>
        ) : (
          <div className="overflow-hidden bg-white shadow sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Error Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cases.map((c) => (
                  <tr key={c.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${c.status === 'open' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-black">
                      {c.currency} {c.amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {c.error_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(c.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 px-3 py-1 rounded">
                        Simulate
                      </button>
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
