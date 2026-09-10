export const USAGE_INTENT_OPTIONS = [
  "Just for fun",
  "Learning",
  "Gardening",
  "Work or school",
] as const;

export type UsageIntent = (typeof USAGE_INTENT_OPTIONS)[number];
