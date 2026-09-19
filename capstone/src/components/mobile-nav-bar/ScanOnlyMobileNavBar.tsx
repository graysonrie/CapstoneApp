"use client";

import { usePathname, useRouter } from "next/navigation";
import { Camera } from "lucide-react";
import { toast } from "sonner";
import AnimatedButton from "../generic/AnimatedButton";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";
import { takePhoto } from "../../lib/camera";

export default function ScanOnlyMobileNavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const setPendingScan = useScanStore((state) => state.setPendingScan);

  const hideScan =
    pathname === "/login" ||
    pathname === "/reset-password" ||
    pathname === "/setup" ||
    pathname === "/plant_screenshot";

  if (hideScan) {
    return null;
  }

  async function handleScan() {
    try {
      const img = await takePhoto();

      if (!img) {
        return;
      }

      setPendingScan(pathname || "/home", img);
      router.push("/plant_screenshot");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error ?? "Unknown error");
      console.error("takePhoto failed:", error);
      toast.error(`Camera failed: ${message}`);
    }
  }

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-50 mx-2 mb-[max(1rem,env(safe-area-inset-bottom))]"
    >
      <AnimatedButton
        type="button"
        onClick={handleScan}
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
