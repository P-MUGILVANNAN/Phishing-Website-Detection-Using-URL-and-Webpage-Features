import React from 'react';
import {
  LayoutDashboard,
  ShieldAlert,
  Layers,
  BarChart3,
  Cpu,
  Database,
  History,
  Shield,
  FileCheck2,
  X,
} from 'lucide-react';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<Props> = ({ activeTab, setActiveTab, isOpen, onClose }) => {
  const navItems = [
    { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'scanner', label: 'URL Scanner', icon: ShieldAlert },
    { id: 'batch', label: 'Batch Analysis', icon: Layers },
    { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
    { id: 'features', label: 'Feature Analysis', icon: Cpu },
    { id: 'dataset', label: 'Dataset & Training', icon: Database },
    { id: 'history', label: 'Prediction History', icon: History },
  ];

  const handleSelect = (id: string) => {
    setActiveTab(id);
    onClose();
  };

  const navContent = (
    <div className="flex flex-col justify-between h-full">
      <div>
        {/* Brand header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-wide text-white uppercase">PhishGuard AI</h1>
              <p className="text-[11px] text-cyan-400/80 font-mono">XGBoost & NLP Research</p>
            </div>
          </div>
          {/* Close button on mobile/tablet */}
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelect(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/50">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <FileCheck2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="truncate">SSRF-Safe / Domain Disjoint</span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1">Research Defense Prototype v1.0.0</p>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 bg-slate-950 border-r border-slate-800 flex-col justify-between shrink-0 h-screen sticky top-0 z-20">
        {navContent}
      </aside>

      {/* Mobile/Tablet Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Mobile/Tablet Drawer */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-slate-950 border-r border-slate-800 transform transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        }`}
      >
        {navContent}
      </div>
    </>
  );
};
