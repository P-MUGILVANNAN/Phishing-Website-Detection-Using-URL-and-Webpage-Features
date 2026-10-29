import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

interface Props {
  prediction?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<Props> = ({ prediction, size = 'md' }) => {
  const isPhish = prediction === 'Phishing';
  const isLegit = prediction === 'Legitimate';

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-2.5 py-1 gap-1.5',
    lg: 'text-base px-3.5 py-1.5 gap-2 font-medium',
  }[size];

  if (isPhish) {
    return (
      <span className={`inline-flex items-center rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 ${sizeClasses}`}>
        <ShieldAlert className="w-4 h-4 text-rose-400" />
        Likely Phishing
      </span>
    );
  }

  if (isLegit) {
    return (
      <span className={`inline-flex items-center rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 ${sizeClasses}`}>
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        Likely Legitimate
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 ${sizeClasses}`}>
      <AlertTriangle className="w-4 h-4 text-amber-400" />
      Suspicious / Uncertain
    </span>
  );
};

