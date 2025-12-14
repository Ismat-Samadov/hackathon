'use client';

import { Technology } from '@/lib/types';

interface TechnologyCardProps {
  tech: Technology;
  onResearch: (techId: string) => void;
  canAfford: boolean;
}

export default function TechnologyCard({ tech, onResearch, canAfford }: TechnologyCardProps) {
  const categoryEmojis = {
    production: '🏭',
    military: '🛡️',
    exploration: '🚀',
    social: '👨‍👩‍👧‍👦',
  };

  const categoryColors = {
    production: 'from-yellow-900/40 to-orange-900/40 border-yellow-500/40',
    military: 'from-red-900/40 to-pink-900/40 border-red-500/40',
    exploration: 'from-blue-900/40 to-cyan-900/40 border-blue-500/40',
    social: 'from-green-900/40 to-emerald-900/40 border-green-500/40',
  };

  return (
    <div className={`bg-gradient-to-br ${
      tech.researched
        ? 'from-purple-900/40 to-indigo-900/40 border-purple-500/40 opacity-75'
        : categoryColors[tech.category]
    } backdrop-blur-sm rounded-lg p-4 shadow-xl border hover:scale-105 transition-transform`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{categoryEmojis[tech.category]}</span>
          <div>
            <h3 className="text-lg font-bold text-cyan-300">{tech.name}</h3>
            <span className="text-xs text-gray-400 capitalize">{tech.category}</span>
          </div>
        </div>
        {tech.researched && (
          <div className="bg-purple-500/20 px-2 py-1 rounded text-xs text-purple-300 border border-purple-500/40">
            ✓ Complete
          </div>
        )}
      </div>

      <p className="text-sm text-gray-300 mb-3">{tech.description}</p>

      <div className="space-y-1 mb-4">
        {tech.effects.map((effect, idx) => (
          <div key={idx} className="text-xs text-green-400">
            ✓ {effect}
          </div>
        ))}
      </div>

      <div className="text-sm text-gray-400 mb-3">
        Cost: {tech.cost.credits}💰 {tech.cost.minerals}⛏️
      </div>

      {!tech.researched && (
        <button
          onClick={() => onResearch(tech.id)}
          disabled={!canAfford}
          className={`w-full py-2 px-4 rounded-lg font-semibold transition-all ${
            canAfford
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg shadow-purple-500/50'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          Research
        </button>
      )}
    </div>
  );
}
