'use client';

interface GameControlsProps {
  gameSpeed: number;
  onSpeedChange: (speed: number) => void;
  onExplore: () => void;
  onReset: () => void;
  canExplore: boolean;
}

export default function GameControls({
  gameSpeed,
  onSpeedChange,
  onExplore,
  onReset,
  canExplore,
}: GameControlsProps) {
  return (
    <div className="bg-gradient-to-r from-slate-900/50 to-gray-900/50 backdrop-blur-sm rounded-lg p-6 shadow-2xl border border-slate-500/30">
      <h2 className="text-2xl font-bold mb-4 text-cyan-300">Controls</h2>

      <div className="space-y-4">
        <div>
          <label className="text-sm text-gray-400 mb-2 block">Game Speed</label>
          <div className="flex gap-2">
            {[0.5, 1, 2, 5].map((speed) => (
              <button
                key={speed}
                onClick={() => onSpeedChange(speed)}
                className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-all ${
                  gameSpeed === speed
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/50'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={onExplore}
          disabled={!canExplore}
          className={`w-full py-3 px-4 rounded-lg font-semibold transition-all ${
            canExplore
              ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white shadow-lg shadow-green-500/50'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          🔭 Explore New Planet (200💰 50⚡)
        </button>

        <button
          onClick={() => {
            if (confirm('Are you sure you want to reset the game? All progress will be lost.')) {
              onReset();
            }
          }}
          className="w-full py-2 px-4 rounded-lg bg-red-900/50 hover:bg-red-800/50 text-red-300 border border-red-500/30 hover:border-red-500/60 transition-all"
        >
          Reset Game
        </button>
      </div>

      <div className="mt-6 p-4 bg-black/30 rounded-lg border border-cyan-500/20">
        <h3 className="text-sm font-semibold text-cyan-400 mb-2">Tips:</h3>
        <ul className="text-xs text-gray-400 space-y-1">
          <li>• Colonize planets to increase production</li>
          <li>• Research technologies for powerful bonuses</li>
          <li>• Events occur randomly - choose wisely!</li>
          <li>• Game auto-saves to your browser</li>
        </ul>
      </div>
    </div>
  );
}
