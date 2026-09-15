"use client";

import { usePathname, useRouter } from "next/navigation";
import { Camera } from "lucide-react";
import AnimatedButton from "../generic/AnimatedButton";
import { open } from "@tauri-apps/plugin-dialog";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";

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
    const selected = await open({
      multiple: false,
      directory: false,
      filters: [
        {
          name: "Images",
          extensions: ["png", "jpg", "jpeg", "webp", "heic", "gif"],
        },
      ],
    });

    if (!selected || Array.isArray(selected)) {
      return;
    }

    setPendingScan(pathname || "/home", selected);
    router.push("/plant_screenshot");
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
