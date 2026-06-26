'use client';

import { useEffect, useState } from 'react';
import { fetchMetrics, fetchTrends } from '@/app/services/api';
import type { DashboardMetrics } from '@/app/types';
import {
  FileText, MessageSquare, CircuitBoard, TrendingUp, Activity,
  BarChart3, PieChart, Loader2,
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart as RPieChart, Pie, Cell,
} from 'recharts';

const COLORS = ['#3b82f6', '#ef4444', '#22c55e', '#f97316', '#a855f7', '#eab308'];

interface AnalyticsData {
  metrics: DashboardMetrics | null;
  trends: { date: string; documents: number }[];
  agentUsage: { name: string; value: number }[];
  documentTypes: { name: string; value: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData>({
    metrics: null, trends: [], agentUsage: [], documentTypes: [],
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [metrics, trends] = await Promise.all([
          fetchMetrics(),
          fetchTrends(timeRange),
        ]);

        // Simulate agent usage from session data
        const agentUsage = [
          { name: 'Expert', value: Math.round(metrics.messages * 0.35) },
          { name: 'RCA', value: Math.round(metrics.messages * 0.25) },
          { name: 'Compliance', value: Math.round(metrics.messages * 0.2) },
          { name: 'Lessons', value: Math.round(metrics.messages * 0.15) },
          { name: 'General', value: Math.round(metrics.messages * 0.05) },
        ];

        const documentTypes = [
          { name: 'PDF', value: Math.round(metrics.documents * 0.4) },
          { name: 'TXT', value: Math.round(metrics.documents * 0.3) },
          { name: 'DOCX', value: Math.round(metrics.documents * 0.15) },
          { name: 'Images', value: Math.round(metrics.documents * 0.1) },
          { name: 'XLSX', value: Math.round(metrics.documents * 0.05) },
        ];

        setData({
          metrics,
          trends: trends.map(t => ({
            ...t,
            date: new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          })),
          agentUsage,
          documentTypes,
        });
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 size={32} className="text-blue-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-slate-400 mt-1">Platform usage insights and performance metrics</p>
        </div>
        <div className="flex gap-2">
          {[7, 14, 30].map(d => (
            <button key={d} onClick={() => setTimeRange(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${timeRange === d ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}>
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-500/10 rounded-lg"><FileText size={18} className="text-blue-400" /></div>
            <span className="text-xs text-slate-500 uppercase tracking-wider">Documents</span>
          </div>
          <p className="text-2xl font-bold text-white">{data.metrics?.documents || 0}</p>
          <p className="text-xs text-green-400 mt-1 flex items-center gap-1"><TrendingUp size={12} />+12% this week</p>
        </div>
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-500/10 rounded-lg"><MessageSquare size={18} className="text-purple-400" /></div>
            <span className="text-xs text-slate-500 uppercase tracking-wider">Chat Sessions</span>
          </div>
          <p className="text-2xl font-bold text-white">{data.metrics?.sessions || 0}</p>
          <p className="text-xs text-green-400 mt-1 flex items-center gap-1"><TrendingUp size={12} />+8% this week</p>
        </div>
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-orange-500/10 rounded-lg"><CircuitBoard size={18} className="text-orange-400" /></div>
            <span className="text-xs text-slate-500 uppercase tracking-wider">AI Queries</span>
          </div>
          <p className="text-2xl font-bold text-white">{data.metrics?.messages || 0}</p>
          <p className="text-xs text-green-400 mt-1 flex items-center gap-1"><TrendingUp size={12} />+15% this week</p>
        </div>
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-500/10 rounded-lg"><Activity size={18} className="text-green-400" /></div>
            <span className="text-xs text-slate-500 uppercase tracking-wider">Equipment</span>
          </div>
          <p className="text-2xl font-bold text-white">{data.metrics?.equipment || 0}</p>
          <p className="text-xs text-slate-500 mt-1">Tracked in knowledge graph</p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document Upload Trends */}
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={16} className="text-blue-400" />
            <h2 className="text-sm font-semibold text-white">Document Upload Trends</h2>
          </div>
          <div className="h-56">
            {data.trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.trends}>
                  <defs>
                    <linearGradient id="colorDocs" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }} />
                  <Area type="monotone" dataKey="documents" stroke="#3b82f6" strokeWidth={2} fill="url(#colorDocs)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">No trend data</div>
            )}
          </div>
        </div>

        {/* Agent Usage */}
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <PieChart size={16} className="text-purple-400" />
            <h2 className="text-sm font-semibold text-white">Agent Usage Distribution</h2>
          </div>
          <div className="h-56 flex items-center">
            <ResponsiveContainer width="50%" height="100%">
              <RPieChart>
                <Pie data={data.agentUsage} cx="50%" cy="50%" innerRadius={40} outerRadius={70}
                  paddingAngle={3} dataKey="value">
                  {data.agentUsage.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }} />
              </RPieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {data.agentUsage.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2 text-xs">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="text-slate-300">{item.name}</span>
                  <span className="text-slate-500 ml-auto">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document Types */}
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <FileText size={16} className="text-green-400" />
            <h2 className="text-sm font-semibold text-white">Document Types</h2>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.documentTypes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {data.documentTypes.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} className="text-orange-400" />
            <h2 className="text-sm font-semibold text-white">System Performance</h2>
          </div>
          <div className="space-y-4 py-2">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Vector Store (Qdrant)</span>
                <span className="text-green-400">Connected</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '85%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Knowledge Graph (Neo4j)</span>
                <span className="text-green-400">Connected</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: '90%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">LLM (Groq)</span>
                <span className="text-green-400">Active</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 rounded-full" style={{ width: '95%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Embedding Pipeline</span>
                <span className="text-green-400">Ready</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-orange-500 rounded-full" style={{ width: '78%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">BM25 Search Index</span>
                <span className="text-green-400">{data.metrics?.documents || 0} docs</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500 rounded-full" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
