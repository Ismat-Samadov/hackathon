import { Planet, Technology, GameEvent } from './types';

export const initialTechnologies: Technology[] = [
  {
    id: 'advanced-mining',
    name: 'Advanced Mining',
    description: 'Increases mineral production by 50%',
    cost: { credits: 500, minerals: 200 },
    researched: false,
    researchProgress: 0,
    category: 'production',
    effects: ['+50% Mineral Production'],
  },
  {
    id: 'solar-arrays',
    name: 'Solar Arrays',
    description: 'Increases energy production by 50%',
    cost: { credits: 400, minerals: 150 },
    researched: false,
    researchProgress: 0,
    category: 'production',
    effects: ['+50% Energy Production'],
  },
  {
    id: 'hydroponics',
    name: 'Hydroponics',
    description: 'Increases food production by 50%',
    cost: { credits: 350, minerals: 100 },
    researched: false,
    researchProgress: 0,
    category: 'production',
    effects: ['+50% Food Production'],
  },
  {
    id: 'warp-drive',
    name: 'Warp Drive',
    description: 'Reduces exploration costs by 30%',
    cost: { credits: 800, minerals: 400 },
    researched: false,
    researchProgress: 0,
    category: 'exploration',
    effects: ['-30% Exploration Costs'],
  },
  {
    id: 'terraforming',
    name: 'Terraforming',
    description: 'Reduces colonization costs by 40%',
    cost: { credits: 1000, minerals: 500 },
    researched: false,
    researchProgress: 0,
    category: 'exploration',
    effects: ['-40% Colonization Costs'],
  },
  {
    id: 'population-growth',
    name: 'Population Growth Initiative',
    description: 'Increases population growth rate by 25%',
    cost: { credits: 600, minerals: 200 },
    researched: false,
    researchProgress: 0,
    category: 'social',
    effects: ['+25% Population Growth'],
  },
  {
    id: 'quantum-computing',
    name: 'Quantum Computing',
    description: 'Reduces all research costs by 20%',
    cost: { credits: 1200, minerals: 600 },
    researched: false,
    researchProgress: 0,
    category: 'production',
    effects: ['-20% Research Costs'],
  },
  {
    id: 'defense-systems',
    name: 'Planetary Defense',
    description: 'Protects against 50% of disaster damage',
    cost: { credits: 700, minerals: 350 },
    researched: false,
    researchProgress: 0,
    category: 'military',
    effects: ['-50% Disaster Damage'],
  },
];

const planetNames = [
  'Proxima', 'Kepler', 'Andoria', 'Vulcan', 'Risa', 'Bajor', 'Cardassia',
  'Romulus', 'Qo\'noS', 'Ferenginar', 'Trill', 'Betazed', 'Deneb', 'Rigel',
  'Altair', 'Vega', 'Arcturus', 'Sirius', 'Polaris', 'Antares', 'Betelgeuse',
  'Aldebaran', 'Procyon', 'Canopus', 'Achernar', 'Mimosa', 'Acrux', 'Spica',
];

let planetCounter = 0;

export function generatePlanet(): Planet {
  const types: Planet['type'][] = ['desert', 'ocean', 'forest', 'ice', 'volcanic', 'gas'];
  const sizes: Planet['size'][] = ['small', 'medium', 'large'];

  const type = types[Math.floor(Math.random() * types.length)];
  const size = sizes[Math.floor(Math.random() * sizes.length)];

  const sizeMultiplier = size === 'large' ? 1.5 : size === 'medium' ? 1 : 0.7;

  const typeBonus = {
    desert: { minerals: 15, energy: 5, food: 3 },
    ocean: { minerals: 5, energy: 8, food: 15 },
    forest: { minerals: 8, energy: 6, food: 12 },
    ice: { minerals: 12, energy: 10, food: 2 },
    volcanic: { minerals: 20, energy: 12, food: 1 },
    gas: { minerals: 3, energy: 18, food: 0 },
  };

  return {
    id: `planet-${Date.now()}-${Math.random()}`,
    name: planetNames[planetCounter++ % planetNames.length],
    type,
    size,
    colonized: false,
    population: 0,
    productionBonus: {
      minerals: Math.round(typeBonus[type].minerals * sizeMultiplier),
      energy: Math.round(typeBonus[type].energy * sizeMultiplier),
      food: Math.round(typeBonus[type].food * sizeMultiplier),
    },
    discoveredAt: Date.now(),
  };
}

const eventTemplates = [
  {
    type: 'discovery' as const,
    title: 'Ancient Artifact Discovered!',
    description: 'Your explorers have found an ancient alien artifact. What should we do with it?',
    choices: [
      {
        text: 'Study it for technology',
        effects: { credits: -100, minerals: 0, energy: 200, food: 0, population: 0 },
      },
      {
        text: 'Sell it for credits',
        effects: { credits: 500, minerals: 0, energy: 0, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'opportunity' as const,
    title: 'Trade Opportunity',
    description: 'A passing merchant fleet offers to trade resources.',
    choices: [
      {
        text: 'Trade minerals for credits',
        effects: { credits: 300, minerals: -150, energy: 0, food: 0, population: 0 },
      },
      {
        text: 'Trade credits for minerals',
        effects: { credits: -200, minerals: 300, energy: 0, food: 0, population: 0 },
      },
      {
        text: 'Decline',
        effects: { credits: 0, minerals: 0, energy: 0, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'disaster' as const,
    title: 'Solar Flare!',
    description: 'A massive solar flare has damaged our energy infrastructure.',
    choices: [
      {
        text: 'Emergency repairs',
        effects: { credits: -200, minerals: -100, energy: -50, food: 0, population: 0 },
      },
      {
        text: 'Accept the damage',
        effects: { credits: 0, minerals: 0, energy: -150, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'discovery' as const,
    title: 'Rich Asteroid Field',
    description: 'Scanners have detected a mineral-rich asteroid field nearby.',
    choices: [
      {
        text: 'Send mining expedition',
        effects: { credits: -150, minerals: 400, energy: -50, food: 0, population: 0 },
      },
      {
        text: 'Mark for later',
        effects: { credits: 0, minerals: 0, energy: 0, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'opportunity' as const,
    title: 'Immigration Wave',
    description: 'A group of colonists from a distant system wishes to join your empire.',
    choices: [
      {
        text: 'Welcome them',
        effects: { credits: -100, minerals: 0, energy: 0, food: -50, population: 50 },
      },
      {
        text: 'Turn them away',
        effects: { credits: 0, minerals: 0, energy: 0, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'threat' as const,
    title: 'Space Pirates!',
    description: 'Pirates are demanding tribute or they\'ll attack our trade routes.',
    choices: [
      {
        text: 'Pay them off',
        effects: { credits: -300, minerals: 0, energy: 0, food: 0, population: 0 },
      },
      {
        text: 'Refuse and fortify',
        effects: { credits: -100, minerals: -150, energy: 0, food: 0, population: 0 },
      },
    ],
  },
  {
    type: 'discovery' as const,
    title: 'Scientific Breakthrough',
    description: 'Your scientists have made an unexpected breakthrough!',
    choices: [
      {
        text: 'Publish findings',
        effects: { credits: 200, minerals: 0, energy: 100, food: 0, population: 0 },
      },
      {
        text: 'Keep it secret',
        effects: { credits: 0, minerals: 100, energy: 200, food: 0, population: 0 },
      },
    ],
  },
];

export function generateRandomEvent(): GameEvent {
  const template = eventTemplates[Math.floor(Math.random() * eventTemplates.length)];
  return {
    ...template,
    id: `event-${Date.now()}`,
    timestamp: Date.now(),
  };
}
