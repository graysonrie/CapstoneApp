export type PlantRarity =
  | "Common"
  | "Uncommon"
  | "Rare"
  | "SuperRare"
  | "Exotic";

export type PlantConfidence = "High" | "Medium" | "Low";

export interface Identification {
  common_name: string | null;
  scientific_name: string | null;
  family: string | null;
  confidence: PlantConfidence;
  rarity: PlantRarity | null;
}

export interface Care {
  light: string | null;
  watering: string | null;
  soil: string | null;
  temperature: string | null;
}

export interface Toxicity {
  humans: string | null;
  pets: string | null;
}

export interface PlantSections {
  appearance: string;
  native_range: string | null;
  care: Care | null;
  interesting_facts: string[];
  toxicity: Toxicity | null;
}

export interface IdentificationNotes {
  reasoning_summary: string | null;
  uncertainty: string | null;
}

export interface PlantScan {
  is_plant: boolean;
  identification: Identification;
  summary: string;
  sections: PlantSections;
  identification_notes: IdentificationNotes;
}

export interface DailyMatch {
  key: string;
  common_name: string;
}

export interface PlantScanResult {
  scan: PlantScan;
  xp_awarded: number;
  is_new_species: boolean;
  daily_match: DailyMatch | null;
  leveled_up: boolean;
}

export interface DailyPlantQuest {
  key: string;
  common_name: string;
  scientific_name: string;
  rarity: PlantRarity;
  xp_reward: number;
  found: boolean;
  image_base64: string | null;
}

export interface HomeResponse {
  first_name: string | null;
  level: number;
  rank_title: string;
  xp: number;
  max_xp: number;
  quests: DailyPlantQuest[];
}

export interface CollectionPlant {
  id: number;
  common_name: string;
  scientific_name: string;
  rarity: PlantRarity | null;
  found_on: string;
  image_base64: string | null;
}

export interface ProfileRank {
  level: number;
  name: string;
  next_rank: string;
  xp: number;
  xp_to_next: number;
}

export interface ProfileStats {
  scans: number;
  unique_species: number;
  streak_days: number;
}

export interface ProfileResponse {
  first_name: string | null;
  last_name: string | null;
  joined_at: string;
  rank: ProfileRank;
  stats: ProfileStats;
  found_plants: CollectionPlant[];
}

export interface ScanPlantPayload {
  result: PlantScanResult;
  image_data_url: string;
}
