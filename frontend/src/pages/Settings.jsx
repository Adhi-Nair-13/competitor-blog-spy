import React, { useState, useEffect } from "react";
import { Save, CheckCircle2, Mail, Server } from "lucide-react";
import { api } from "../services/api";

export function Settings() {
  const [formData, setFormData] = useState({
    monitoring_interval_minutes: 5,
    request_timeout_seconds: 15,
    max_retries: 3,
    concurrent_workers: 10,
    user_agent: "",
    email_notifications_enabled: false,
    smtp_host: "",
    smtp_port: 587,
    smtp_user: "",
    alert_email_recipient: "",
    demo_mode: true,
  });

  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await api.getSettings();
        setFormData({
          monitoring_interval_minutes: data.monitoring_interval_minutes,
          request_timeout_seconds: data.request_timeout_seconds,
          max_retries: data.max_retries,
          concurrent_workers: data.concurrent_workers,
          user_agent: data.user_agent,
          email_notifications_enabled: data.email_notifications_enabled,
          smtp_host: data.smtp_host || "",
          smtp_port: data.smtp_port || 587,
          smtp_user: data.smtp_user || "",
          alert_email_recipient: data.alert_email_recipient || "",
          demo_mode: data.demo_mode,
        });
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.updateSettings(formData);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert(`Failed to save settings: ${err.message}`);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 border-b border-[#27272A]">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">System & Monitoring Configuration</h2>
            <p className="text-xs text-zinc-400">Configure polling frequencies, concurrency limits, and alert policies</p>
          </div>
          {savedSuccess && (
            <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20">
              <CheckCircle2 className="w-4 h-4" /> Settings Saved!
            </span>
          )}
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-6 text-xs">
          {/* Section: Monitoring Engine */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-[#8B5CF6] uppercase tracking-wider flex items-center gap-1.5">
              <Server className="w-4 h-4" /> Monitoring Scheduler
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-zinc-300 font-semibold mb-1">
                  Polling Interval (Minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={formData.monitoring_interval_minutes}
                  onChange={(e) =>
                    setFormData({ ...formData, monitoring_interval_minutes: Number(e.target.value) })
                  }
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-violet-500"
                />
                <span className="text-[11px] text-zinc-500 mt-1 block">Default: 5 minutes</span>
              </div>

              <div>
                <label className="block text-zinc-300 font-semibold mb-1">
                  Concurrent Worker Fiber Limit
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formData.concurrent_workers}
                  onChange={(e) =>
                    setFormData({ ...formData, concurrent_workers: Number(e.target.value) })
                  }
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-violet-500"
                />
                <span className="text-[11px] text-zinc-500 mt-1 block">Parallel website checks</span>
              </div>

              <div>
                <label className="block text-zinc-300 font-semibold mb-1">
                  HTTP Request Timeout (Seconds)
                </label>
                <input
                  type="number"
                  min="3"
                  max="60"
                  value={formData.request_timeout_seconds}
                  onChange={(e) =>
                    setFormData({ ...formData, request_timeout_seconds: Number(e.target.value) })
                  }
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-zinc-300 font-semibold mb-1">
                  Maximum Retries per Cycle
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={formData.max_retries}
                  onChange={(e) =>
                    setFormData({ ...formData, max_retries: Number(e.target.value) })
                  }
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-violet-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-zinc-300 font-semibold mb-1">
                Custom User-Agent Header
              </label>
              <input
                type="text"
                value={formData.user_agent}
                onChange={(e) => setFormData({ ...formData, user_agent: e.target.value })}
                className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          {/* Section: Email Notifications */}
          <div className="space-y-4 pt-6 border-t border-[#27272A]">
            <h3 className="text-xs font-bold text-[#8B5CF6] uppercase tracking-wider flex items-center gap-1.5">
              <Mail className="w-4 h-4" /> SMTP Email Alerts (Optional)
            </h3>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="emailToggle"
                checked={formData.email_notifications_enabled}
                onChange={(e) =>
                  setFormData({ ...formData, email_notifications_enabled: e.target.checked })
                }
                className="rounded border-zinc-700 bg-zinc-900 text-violet-600"
              />
              <label htmlFor="emailToggle" className="text-zinc-300 font-medium">
                Dispatch email notification when new articles are detected
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-zinc-300 font-semibold mb-1">SMTP Host</label>
                <input
                  type="text"
                  placeholder="smtp.mailtrap.io"
                  value={formData.smtp_host}
                  onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-zinc-300 font-semibold mb-1">Alert Recipient Email</label>
                <input
                  type="email"
                  placeholder="team@example.com"
                  value={formData.alert_email_recipient}
                  onChange={(e) => setFormData({ ...formData, alert_email_recipient: e.target.value })}
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-violet-500"
                />
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-[#27272A] flex justify-end">
            <button
              type="submit"
              className="px-6 py-2.5 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-xl text-xs font-bold shadow-lg shadow-violet-600/30 transition flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>Save Configuration</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
