import React from 'react';

interface Props {
  score: number;
  label?: string;
}

export const ScoreGauge: React.FC<Props> = ({ score, label }) => {
  const percentage = Math.round(score * 100);

  const getColor = (s: number) => {
    if (s < 0.3) return 'text-emerald-400 bg-emerald-500';
    if (s < 0.7) return 'text-amber-400 bg-amber-500';
    return 'text-rose-500 bg-rose-500';
  };

  const getBorderColor = (s: number) => {
    if (s < 0.3) return 'border-emerald-500/30';
    if (s < 0.7) return 'border-amber-500/30';
    return 'border-rose-500/30';
  };

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-slate-900/60 rounded-xl border border-slate-800">
      <div className="relative w-32 h-32 flex items-center justify-center">
        {/* Circular indicator container */}
        <div className={`w-28 h-28 rounded-full border-4 ${getBorderColor(score)} flex flex-col items-center justify-center bg-slate-950/80 shadow-lg`}>
          <span className="text-2xl font-bold tracking-tight text-white">{percentage}%</span>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Risk Score</span>
        </div>
      </div>
      {label && <p className="mt-2 text-xs text-slate-400 text-center font-medium">{label}</p>}
      <div className="w-full mt-3 bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${getColor(score).split(' ')[1]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="w-full flex justify-between text-[10px] font-mono text-slate-500 mt-1">
        <span>0.0 Legit</span>
        <span>0.30</span>
        <span>0.70</span>
        <span>1.0 Phish</span>
      </div>
    </div>
  );
};

