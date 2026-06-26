'use client';

import { useEffect, useState } from 'react';
import { fetchMetrics, fetchTrends, listDocuments } from '@/app/services/api';
import type { DashboardMetrics } from '@/app/types';
import {
  FileText,
  MessageSquare,
  CircuitBoard,
  HardDrive,
  TrendingUp,
  TrendingDown,
  Clock,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface TrendPoint {
  name: string;
  value: number;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: 'bg-green-500/20 text-green-400',
    processing: 'bg-yellow-500/20 text-yellow-400',
    failed: 'bg-red-500/20 text-red-400',
    uploaded: 'bg-blue-500/20 text-blue-400',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-slate-500/20 text-slate-400'}`}>
      {status}
    </span>
  );
}

function StatCard({ icon: Icon, label, value, trend }: { icon: React.ElementType; label: string; value: number | string; trend?: 'up' | 'down' }) {
  return (
    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-blue-500/10 rounded-lg">
          <Icon size={20} className="text-blue-400" />
        </div>
        {trend && (
          <span className={`flex items-center gap-1 text-xs font-medium ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
            {trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            12%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-sm text-slate-400 mt-1">{label}</p>
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800 animate-pulse">
      <div className="w-10 h-10 bg-slate-800 rounded-lg mb-4" />
      <div className="h-8 w-16 bg-slate-800 rounded mb-2" />
      <div className="h-4 w-24 bg-slate-800 rounded" />
    </div>
  );
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [data, trends] = await Promise.all([fetchMetrics(), fetchTrends(7)]);
        if (!cancelled) {
          setMetrics(data);
          setTrendData(
            trends.length > 0
              ? trends.map((t) => ({ name: new Date(t.date).toLocaleDateString('en-US', { weekday: 'short' }), value: t.documents }))
              : []
          );
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load metrics');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-8 max-w-md">
          <p className="text-red-400 font-medium mb-2">Failed to load dashboard</p>
          <p className="text-sm text-slate-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg text-sm hover:bg-red-500/30 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1">Overview of your industrial intelligence platform</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : metrics ? (
          <>
            <StatCard icon={FileText} label="Total Documents" value={metrics.documents} trend="up" />
            <StatCard icon={MessageSquare} label="Active Sessions" value={metrics.sessions} />
            <StatCard icon={CircuitBoard} label="Chat Messages" value={metrics.messages} trend="up" />
            <StatCard icon={HardDrive} label="Equipment Tracked" value={metrics.equipment} />
          </>
        ) : null}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <h2 className="text-lg font-semibold text-white mb-4">Weekly Activity</h2>
          <div className="h-64">
            {trendData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">No trend data yet</div>
            ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2f8ef5" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2f8ef5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f1f5f9',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#2f8ef5"
                  strokeWidth={2}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Uploads</h2>
          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-12 bg-slate-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : metrics && metrics.recent_documents.length > 0 ? (
            <div className="space-y-3">
              {metrics.recent_documents.slice(0, 5).map((doc, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
                  <div className="flex items-center gap-3 min-w-0">
                    <FileText size={16} className="text-slate-500 shrink-0" />
                    <span className="text-sm text-slate-300 truncate">{doc.name}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-slate-500">{formatSize(doc.size)}</span>
                    <StatusBadge status={doc.status} />
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock size={12} />
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <FileText size={32} className="mb-2" />
              <p className="text-sm">No documents uploaded yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
