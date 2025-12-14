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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900 p-4 md:p-8">
      {/* Background stars effect */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '10%', left: '20%' }} />
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '30%', left: '40%', animationDelay: '0.5s' }} />
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '50%', left: '60%', animationDelay: '1s' }} />
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '70%', left: '80%', animationDelay: '1.5s' }} />
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '20%', left: '70%', animationDelay: '0.3s' }} />
        <div className="absolute w-1 h-1 bg-white rounded-full animate-pulse" style={{ top: '80%', left: '30%', animationDelay: '0.8s' }} />
        <div className="absolute w-2 h-2 bg-cyan-400 rounded-full animate-pulse-slow" style={{ top: '15%', left: '85%' }} />
        <div className="absolute w-2 h-2 bg-purple-400 rounded-full animate-pulse-slow" style={{ top: '60%', left: '15%', animationDelay: '1s' }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-4 animate-in fade-in slide-in-from-top duration-1000">
            Space Colonization
          </h1>
          <p className="text-xl text-gray-400 animate-in fade-in slide-in-from-bottom duration-1000 delay-200">
            Build Your Galactic Empire
          </p>
        </header>

        {/* Main Game Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 space-y-6">
            <ResourceDisplay resources={resources} />

            {/* Planets Section */}
            <div className="bg-gradient-to-r from-blue-900/30 to-cyan-900/30 backdrop-blur-sm rounded-lg p-6 shadow-2xl border border-blue-500/30">
              <h2 className="text-3xl font-bold mb-4 text-cyan-300">🪐 Planets</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 backdrop-blur-sm rounded-lg p-6 shadow-2xl border border-purple-500/30">
              <h2 className="text-3xl font-bold mb-4 text-cyan-300">🔬 Research</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

          <div className="space-y-6">
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
        <footer className="text-center text-gray-500 text-sm">
          <p>No login required • Auto-saves to browser • Made with Next.js & TypeScript</p>
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
