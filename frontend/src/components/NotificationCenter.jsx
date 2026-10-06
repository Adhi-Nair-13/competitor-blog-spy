import React from "react";
import { X, Bell, CheckCheck, Clock, ArrowRight } from "lucide-react";
import { DelayBadge } from "./DelayBadge";

export function NotificationCenter({ isOpen, onClose, notifications, onMarkAllRead, onSelectArticle }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-[#09090B]/80 backdrop-blur-sm transition-opacity" 
        onClick={onClose} 
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-[#18181B] border-l border-[#27272A] shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-5 border-b border-[#27272A] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20">
                <Bell className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-white">Detection Notifications</h2>
                <p className="text-xs text-zinc-400">Live competitor article detection events</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={onMarkAllRead}
                title="Mark all as read"
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#27272A] transition text-xs flex items-center gap-1 font-medium"
              >
                <CheckCheck className="w-4 h-4" />
                <span className="hidden sm:inline">Mark read</span>
              </button>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#27272A] transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {notifications.length === 0 ? (
              <div className="text-center py-16 text-zinc-500">
                <Bell className="w-10 h-10 mx-auto text-zinc-600 stroke-[1.5] mb-2" />
                <p className="text-sm font-medium text-zinc-400">No new notifications</p>
                <p className="text-xs text-zinc-600 mt-1">Newly detected articles will show up here.</p>
              </div>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`p-4 rounded-xl border transition cursor-pointer ${
                    notif.is_read
                      ? "bg-[#18181B]/60 border-[#27272A]/80 opacity-80"
                      : "bg-[#27272A]/50 border-violet-500/30 hover:border-violet-500/60"
                  }`}
                  onClick={() => {
                    if (notif.article_id && onSelectArticle) {
                      onSelectArticle(notif.article_id);
                      onClose();
                    }
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-semibold text-[#8B5CF6]">
                      {notif.competitor_name || "Monitored Competitor"}
                    </span>
                    <span className="text-[11px] text-zinc-500 flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>

                  <p className="mt-1.5 text-sm font-medium text-zinc-200 line-clamp-2">
                    {notif.message}
                  </p>

                  <div className="mt-3 flex items-center justify-between pt-2 border-t border-[#27272A]/60">
                    <DelayBadge
                      delaySeconds={notif.detection_delay_seconds}
                      delayFormatted={notif.detection_delay_formatted}
                    />

                    {notif.article_id && (
                      <span className="text-xs font-medium text-[#8B5CF6] hover:text-violet-300 flex items-center gap-1">
                        View Article <ArrowRight className="w-3.5 h-3.5" />
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
