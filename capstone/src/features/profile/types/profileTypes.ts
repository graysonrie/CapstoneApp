export type PlantRarity = "Common" | "Uncommon" | "Rare";

export interface FoundPlant {
  id: string;
  commonName: string;
  scientificName: string;
  rarity: PlantRarity;
  foundAt: string;
  /** tailwind background class for the photo placeholder tile */
  tileClass: string;
}

export interface ProfileAccountInfo {
  firstName: string;
  lastName: string;
  /** Chrono date */
  joinedAtDate: string;
  rank: {
    level: number;
    name: string;
    nextRank: string;
    xp: number;
    xpToNext: number;
  };
  stats: {
    scans: number;
    uniqueSpecies: number;
    streakDays: number;
  };
  foundPlants: FoundPlant[];
}

export const FAKE_PROFILE: ProfileAccountInfo = {
  firstName: "Grayson",
  lastName: "Rieger",
  /** Chrono date */
  joinedAtDate: "2025-03-14T18:30:00Z",
  rank: {
    level: 12,
    name: "Weed Eater",
    nextRank: "Plant Expert",
    xp: 2450,
    xpToNext: 3000,
  },
  stats: {
    scans: 47,
    uniqueSpecies: 18,
    streakDays: 5,
  },
  foundPlants: [
    {
      id: "rose",
      commonName: "Rose",
      scientificName: "Roseus Rose",
      rarity: "Common",
      foundAt: "May 28",
      tileClass: "bg-red-500",
    },
    {
      id: "redbud",
      commonName: "Eastern Redbud",
      scientificName: "Redbudius Redbud",
      rarity: "Uncommon",
      foundAt: "July 24",
      tileClass: "bg-secondary",
    },
    {
      id: "white-oak",
      commonName: "White Oak",
      scientificName: "Whitus Oakus",
      rarity: "Common",
      foundAt: "July 21",
      tileClass: "bg-chart-3/40",
    },
  ],
};
