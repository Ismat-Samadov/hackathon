'use client';

import { Planet } from '@/lib/types';

interface PlanetCardProps {
  planet: Planet;
  onColonize: (planetId: string) => void;
  canAfford: boolean;
}

export default function PlanetCard({ planet, onColonize, canAfford }: PlanetCardProps) {
  const planetEmojis = {
    desert: '🏜️',
    ocean: '🌊',
    forest: '🌲',
    ice: '❄️',
    volcanic: '🌋',
    gas: '💨',
  };

  const sizeColors = {
    small: 'text-yellow-400',
    medium: 'text-orange-400',
    large: 'text-red-400',
  };

  return (
    <div className={`bg-gradient-to-br ${
      planet.colonized
        ? 'from-green-900/40 to-emerald-900/40 border-green-500/40'
        : 'from-gray-900/40 to-slate-900/40 border-gray-500/30'
    } backdrop-blur-sm rounded-lg p-4 shadow-xl border hover:scale-105 transition-transform`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-xl font-bold text-cyan-300">{planet.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-2xl">{planetEmojis[planet.type]}</span>
            <span className={`text-sm font-semibold ${sizeColors[planet.size]} capitalize`}>
              {planet.size}
            </span>
          </div>
        </div>
        {planet.colonized && (
          <div className="bg-green-500/20 px-2 py-1 rounded text-xs text-green-300 border border-green-500/40">
            Colonized
          </div>
        )}
      </div>

      <div className="space-y-2 mb-4">
        <div className="text-sm text-gray-400">
          <span className="text-yellow-400">⛏️</span> Minerals: +{planet.productionBonus.minerals}/s
        </div>
        <div className="text-sm text-gray-400">
          <span className="text-blue-400">⚡</span> Energy: +{planet.productionBonus.energy}/s
        </div>
        <div className="text-sm text-gray-400">
          <span className="text-green-400">🌾</span> Food: +{planet.productionBonus.food}/s
        </div>
        {planet.colonized && (
          <div className="text-sm text-cyan-400">
            👥 Population: {planet.population}
          </div>
        )}
      </div>

      {!planet.colonized && (
        <button
          onClick={() => onColonize(planet.id)}
          disabled={!canAfford}
          className={`w-full py-2 px-4 rounded-lg font-semibold transition-all ${
            canAfford
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/50'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          Colonize (500💰 300⛏️ 50👥)
        </button>
      )}
    </div>
  );
}
