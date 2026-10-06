import React, { useState, useEffect } from "react";
import { Cpu, Play, CheckCircle2, Clock, Activity, Zap, ShieldAlert } from "lucide-react";
import { api } from "../services/api";
import { StatCard } from "../components/StatCard";

export function ScaleTest() {
  const [status, setStatus] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [targetCount, setTargetCount] = useState(100);
  const [workerCount, setWorkerCount] = useState(15);

  const fetchStatus = async () => {
    try {
      const data = await api.getScaleTestStatus();
      setStatus(data);
      setIsRunning(data.is_running);
    } catch (err) {
      console.error("Failed to fetch scale test status:", err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 1000); // 1s polling while on page
    return () => clearInterval(interval);
  }, []);

  const handleStartTest = async () => {
    try {
      await api.startScaleTest({
        total_targets: targetCount,
        concurrent_workers: workerCount,
      });
      setIsRunning(true);
      fetchStatus();
    } catch (err) {
      alert(`Simulation failed to start: ${err.message}`);
    }
  };

  const progressPercent = status?.total_targets
    ? Math.round(((status.completed_tasks + status.failed_tasks) / status.total_targets) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Architecture & Overview Card */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#27272A]">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded font-mono text-[11px] font-bold bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20">
                SCALABILITY VERIFICATION
              </span>
              <span className="text-xs text-zinc-500">•</span>
              <span className="text-xs text-zinc-400">Worker Pool & Task Queue Architecture</span>
            </div>
            <h2 className="text-xl font-bold text-white mt-1">100-Website Concurrency Benchmark</h2>
            <p className="text-xs text-zinc-400 mt-1 max-w-2xl">
              Demonstrates asynchronous non-blocking ingestion across 100 competitor sites simultaneously. Slow or failing websites are isolated in independent worker fibers and never degrade the rest of the queue.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div>
                <label className="block text-[10px] text-zinc-400 font-semibold uppercase">Sites</label>
                <input
                  type="number"
                  min="10"
                  max="500"
                  value={targetCount}
                  onChange={(e) => setTargetCount(Number(e.target.value))}
                  disabled={isRunning}
                  className="w-20 bg-[#09090B] border border-zinc-700 rounded-lg px-2.5 py-1 text-xs text-white font-mono focus:outline-none focus:border-violet-500 disabled:opacity-50"
                />
              </div>

              <div>
                <label className="block text-[10px] text-zinc-400 font-semibold uppercase">Workers</label>
                <input
                  type="number"
                  min="2"
                  max="50"
                  value={workerCount}
                  onChange={(e) => setWorkerCount(Number(e.target.value))}
                  disabled={isRunning}
                  className="w-16 bg-[#09090B] border border-zinc-700 rounded-lg px-2.5 py-1 text-xs text-white font-mono focus:outline-none focus:border-violet-500 disabled:opacity-50"
                />
              </div>
            </div>

            <button
              onClick={handleStartTest}
              disabled={isRunning}
              className="mt-4 px-5 py-2.5 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-xl text-xs font-bold shadow-lg shadow-violet-600/30 transition flex items-center gap-2 disabled:opacity-50"
            >
              <Play className={`w-4 h-4 ${isRunning ? "animate-pulse" : ""}`} />
              <span>{isRunning ? "Simulating..." : "Launch 100-Site Test"}</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between items-center text-xs mb-2">
            <span className="font-semibold text-zinc-300">
              Benchmark Execution Progress ({progressPercent}%)
            </span>
            <span className="font-mono text-zinc-400">
              {(status?.completed_tasks ?? 0) + (status?.failed_tasks ?? 0)} / {status?.total_targets ?? targetCount} Sites
            </span>
          </div>
          <div className="w-full bg-[#09090B] rounded-full h-3 overflow-hidden border border-[#27272A]">
            <div
              className="bg-[#8B5CF6] h-full rounded-full transition-all duration-300 shadow-md shadow-violet-500/50"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <StatCard
          title="Queue Size"
          value={status?.queued_tasks ?? 0}
          icon={Activity}
          color="violet"
        />
        <StatCard
          title="Active Workers"
          value={status?.active_workers ?? 0}
          icon={Zap}
          color="amber"
          badge={`Limit: ${status?.concurrent_workers ?? workerCount}`}
        />
        <StatCard
          title="Completed"
          value={status?.completed_tasks ?? 0}
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Failures Isolated"
          value={status?.failed_tasks ?? 0}
          icon={ShieldAlert}
          color="rose"
        />
        <StatCard
          title="Avg Latency"
          value={`${status?.avg_response_time_ms ?? 0} ms`}
          icon={Clock}
          color="indigo"
        />
        <StatCard
          title="Throughput"
          value={`${status?.throughput_checks_per_sec ?? 0} /s`}
          icon={Cpu}
          color="violet"
        />
      </div>

      {/* Real-time Streaming Logs */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#27272A] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <h3 className="text-sm font-bold text-white tracking-tight">Live Worker Concurrency Stream</h3>
          </div>
          <span className="text-xs text-zinc-500 font-mono">Real-time Task Ingestion Log</span>
        </div>

        <div className="p-4 bg-[#09090B] font-mono text-xs max-h-80 overflow-y-auto space-y-1.5 divide-y divide-[#18181B]">
          {!status?.recent_logs || status.recent_logs.length === 0 ? (
            <div className="py-12 text-center text-zinc-600">
              No live test running. Click <strong>"Launch 100-Site Test"</strong> above to benchmark asynchronous workers!
            </div>
          ) : (
            status.recent_logs.map((log, idx) => (
              <div key={idx} className="pt-1.5 flex items-center justify-between gap-4 text-zinc-300">
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-zinc-500">[{log.timestamp}]</span>
                  <span className="text-[#8B5CF6] font-bold">Worker-{log.worker_id}</span>
                </div>

                <div className="truncate flex-1">
                  <span className="text-zinc-200">{log.site}</span>
                  <span className="text-zinc-500 ml-2">({log.strategy})</span>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-zinc-400">{log.response_time_ms} ms</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.status === "SUCCESS"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-rose-500/20 text-rose-400"
                    }`}
                  >
                    {log.status}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
