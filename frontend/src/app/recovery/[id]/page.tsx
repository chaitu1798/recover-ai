"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface CaseData {
  payment: {
    id: string;
    amount: number;
    currency: string;
    error_code: string;
    method: string | null;
  };
  case: {
    id: string;
    status: string;
    approval_status: string | null;
    recovery_probability: number | null;
    priority_level: string | null;
    priority_score: number | null;
    expected_recovery_value: number | null;
    approved_by: string | null;
    opened_at: string;
    rejected_by: string | null;
    rejection_reason: string | null;
  };
  decision: {
    id: string | null;
    recommended_action: string | null;
    confidence: number | null;
    diagnosis: string;
    reasoning: string | Record<string, unknown> | null;
    strategy: string | null;
    policy_checks: Record<string, unknown> | null;
  };
  action: {
    action_type: string | null;
    status: string | null;
  };
  audit_logs: Array<{
    action: string;
    actor: string;
    reason: string | null;
    timestamp: string;
  }>;
}

export default function CaseDetails() {
  const params = useParams();
  const caseId = params.id as string;

  const [data, setData] = useState<CaseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [reason, setReason] = useState("Looks good");

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/recovery/cases/${caseId}`);
      if (!res.ok) throw new Error("Failed to fetch case details");
      const result = await res.json();
      setData(result);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/recovery/${caseId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved_by: "operator", reason })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Approval failed");
      }
      await fetchData();
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert("Error: " + err.message);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    try {
      setActionLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/recovery/${caseId}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rejected_by: "operator", reason })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Rejection failed");
      }
      await fetchData();
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert("Error: " + err.message);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!data?.decision?.id) {
      alert("No decision available for execution.");
      return;
    }
    try {
      setActionLoading(true);
      const res = await fetch("http://localhost:8000/api/v1/recovery/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recovery_case_id: caseId,
          decision_id: data.decision.id,
          idempotency_key: `exec_${caseId}_${Date.now()}`
        })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || (d.error && d.error.message) || "Execution failed");
      }
      await fetchData();
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert("Execution Error: " + err.message);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (minorUnits: number | null | undefined, currency: string) => {
    if (minorUnits === undefined || minorUnits === null) return 'N/A';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency || 'INR',
    }).format(minorUnits / 100);
  };

  const getPlainTextReasoning = (reasoning: unknown): string => {
    if (!reasoning) return 'No reasoning provided.';

    let obj: unknown = reasoning;
    if (typeof reasoning === 'string') {
      try {
        obj = JSON.parse(reasoning);
      } catch {
        const stratMatch = reasoning.match(/['"]strategy_explanation['"]\s*:\s*['"]([^'"]+)['"]/);
        const prioMatch = reasoning.match(/['"]priority_explanation['"]\s*:\s*['"]([^'"]+)['"]/);
        const parts: string[] = [];
        if (stratMatch) parts.push(stratMatch[1]);
        if (prioMatch) parts.push(prioMatch[1]);
        if (parts.length > 0) return parts.join(' ');
        return reasoning;
      }
    }

    if (typeof obj === 'object' && obj !== null) {
      const record = obj as Record<string, unknown>;
      const inner = (record.reasoning || record) as Record<string, unknown> | string;
      const parts: string[] = [];

      if (typeof inner === 'string') {
        parts.push(inner);
      } else if (typeof inner === 'object' && inner !== null) {
        if (inner.strategy_explanation) {
          parts.push(String(inner.strategy_explanation));
        }
        if (inner.priority_explanation) {
          parts.push(String(inner.priority_explanation));
        }
      }

      if (parts.length > 0) {
        return parts.join(' ');
      }

      if (record.explanation) return String(record.explanation);
    }

    return String(reasoning);
  };

  if (loading) return <div className="p-12 text-center text-gray-500">Loading details...</div>;
  if (error) return <div className="p-12 text-center text-red-500">Error: {error}</div>;
  if (!data) return null;

  const normalizedApprovalStatus = data.case.approval_status ? data.case.approval_status.toUpperCase() : 'NOT_REQUIRED';
  const isPendingApproval = normalizedApprovalStatus === 'PENDING_APPROVAL';
  const isApproved = normalizedApprovalStatus === 'APPROVED';
  const isRejected = normalizedApprovalStatus === 'REJECTED';

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-50">
      <div className="w-full max-w-5xl mb-6">
        <Link href="/" className="text-indigo-600 hover:underline flex items-center gap-2">
          &larr; Back to Dashboard
        </Link>
      </div>

      <div className="w-full max-w-5xl bg-white shadow rounded-lg overflow-hidden border border-gray-200">
        <div className="px-6 py-5 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Case Details</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500 font-mono">{caseId}</p>
          </div>
          <div>
            <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full 
                        ${data.case.status === 'recovered' ? 'bg-green-100 text-green-800' : 
                          data.case.status === 'failed' ? 'bg-red-100 text-red-800' : 
                          data.case.status === 'executing' ? 'bg-blue-100 text-blue-800' : 
                          data.case.status === 'approved' ? 'bg-emerald-100 text-emerald-800' :
                          data.case.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'}`}>
              Status: {data.case.status.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="px-6 py-5 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 border-b pb-2">Payment Info</h4>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Payment ID</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono truncate">{data.payment.id}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Amount</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatCurrency(data.payment.amount, data.payment.currency)}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Failure Reason</dt>
                <dd className="mt-1 text-sm text-gray-900">{data.payment.error_code}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Method</dt>
                <dd className="mt-1 text-sm text-gray-900">{data.payment.method || 'N/A'}</dd>
              </div>
            </dl>
          </div>

          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 border-b pb-2">AI Analysis</h4>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Rec. Action</dt>
                <dd className="mt-1 text-sm text-gray-900 font-semibold">{data.decision.recommended_action || 'N/A'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Recovery Prob.</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {data.case.recovery_probability !== null && data.case.recovery_probability !== undefined
                    ? (data.case.recovery_probability * 100).toFixed(1) + '%'
                    : 'N/A'}
                </dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Expected Value</dt>
                <dd className="mt-1 text-sm text-gray-900 font-semibold text-green-600">
                  {data.case.expected_recovery_value !== null && data.case.expected_recovery_value !== undefined
                    ? formatCurrency(data.case.expected_recovery_value, data.payment.currency)
                    : 'N/A'}
                </dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Priority Level</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    data.case.priority_level?.toUpperCase() === 'HIGH' ? 'bg-red-100 text-red-800' :
                    data.case.priority_level?.toUpperCase() === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    data.case.priority_level?.toUpperCase() === 'LOW' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {data.case.priority_level || 'N/A'}
                  </span>
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Diagnosis</dt>
                <dd className="mt-1 text-sm text-gray-900">{data.decision.diagnosis}</dd>
              </div>
              {data.decision.reasoning && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Reasoning</dt>
                  <dd className="mt-1 text-sm text-gray-800 bg-gray-50 p-3 rounded border border-gray-200 leading-relaxed">
                    <p className="font-medium text-gray-900 mb-1">
                      {getPlainTextReasoning(data.decision.reasoning)}
                    </p>
                    <details className="mt-2 pt-2 border-t border-gray-200">
                      <summary className="text-xs text-indigo-600 hover:text-indigo-800 cursor-pointer font-medium select-none">
                        View Raw Reasoning JSON
                      </summary>
                      <pre className="mt-2 text-xs font-mono text-gray-700 bg-white p-2 rounded border border-gray-200 overflow-x-auto">
                        {typeof data.decision.reasoning === 'string'
                          ? data.decision.reasoning
                          : JSON.stringify(data.decision.reasoning, null, 2)}
                      </pre>
                    </details>
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Approval Section */}
        <div className="px-6 py-5 bg-gray-50 border-t border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Human Approval Layer</h4>
          
          <div className="mb-4 flex items-center gap-3">
            <span className="text-sm font-medium text-gray-500">Approval Status:</span>
            <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
              isApproved ? 'bg-green-100 text-green-800' :
              isRejected ? 'bg-red-100 text-red-800' :
              isPendingApproval ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'}`}>
              {normalizedApprovalStatus.replace(/_/g, ' ')}
            </span>
          </div>

          {isPendingApproval && (
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center p-4 bg-white rounded border border-gray-200">
              <input 
                type="text" 
                value={reason} 
                onChange={e => setReason(e.target.value)} 
                placeholder="Reason (optional)"
                className="border border-gray-300 rounded px-3 py-2 text-sm w-full sm:w-64"
              />
              <button 
                onClick={handleApprove} 
                disabled={actionLoading}
                className="bg-green-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                Approve Recovery
              </button>
              <button 
                onClick={handleReject} 
                disabled={actionLoading}
                className="bg-red-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                Reject Recovery
              </button>
            </div>
          )}
          {isApproved && (
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 p-4 bg-emerald-50 rounded border border-emerald-200">
              <div>
                <p className="text-sm text-emerald-900 font-medium">Approval Granted</p>
                <p className="text-xs text-emerald-700 mt-0.5">Approved by <span className="font-semibold">{data.case.approved_by || 'operator'}</span> on {new Date(data.case.opened_at).toLocaleString()}</p>
              </div>
              {data.case.status.toLowerCase() === 'approved' && (
                <button
                  onClick={handleExecute}
                  disabled={actionLoading}
                  className="bg-indigo-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
                >
                  {actionLoading ? "Executing..." : "Execute Recovery (Simulator)"}
                </button>
              )}
            </div>
          )}
          {isRejected && (
            <div className="p-4 bg-red-50 rounded border border-red-200">
              <p className="text-sm text-red-900 font-medium">Approval Rejected</p>
              <p className="text-xs text-red-700 mt-0.5">Rejected by <span className="font-semibold">{data.case.rejected_by || 'operator'}</span>: {data.case.rejection_reason || 'No reason specified'}</p>
            </div>
          )}
        </div>

        {/* Timeline */}
        <div className="px-6 py-5 border-t border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-4">Audit Timeline</h4>
          <ul className="space-y-4">
            {data.audit_logs.map((log, idx: number) => (
              <li key={idx} className="bg-gray-50 p-3 rounded border border-gray-100 flex flex-col sm:flex-row sm:justify-between sm:items-center">
                <div>
                  <p className="text-sm font-medium text-gray-900">{log.action.replace(/_/g, ' ')}</p>
                  <p className="text-xs text-gray-500">By {log.actor} • {log.reason || 'No reason provided'}</p>
                </div>
                <div className="text-xs text-gray-400 mt-2 sm:mt-0">
                  {new Date(log.timestamp).toLocaleString()}
                </div>
              </li>
            ))}
            {data.audit_logs.length === 0 && <p className="text-sm text-gray-500">No events recorded.</p>}
          </ul>
        </div>
      </div>
    </main>
  );
}
