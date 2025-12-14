'use client';

import { GameStats } from '@/lib/types';

interface StatsDisplayProps {
  stats: GameStats;
}

export default function StatsDisplay({ stats }: StatsDisplayProps) {
  const playTime = Math.floor((Date.now() - stats.gameStarted) / 1000 / 60); // minutes

  return (
    <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-sm rounded-lg p-6 shadow-2xl border border-purple-500/30">
      <h2 className="text-2xl font-bold mb-4 text-cyan-300">Statistics</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
          <div className="text-sm text-gray-400">Planets Colonized</div>
          <div className="text-2xl font-bold text-purple-300">{stats.planetsColonized}</div>
        </div>
        <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
          <div className="text-sm text-gray-400">Tech Researched</div>
          <div className="text-2xl font-bold text-purple-300">{stats.technologiesResearched}</div>
        </div>
        <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
          <div className="text-sm text-gray-400">Total Production</div>
          <div className="text-2xl font-bold text-purple-300">
            {Math.floor(stats.totalProduction).toLocaleString()}
          </div>
        </div>
        <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
          <div className="text-sm text-gray-400">Play Time</div>
          <div className="text-2xl font-bold text-purple-300">{playTime}m</div>
        </div>
      </div>
    </div>
  );
}
