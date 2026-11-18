"use client";

import { useQuery } from "@tanstack/react-query";
import { getSession } from "@/generated";

export const sessionQueryKey = ["session"] as const;

export function useIsValidSession() {
  return useQuery({
    queryKey: sessionQueryKey,
    queryFn: getSession,
    select: (session) => session !== null,
  });
}
