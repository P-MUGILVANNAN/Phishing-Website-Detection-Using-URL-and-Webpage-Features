import React from 'react';
import { HealthInfo } from '../types';
import { Server, Activity, ShieldCheck, Cpu, Menu } from 'lucide-react';

interface Props {
  health: HealthInfo | null;
  activeTabTitle: string;
  onToggleMenu: () => void;
}

export const Navbar: React.FC<Props> = ({ health, activeTabTitle, onToggleMenu }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 sm:px-6 lg:px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3 min-w-0">
        {/* Mobile / Tablet Menu Button */}
        <button
          onClick={onToggleMenu}
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 border border-slate-800 transition-colors shrink-0"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5 text-cyan-400" />
        </button>

        <h2 className="text-sm sm:text-base font-semibold text-white tracking-tight truncate">
          {activeTabTitle}
        </h2>
      </div>

      <div className="flex items-center gap-2 sm:gap-3 text-xs shrink-0">
        {/* Backend status */}
        <div className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800">
          <Server className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="hidden sm:inline text-slate-400">Backend:</span>
          <span className={`font-mono font-medium ${health?.status === 'HEALTHY' ? 'text-emerald-400' : 'text-amber-400'}`}>
            <span className="sm:hidden">{health?.status === 'HEALTHY' ? 'OK' : 'ERR'}</span>
            <span className="hidden sm:inline">{health?.status || 'OFFLINE'}</span>
          </span>
        </div>

        {/* Model status */}
        <div className="hidden xs:flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800">
          <Cpu className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="hidden md:inline text-slate-400">Model:</span>
          <span className="font-mono text-cyan-300 truncate max-w-[90px] sm:max-w-none">
            {health?.model_loaded ? health.model_version || 'Loaded' : 'Untrained'}
          </span>
        </div>

        {/* Safe fetch indicator */}
        <div className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1.5 rounded-md bg-slate-900/60 border border-slate-800 text-slate-400" title="SSRF Protection Guard Active">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span className="hidden xl:inline text-[11px]">SSRF Protection Active</span>
          <span className="hidden sm:inline xl:hidden text-[11px]">SSRF Guard</span>
        </div>
      </div>
    </header>
  );
};
