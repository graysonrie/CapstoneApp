"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { takePendingPhoto } from "@/lib/camera";

export default function ResumePendingScan() {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;

    takePendingPhoto().then((path) => {
      if (cancelled || !path) {
        return;
      }
      if (pathname === "/plant_screenshot" || pathname === "/plant_analysis") {
        return;
      }
      router.push("/plant_screenshot");
    });

    return () => {
      cancelled = true;
    };
  }, [pathname, router]);

  return null;
}
