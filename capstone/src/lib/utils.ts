import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Ex: 2025-03-14T18:30:00Z should convert to 'March 2025' */
export function chronoUtcDateTimeToUserFriendlyFormat(dateTime: string) {
  const formatted = new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
  }).format(new Date(dateTime));
  return formatted;
}
