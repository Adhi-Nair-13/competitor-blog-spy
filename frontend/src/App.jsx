import React, { useState, useEffect } from "react";
import { Sidebar } from "./components/Sidebar";
import { Navbar } from "./components/Navbar";
import { NotificationCenter } from "./components/NotificationCenter";
import { Dashboard } from "./pages/Dashboard";
import { Competitors } from "./pages/Competitors";
import { Articles } from "./pages/Articles";
import { MonitoringHistory } from "./pages/MonitoringHistory";
import { Analytics } from "./pages/Analytics";
import { ScaleTest } from "./pages/ScaleTest";
import { DemoControl } from "./pages/DemoControl";
import { Settings } from "./pages/Settings";
import { ArticleDetailModal } from "./pages/ArticleDetailModal";
import { api } from "./services/api";

export default function App() {
  const [currentTab, setCurrentTab] = useState("dashboard");
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedArticleId, setSelectedArticleId] = useState(null);

  // Notifications
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Global Actions State
  const [isCheckingAll, setIsCheckingAll] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);

  const fetchNotifications = async () => {
    try {
      const [notifsData, countData] = await Promise.all([
        api.getNotifications(30),
        api.getUnreadCount(),
      ]);
      setNotifications(notifsData);
      setUnreadCount(countData.unread_count);
    } catch (err) {
      // Quiet fail if backend temporarily starting
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 12000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerRunAll = async () => {
    try {
      setIsCheckingAll(true);
      await api.runAllChecks();
      setTimeout(async () => {
        await fetchNotifications();
        setIsCheckingAll(false);
      }, 2000);
    } catch (err) {
      alert(`Could not trigger checks: ${err.message}`);
      setIsCheckingAll(false);
    }
  };

  const handleSeedDemo = async () => {
    try {
      setIsSeeding(true);
      const res = await api.seedDemoCompetitor();
      alert(`✅ Demo competitor configured! Discovered sources and initialized monitoring.`);
      await fetchNotifications();
      setCurrentTab("dashboard");
    } catch (err) {
      alert(`Could not seed demo competitor: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setUnreadCount(0);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-[#09090B] text-zinc-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Navbar */}
        <Navbar
          currentTab={currentTab}
          onOpenNotifications={() => setIsNotifOpen(true)}
          unreadCount={unreadCount}
          onTriggerRunAll={handleTriggerRunAll}
          isCheckingAll={isCheckingAll}
          onSeedDemo={handleSeedDemo}
          isSeeding={isSeeding}
        />

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#09090B]">
          {currentTab === "dashboard" && (
            <Dashboard
              onNavigate={setCurrentTab}
              onSelectArticle={setSelectedArticleId}
              onAddCompetitorClick={() => {
                setCurrentTab("competitors");
                setIsAddModalOpen(true);
              }}
            />
          )}

          {currentTab === "competitors" && (
            <Competitors
              isAddModalOpen={isAddModalOpen}
              setIsAddModalOpen={setIsAddModalOpen}
            />
          )}

          {currentTab === "articles" && (
            <Articles initialArticleId={selectedArticleId} />
          )}

          {currentTab === "history" && <MonitoringHistory />}

          {currentTab === "analytics" && <Analytics />}

          {currentTab === "scale-test" && <ScaleTest />}

          {currentTab === "demo-control" && (
            <DemoControl
              onNavigate={setCurrentTab}
              onSelectArticle={setSelectedArticleId}
            />
          )}

          {currentTab === "settings" && <Settings />}
        </main>
      </div>

      {/* Global Notifications Slide-over Drawer */}
      <NotificationCenter
        isOpen={isNotifOpen}
        onClose={() => setIsNotifOpen(false)}
        notifications={notifications}
        onMarkAllRead={handleMarkAllRead}
        onSelectArticle={(id) => {
          setSelectedArticleId(id);
          setCurrentTab("articles");
        }}
      />

      {/* Reader Modal */}
      {selectedArticleId && (
        <ArticleDetailModal
          articleId={selectedArticleId}
          onClose={() => setSelectedArticleId(null)}
        />
      )}
    </div>
  );
}
