'use client';

import { Resources } from '@/lib/types';

interface ResourceDisplayProps {
  resources: Resources;
}

export default function ResourceDisplay({ resources }: ResourceDisplayProps) {
  const resourceIcons = {
    credits: '💰',
    minerals: '⛏️',
    energy: '⚡',
    food: '🌾',
    population: '👥',
  };

  return (
    <div className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 backdrop-blur-md rounded-xl p-4 sm:p-6 shadow-2xl border border-indigo-500/30 hover:border-indigo-400/50 transition-all glow-purple">
      <h2 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-cyan-300">Resources</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-3 md:gap-4">
        {Object.entries(resources).map(([key, value]) => (
          <div
            key={key}
            className="bg-black/40 rounded-lg p-2 sm:p-3 border border-cyan-500/20 hover:border-cyan-500/60 hover:bg-black/60 transition-all hover:scale-105 active:scale-95"
          >
            <div className="text-xl sm:text-2xl mb-1">{resourceIcons[key as keyof Resources]}</div>
            <div className="text-xs sm:text-sm text-gray-400 capitalize truncate">{key}</div>
            <div className="text-base sm:text-lg md:text-xl font-bold text-cyan-300">
              {Math.floor(value).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
