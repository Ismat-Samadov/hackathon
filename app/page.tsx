'use client';

import { useEffect, useState } from 'react';
import { useGameStore } from '@/lib/gameStore';
import ResourceDisplay from '@/components/ResourceDisplay';
import PlanetCard from '@/components/PlanetCard';
import TechnologyCard from '@/components/TechnologyCard';
import EventModal from '@/components/EventModal';
import GameControls from '@/components/GameControls';
import StatsDisplay from '@/components/StatsDisplay';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const {
    resources,
    planets,
    technologies,
    currentEvent,
    stats,
    gameSpeed,
    colonizePlanet,
    discoverPlanet,
    researchTechnology,
    handleEvent,
    dismissEvent,
    tick,
    setGameSpeed,
    resetGame,
    spendResources,
  } = useGameStore();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const interval = setInterval(() => {
      tick();
    }, 1000);

    return () => clearInterval(interval);
  }, [mounted, tick]);

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900">
        <div className="text-2xl text-cyan-300 animate-pulse">Loading Galaxy...</div>
      </div>
    );
  }

  const canAffordColonization = resources.credits >= 500 && resources.minerals >= 300 && resources.population >= 50;
  const canAffordExploration = resources.credits >= 200 && resources.energy >= 50;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900 p-3 sm:p-4 md:p-6 lg:p-8">
      {/* Enhanced Background stars effect */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Small stars */}
        {[...Array(50)].map((_, i) => (
          <div
            key={`star-${i}`}
            className="absolute w-0.5 h-0.5 bg-white rounded-full animate-twinkle"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
        {/* Medium stars */}
        {[...Array(20)].map((_, i) => (
          <div
            key={`star-med-${i}`}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
        {/* Glowing stars */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`star-glow-${i}`}
            className={`absolute w-2 h-2 rounded-full animate-pulse-slow ${
              i % 3 === 0 ? 'bg-cyan-400' : i % 3 === 1 ? 'bg-purple-400' : 'bg-pink-400'
            }`}
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              boxShadow: `0 0 ${10 + Math.random() * 10}px currentColor`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-6 sm:mb-8">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-3 sm:mb-4 animate-in fade-in slide-in-from-top duration-1000 drop-shadow-2xl">
            Space Colonization
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-gray-400 animate-in fade-in slide-in-from-bottom duration-1000 delay-200 px-4">
            Build Your Galactic Empire
          </p>
        </header>

        {/* Main Game Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div className="lg:col-span-2 space-y-4 sm:space-y-6">
            <ResourceDisplay resources={resources} />

            {/* Planets Section */}
            <div className="bg-gradient-to-r from-blue-900/30 to-cyan-900/30 backdrop-blur-md rounded-xl p-4 sm:p-6 shadow-2xl border border-blue-500/30 hover:border-blue-400/50 transition-all glow-cyan">
              <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-cyan-300 flex items-center gap-2">
                <span>🪐</span>
                <span>Planets</span>
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {planets.map((planet) => (
                  <PlanetCard
                    key={planet.id}
                    planet={planet}
                    onColonize={colonizePlanet}
                    canAfford={canAffordColonization}
                  />
                ))}
              </div>
            </div>

            {/* Technologies Section */}
            <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 backdrop-blur-md rounded-xl p-4 sm:p-6 shadow-2xl border border-purple-500/30 hover:border-purple-400/50 transition-all glow-purple">
              <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-cyan-300 flex items-center gap-2">
                <span>🔬</span>
                <span>Research</span>
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {technologies.map((tech) => {
                  const canAfford = resources.credits >= tech.cost.credits && resources.minerals >= tech.cost.minerals;
                  return (
                    <TechnologyCard
                      key={tech.id}
                      tech={tech}
                      onResearch={researchTechnology}
                      canAfford={canAfford && !tech.researched}
                    />
                  );
                })}
              </div>
            </div>
          </div>

          <div className="space-y-4 sm:space-y-6 order-first lg:order-last">
            <GameControls
              gameSpeed={gameSpeed}
              onSpeedChange={setGameSpeed}
              onExplore={discoverPlanet}
              onReset={resetGame}
              canExplore={canAffordExploration}
            />

            <StatsDisplay stats={stats} />
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center text-gray-500 text-xs sm:text-sm py-4">
          <p className="px-4">No login required • Auto-saves to browser • Made with Next.js & TypeScript</p>
        </footer>
      </div>

      {/* Event Modal */}
      {currentEvent && (
        <EventModal
          event={currentEvent}
          onChoice={handleEvent}
          onDismiss={dismissEvent}
        />
      )}
    </div>
  );
}
