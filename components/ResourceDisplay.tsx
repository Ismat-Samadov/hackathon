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
    <div className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 backdrop-blur-sm rounded-lg p-6 shadow-2xl border border-indigo-500/30">
      <h2 className="text-2xl font-bold mb-4 text-cyan-300">Resources</h2>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {Object.entries(resources).map(([key, value]) => (
          <div key={key} className="bg-black/30 rounded-lg p-3 border border-cyan-500/20 hover:border-cyan-500/50 transition-all">
            <div className="text-2xl mb-1">{resourceIcons[key as keyof Resources]}</div>
            <div className="text-sm text-gray-400 capitalize">{key}</div>
            <div className="text-xl font-bold text-cyan-300">
              {Math.floor(value).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
