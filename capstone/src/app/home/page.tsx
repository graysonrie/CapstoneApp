"use client";

import { useHomeStore } from "@/features/home/store/useHomeStore";
import { useAppStore } from "@/stores/useAppStore";
import { useEffect } from "react";

export default function HomePage() {
  const { isFirstVisit, setValues } = useHomeStore();
  const { isConfirmedOffline } = useAppStore();

  useEffect(() => {
    if (isConfirmedOffline && isFirstVisit) {
      console.warn("You are offline");
      // Show offline warning
    }
    setValues({ isFirstVisit: false });
  }, [setValues, isFirstVisit, isConfirmedOffline]);

  return <div>I am HomePage</div>;
}
