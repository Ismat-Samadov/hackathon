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
        ? 'from-green-900/40 to-emerald-900/40 border-green-500/40 glow-green'
        : 'from-gray-900/40 to-slate-900/40 border-gray-500/30'
    } backdrop-blur-md rounded-xl p-3 sm:p-4 shadow-xl border hover:scale-105 active:scale-100 transition-all duration-300`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg sm:text-xl font-bold text-cyan-300 truncate">{planet.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xl sm:text-2xl">{planetEmojis[planet.type]}</span>
            <span className={`text-xs sm:text-sm font-semibold ${sizeColors[planet.size]} capitalize`}>
              {planet.size}
            </span>
          </div>
        </div>
        {planet.colonized && (
          <div className="bg-green-500/20 px-2 py-1 rounded text-xs text-green-300 border border-green-500/40 ml-2 shrink-0 animate-pulse">
            ✓
          </div>
        )}
      </div>

      <div className="space-y-1.5 sm:space-y-2 mb-3 sm:mb-4">
        <div className="text-xs sm:text-sm text-gray-400 flex items-center justify-between">
          <span><span className="text-yellow-400">⛏️</span> Minerals</span>
          <span className="font-semibold text-yellow-300">+{planet.productionBonus.minerals}/s</span>
        </div>
        <div className="text-xs sm:text-sm text-gray-400 flex items-center justify-between">
          <span><span className="text-blue-400">⚡</span> Energy</span>
          <span className="font-semibold text-blue-300">+{planet.productionBonus.energy}/s</span>
        </div>
        <div className="text-xs sm:text-sm text-gray-400 flex items-center justify-between">
          <span><span className="text-green-400">🌾</span> Food</span>
          <span className="font-semibold text-green-300">+{planet.productionBonus.food}/s</span>
        </div>
        {planet.colonized && (
          <div className="text-xs sm:text-sm text-cyan-400 flex items-center justify-between">
            <span>👥 Population</span>
            <span className="font-semibold text-cyan-300">{planet.population}</span>
          </div>
        )}
      </div>

      {!planet.colonized && (
        <button
          onClick={() => onColonize(planet.id)}
          disabled={!canAfford}
          className={`w-full py-2.5 sm:py-3 px-3 sm:px-4 rounded-lg font-semibold transition-all text-sm sm:text-base ${
            canAfford
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/50 hover:shadow-cyan-500/70 active:scale-95'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          <span className="hidden sm:inline">Colonize (500💰 300⛏️ 50👥)</span>
          <span className="sm:hidden">Colonize</span>
        </button>
      )}
    </div>
  );
}
