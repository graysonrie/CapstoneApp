import type { PlantRarity } from "@/features/profile/types/profileTypes";

export type DailyPlantQuest = {
  id: string;
  commonName: string;
  scientificName: string;
  rarity: PlantRarity;
  xpReward: number;
  found: boolean;
  /** Tailwind background class for the photo placeholder tile */
  tileClass: string;
};

export type HomeMock = {
  firstName: string;
  quests: DailyPlantQuest[];
};

export const FAKE_HOME: HomeMock = {
  firstName: "Grayson",
  quests: [
    {
      id: "rose",
      commonName: "Rose",
      scientificName: "Roseus Rose",
      rarity: "Common",
      xpReward: 50,
      found: true,
      tileClass: "bg-red-500",
    },
    {
      id: "redbud",
      commonName: "Eastern Redbud",
      scientificName: "Redbudius Redbud",
      rarity: "Uncommon",
      xpReward: 100,
      found: false,
      tileClass: "bg-secondary",
    },
    {
      id: "white-oak",
      commonName: "White Oak",
      scientificName: "Whitus Oakus",
      rarity: "Common",
      xpReward: 75,
      found: false,
      tileClass: "bg-chart-3/40",
    },
  ],
};
