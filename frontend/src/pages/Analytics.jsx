import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { RefreshCw, BarChart3, PieChart as PieIcon, TrendingUp, ShieldCheck } from "lucide-react";
import { api } from "../services/api";

const PIE_COLORS = ["#8B5CF6", "#6366F1", "#10B981", "#F59E0B", "#EC4899"];

export function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between bg-[#18181B] p-4 rounded-xl border border-[#27272A]">
        <div>
          <h2 className="text-sm font-bold text-white tracking-tight">Performance Analytics & Intelligence</h2>
          <p className="text-xs text-zinc-400">Quantitative evaluation of detection speeds, method effectiveness, and health</p>
        </div>
        <button
          onClick={loadAnalytics}
          className="p-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition"
          title="Refresh Analytics"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Detection Time Over Time / Daily Articles */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-[#8B5CF6]" />
            <h3 className="text-sm font-bold text-white">Articles Detected & Average Delay Trend</h3>
          </div>
          <div className="h-64 text-xs font-mono">
            {data?.detection_trend?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.detection_trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="date" stroke="#71717A" />
                  <YAxis stroke="#71717A" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181B", borderColor: "#27272A", borderRadius: "8px", color: "#F4F4F5" }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="articles_detected"
                    name="Articles Detected"
                    stroke="#8B5CF6"
                    strokeWidth={2}
                    activeDot={{ r: 6 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="avg_delay_seconds"
                    name="Avg Delay (s)"
                    stroke="#F59E0B"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500">
                No trend data available yet.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Detection Method Distribution */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <PieIcon className="w-4 h-4 text-[#6366F1]" />
            <h3 className="text-sm font-bold text-white">Detection Method Distribution</h3>
          </div>
          <div className="h-64 text-xs">
            {data?.method_distribution?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.method_distribution}
                    dataKey="count"
                    nameKey="method"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {data.method_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181B", borderColor: "#27272A", borderRadius: "8px", color: "#F4F4F5" }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500">
                No articles captured yet to calculate distribution.
              </div>
            )}
          </div>
        </div>

        {/* Chart 3: Average Delay By Competitor */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-[#8B5CF6]" />
            <h3 className="text-sm font-bold text-white">Average Detection Delay by Competitor (Seconds)</h3>
          </div>
          <div className="h-64 text-xs font-mono">
            {data?.avg_delay_by_competitor?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.avg_delay_by_competitor}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="competitor_name" stroke="#71717A" />
                  <YAxis stroke="#71717A" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181B", borderColor: "#27272A", borderRadius: "8px", color: "#F4F4F5" }}
                  />
                  <Bar dataKey="avg_delay_seconds" name="Avg Delay (s)" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500">
                No competitor delay data recorded yet.
              </div>
            )}
          </div>
        </div>

        {/* Chart 4: Successful vs Failed Checks */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Monitoring Check Reliability</h3>
          </div>
          <div className="h-64 text-xs font-mono">
            {data?.checks_distribution?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.checks_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="status" stroke="#71717A" />
                  <YAxis stroke="#71717A" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181B", borderColor: "#27272A", borderRadius: "8px", color: "#F4F4F5" }}
                  />
                  <Bar dataKey="count" name="Count" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500">
                No check records found yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
