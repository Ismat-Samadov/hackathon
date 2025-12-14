import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Resources, Planet, Technology, Ship, GameEvent, GameStats } from './types';
import { generatePlanet, generateRandomEvent, initialTechnologies } from './gameData';

interface GameState {
  resources: Resources;
  planets: Planet[];
  technologies: Technology[];
  ships: Ship[];
  currentEvent: GameEvent | null;
  stats: GameStats;
  gameSpeed: number;
  lastUpdate: number;

  // Actions
  addResources: (resources: Partial<Resources>) => void;
  spendResources: (resources: Partial<Resources>) => boolean;
  colonizePlanet: (planetId: string) => void;
  discoverPlanet: () => void;
  researchTechnology: (techId: string) => void;
  updateTechProgress: (techId: string, progress: number) => void;
  handleEvent: (choiceIndex: number) => void;
  dismissEvent: () => void;
  tick: () => void;
  setGameSpeed: (speed: number) => void;
  resetGame: () => void;
}

const initialResources: Resources = {
  credits: 1000,
  minerals: 500,
  energy: 100,
  food: 200,
  population: 100,
};

const initialStats: GameStats = {
  planetsColonized: 1,
  technologiesResearched: 0,
  totalProduction: 0,
  gameStarted: Date.now(),
  achievements: [],
};

const homePlanet: Planet = {
  id: 'home',
  name: 'Earth',
  type: 'forest',
  size: 'large',
  colonized: true,
  population: 100,
  productionBonus: {
    minerals: 10,
    energy: 10,
    food: 15,
  },
  discoveredAt: Date.now(),
};

export const useGameStore = create<GameState>()(
  persist(
    (set, get) => ({
      resources: initialResources,
      planets: [homePlanet],
      technologies: initialTechnologies,
      ships: [
        { id: 'ship-1', name: 'Explorer I', type: 'scout', status: 'idle' },
        { id: 'ship-2', name: 'Colony Ship Alpha', type: 'colony', status: 'idle' },
      ],
      currentEvent: null,
      stats: initialStats,
      gameSpeed: 1,
      lastUpdate: Date.now(),

      addResources: (resources) => {
        set((state) => ({
          resources: {
            credits: state.resources.credits + (resources.credits || 0),
            minerals: state.resources.minerals + (resources.minerals || 0),
            energy: state.resources.energy + (resources.energy || 0),
            food: state.resources.food + (resources.food || 0),
            population: state.resources.population + (resources.population || 0),
          },
        }));
      },

      spendResources: (resources) => {
        const state = get();
        const canAfford =
          (state.resources.credits >= (resources.credits || 0)) &&
          (state.resources.minerals >= (resources.minerals || 0)) &&
          (state.resources.energy >= (resources.energy || 0)) &&
          (state.resources.food >= (resources.food || 0));

        if (canAfford) {
          set((state) => ({
            resources: {
              credits: state.resources.credits - (resources.credits || 0),
              minerals: state.resources.minerals - (resources.minerals || 0),
              energy: state.resources.energy - (resources.energy || 0),
              food: state.resources.food - (resources.food || 0),
              population: state.resources.population - (resources.population || 0),
            },
          }));
          return true;
        }
        return false;
      },

      colonizePlanet: (planetId) => {
        const state = get();
        const cost = { credits: 500, minerals: 300, population: 50 };

        if (state.spendResources(cost)) {
          set((state) => ({
            planets: state.planets.map((planet) =>
              planet.id === planetId
                ? { ...planet, colonized: true, population: 50 }
                : planet
            ),
            stats: {
              ...state.stats,
              planetsColonized: state.stats.planetsColonized + 1,
            },
          }));
        }
      },

      discoverPlanet: () => {
        const state = get();
        const cost = { credits: 200, energy: 50 };

        if (state.spendResources(cost)) {
          const newPlanet = generatePlanet();
          set((state) => ({
            planets: [...state.planets, newPlanet],
          }));
        }
      },

      researchTechnology: (techId) => {
        const state = get();
        const tech = state.technologies.find((t) => t.id === techId);

        if (tech && !tech.researched && state.spendResources(tech.cost)) {
          set((state) => ({
            technologies: state.technologies.map((t) =>
              t.id === techId ? { ...t, researched: true, researchProgress: 100 } : t
            ),
            stats: {
              ...state.stats,
              technologiesResearched: state.stats.technologiesResearched + 1,
            },
          }));
        }
      },

      updateTechProgress: (techId, progress) => {
        set((state) => ({
          technologies: state.technologies.map((t) =>
            t.id === techId ? { ...t, researchProgress: Math.min(100, progress) } : t
          ),
        }));
      },

      handleEvent: (choiceIndex) => {
        const state = get();
        if (state.currentEvent) {
          const choice = state.currentEvent.choices[choiceIndex];
          state.addResources(choice.effects);
          set({ currentEvent: null });
        }
      },

      dismissEvent: () => {
        set({ currentEvent: null });
      },

      tick: () => {
        const state = get();
        const now = Date.now();
        const deltaTime = (now - state.lastUpdate) / 1000; // seconds

        // Calculate production from all colonized planets
        let production = { credits: 0, minerals: 0, energy: 0, food: 0 };

        state.planets.forEach((planet) => {
          if (planet.colonized) {
            production.credits += 5 * (planet.population / 100);
            production.minerals += planet.productionBonus.minerals * (planet.population / 100);
            production.energy += planet.productionBonus.energy * (planet.population / 100);
            production.food += planet.productionBonus.food * (planet.population / 100);
          }
        });

        // Apply technology bonuses
        state.technologies.forEach((tech) => {
          if (tech.researched) {
            if (tech.id === 'advanced-mining') {
              production.minerals *= 1.5;
            } else if (tech.id === 'solar-arrays') {
              production.energy *= 1.5;
            } else if (tech.id === 'hydroponics') {
              production.food *= 1.5;
            }
          }
        });

        // Random events (5% chance every tick)
        let newEvent = state.currentEvent;
        if (!state.currentEvent && Math.random() < 0.05) {
          newEvent = generateRandomEvent();
        }

        // Update resources
        const resourceUpdate = {
          credits: production.credits * deltaTime * state.gameSpeed,
          minerals: production.minerals * deltaTime * state.gameSpeed,
          energy: production.energy * deltaTime * state.gameSpeed,
          food: production.food * deltaTime * state.gameSpeed,
        };

        state.addResources(resourceUpdate);

        set({
          lastUpdate: now,
          currentEvent: newEvent,
          stats: {
            ...state.stats,
            totalProduction: state.stats.totalProduction +
              (production.credits + production.minerals + production.energy + production.food),
          },
        });
      },

      setGameSpeed: (speed) => {
        set({ gameSpeed: speed });
      },

      resetGame: () => {
        set({
          resources: initialResources,
          planets: [homePlanet],
          technologies: initialTechnologies,
          ships: [
            { id: 'ship-1', name: 'Explorer I', type: 'scout', status: 'idle' },
            { id: 'ship-2', name: 'Colony Ship Alpha', type: 'colony', status: 'idle' },
          ],
          currentEvent: null,
          stats: { ...initialStats, gameStarted: Date.now() },
          gameSpeed: 1,
          lastUpdate: Date.now(),
        });
      },
    }),
    {
      name: 'space-colonization-game',
    }
  )
);
