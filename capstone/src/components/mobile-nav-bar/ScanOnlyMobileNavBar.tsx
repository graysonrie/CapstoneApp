"use client";

import { usePathname } from "next/navigation";
import { Camera } from "lucide-react";
import AnimatedButton from "../generic/AnimatedButton";
// import { useIsValidSession } from "@/features/auth/hooks/useIsValidSession";
// import { useAppStore } from "@/stores/useAppStore";

export default function ScanOnlyMobileNavBar() {
  const pathname = usePathname();
  // const { data: isLoggedIn, isLoading } = useIsValidSession();
  // const { isConfirmedOffline } = useAppStore();

  const isLogin = pathname === "/login";

  if (isLogin) {
    return null;
  }

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-50 mx-2 mb-[max(1rem,env(safe-area-inset-bottom))]"
    >
      <AnimatedButton
        href="/plant_screenshot"
        className="h-24 w-full flex-col gap-0.5 rounded-full"
        variant="glass"
        aria-label="Scan"
      >
        <Camera className="size-10" strokeWidth={2} aria-hidden />
        <span className="text-sm font-medium">Scan</span>
      </AnimatedButton>
    </nav>
  );
}
