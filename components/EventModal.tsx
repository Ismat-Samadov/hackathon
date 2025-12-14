'use client';

import { GameEvent } from '@/lib/types';

interface EventModalProps {
  event: GameEvent;
  onChoice: (choiceIndex: number) => void;
  onDismiss: () => void;
}

export default function EventModal({ event, onChoice, onDismiss }: EventModalProps) {
  const eventEmojis = {
    discovery: '🔭',
    disaster: '💥',
    opportunity: '💡',
    threat: '⚔️',
  };

  const eventColors = {
    discovery: 'from-blue-600 to-cyan-600',
    disaster: 'from-red-600 to-orange-600',
    opportunity: 'from-green-600 to-emerald-600',
    threat: 'from-purple-600 to-pink-600',
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-3 sm:p-4 animate-in fade-in duration-300">
      <div className="bg-gradient-to-br from-gray-900 to-slate-900 rounded-2xl max-w-2xl w-full shadow-2xl border-2 border-cyan-500/50 animate-in zoom-in-95 duration-300 max-h-[90vh] overflow-y-auto">
        <div className={`bg-gradient-to-r ${eventColors[event.type]} p-4 sm:p-6 rounded-t-2xl`}>
          <div className="flex items-center gap-2 sm:gap-3 mb-2">
            <span className="text-3xl sm:text-4xl">{eventEmojis[event.type]}</span>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white">{event.title}</h2>
          </div>
          <div className="bg-black/20 px-3 py-1 rounded inline-block">
            <span className="text-xs sm:text-sm text-white/90 capitalize">{event.type}</span>
          </div>
        </div>

        <div className="p-4 sm:p-6">
          <p className="text-base sm:text-lg text-gray-300 mb-4 sm:mb-6">{event.description}</p>

          <div className="space-y-2 sm:space-y-3">
            {event.choices.map((choice, index) => (
              <button
                key={index}
                onClick={() => onChoice(index)}
                className="w-full p-3 sm:p-4 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 hover:from-indigo-800/60 hover:to-purple-800/60 rounded-lg border border-indigo-500/30 hover:border-indigo-400/60 transition-all group active:scale-95"
              >
                <div className="text-left">
                  <div className="text-white font-semibold mb-2 group-hover:text-cyan-300 transition-colors text-sm sm:text-base">
                    {choice.text}
                  </div>
                  <div className="flex flex-wrap gap-1.5 sm:gap-2 text-xs sm:text-sm">
                    {choice.effects.credits !== 0 && (
                      <span className={choice.effects.credits! > 0 ? 'text-green-400' : 'text-red-400'}>
                        {choice.effects.credits! > 0 ? '+' : ''}{choice.effects.credits}💰
                      </span>
                    )}
                    {choice.effects.minerals !== 0 && (
                      <span className={choice.effects.minerals! > 0 ? 'text-green-400' : 'text-red-400'}>
                        {choice.effects.minerals! > 0 ? '+' : ''}{choice.effects.minerals}⛏️
                      </span>
                    )}
                    {choice.effects.energy !== 0 && (
                      <span className={choice.effects.energy! > 0 ? 'text-green-400' : 'text-red-400'}>
                        {choice.effects.energy! > 0 ? '+' : ''}{choice.effects.energy}⚡
                      </span>
                    )}
                    {choice.effects.food !== 0 && (
                      <span className={choice.effects.food! > 0 ? 'text-green-400' : 'text-red-400'}>
                        {choice.effects.food! > 0 ? '+' : ''}{choice.effects.food}🌾
                      </span>
                    )}
                    {choice.effects.population !== 0 && (
                      <span className={choice.effects.population! > 0 ? 'text-green-400' : 'text-red-400'}>
                        {choice.effects.population! > 0 ? '+' : ''}{choice.effects.population}👥
                      </span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>

          <button
            onClick={onDismiss}
            className="mt-3 sm:mt-4 w-full py-2 text-gray-400 hover:text-white transition-colors text-xs sm:text-sm active:scale-95"
          >
            Dismiss (Later)
          </button>
        </div>
      </div>
    </div>
  );
}
