export interface Resources {
  credits: number;
  minerals: number;
  energy: number;
  food: number;
  population: number;
}

export interface Planet {
  id: string;
  name: string;
  type: 'desert' | 'ocean' | 'forest' | 'ice' | 'volcanic' | 'gas';
  size: 'small' | 'medium' | 'large';
  colonized: boolean;
  population: number;
  productionBonus: {
    minerals: number;
    energy: number;
    food: number;
  };
  discoveredAt: number;
}

export interface Technology {
  id: string;
  name: string;
  description: string;
  cost: {
    credits: number;
    minerals: number;
  };
  researched: boolean;
  researchProgress: number;
  category: 'production' | 'military' | 'exploration' | 'social';
  effects: string[];
  prerequisites?: string[];
}

export interface Ship {
  id: string;
  name: string;
  type: 'colony' | 'scout' | 'military';
  status: 'idle' | 'exploring' | 'colonizing';
}

export interface GameEvent {
  id: string;
  type: 'discovery' | 'disaster' | 'opportunity' | 'threat';
  title: string;
  description: string;
  choices: {
    text: string;
    effects: Partial<Resources>;
  }[];
  timestamp: number;
}

export interface GameStats {
  planetsColonized: number;
  technologiesResearched: number;
  totalProduction: number;
  gameStarted: number;
  achievements: string[];
}
