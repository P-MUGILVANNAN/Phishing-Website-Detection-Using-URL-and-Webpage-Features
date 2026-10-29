import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { ScannerPage } from './pages/ScannerPage';
import { BatchPage } from './pages/BatchPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { FeaturesPage } from './pages/FeaturesPage';
import { DatasetPage } from './pages/DatasetPage';
import { HistoryPage } from './pages/HistoryPage';
import { api } from './services/api';
import { HealthInfo } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [scanTargetUrl, setScanTargetUrl] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    checkHealth();
    const timer = setInterval(checkHealth, 30000);
    return () => clearInterval(timer);
  }, []);

  const checkHealth = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      setHealth(null);
    }
  };

  const handleScanUrlFromExternal = (url: string) => {
    setScanTargetUrl(url);
    setActiveTab('scanner');
  };

  const tabTitles: Record<string, string> = {
    dashboard: 'Overview Dashboard',
    scanner: 'URL Threat & Phishing Scanner',
    batch: 'Batch URL Processing',
    evaluation: 'Robustness & Generalization Benchmarks',
    features: 'Feature Importance & Multi-Modal XAI',
    dataset: 'Dataset Validation & Model Training',
    history: 'Prediction History & Audit Logs',
  };

  return (
    <div className="flex min-h-screen bg-[#070b12] text-slate-100 overflow-x-hidden">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0 w-full overflow-hidden">
        <Navbar
          health={health}
          activeTabTitle={tabTitles[activeTab] || 'PhishGuard AI'}
          onToggleMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        />
        <main className="flex-1 overflow-y-auto w-full">
          {activeTab === 'dashboard' && (
            <DashboardPage
              onScanUrl={handleScanUrlFromExternal}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}
          {activeTab === 'scanner' && <ScannerPage initialUrl={scanTargetUrl} />}
          {activeTab === 'batch' && <BatchPage />}
          {activeTab === 'evaluation' && <EvaluationPage />}
          {activeTab === 'features' && <FeaturesPage />}
          {activeTab === 'dataset' && <DatasetPage />}
          {activeTab === 'history' && <HistoryPage />}
        </main>
      </div>
    </div>
  );
};

export default App;
