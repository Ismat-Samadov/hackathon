# Space Colonization Game

A highly engaging space colonization strategy game built with Next.js and TypeScript. No login required - just start playing!

## Features

- **Resource Management**: Manage credits, minerals, energy, food, and population
- **Planet Colonization**: Discover and colonize different types of planets with unique production bonuses
- **Technology Research**: Unlock powerful technologies to boost your empire
- **Random Events**: Deal with discoveries, disasters, opportunities, and threats
- **Auto-Save**: Game progress automatically saves to your browser's local storage
- **Multiple Game Speeds**: Control the pace with 0.5x, 1x, 2x, or 5x speed
- **Beautiful UI**: Stunning space-themed interface with animations

## Getting Started

### Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## How to Play

### Starting Out
- You begin with Earth and basic resources
- Resources generate automatically over time based on your colonized planets
- Use the game speed controls to speed up or slow down time

### Expanding Your Empire

1. **Explore**: Click "Explore New Planet" to discover new worlds (costs 200💰 50⚡)
2. **Colonize**: Click "Colonize" on discovered planets (costs 500💰 300⛏️ 50👥)
3. **Research**: Unlock technologies for powerful bonuses
4. **Manage Events**: Random events will occur - choose wisely!

### Planet Types
- **Desert** 🏜️: High minerals, low food
- **Ocean** 🌊: High food, good energy
- **Forest** 🌲: Balanced production
- **Ice** ❄️: High minerals and energy, very low food
- **Volcanic** 🌋: Extreme minerals and energy, almost no food
- **Gas** 💨: Excellent energy, no food

### Technologies
Research technologies in four categories:
- **Production**: Increase resource output
- **Exploration**: Reduce exploration and colonization costs
- **Military**: Protect against disasters
- **Social**: Boost population growth

### Tips for Success
- Colonize planets early to increase production
- Balance your resource spending between exploration, colonization, and research
- Different planet types specialize in different resources
- Events can provide big bonuses or challenges - choose carefully
- The game auto-saves, so you can always come back later

## Tech Stack

- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management with persistence
- **React 19** - UI library

## Project Structure

```
space_colonization/
├── app/
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Main game page
│   └── globals.css     # Global styles
├── components/
│   ├── ResourceDisplay.tsx
│   ├── PlanetCard.tsx
│   ├── TechnologyCard.tsx
│   ├── EventModal.tsx
│   ├── GameControls.tsx
│   └── StatsDisplay.tsx
└── lib/
    ├── types.ts        # TypeScript interfaces
    ├── gameStore.ts    # Zustand store
    └── gameData.ts     # Game configuration
```

## License

MIT
