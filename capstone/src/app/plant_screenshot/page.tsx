"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PointGridBg from "@/components/PointGridBg";
import { Progress } from "@/components/ui/progress";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";
import { scanPlant } from "@/generated";
import { TRANSITION1 } from "@/types/motionConstants";
import { motion } from "motion/react";
import { useQueryClient } from "@tanstack/react-query";

export default function PlantScreenshotPage() {
  const router = useRouter();
  const { pendingImagePath, previousPath, setResult, clearPending, markScanStarted } =
    useScanStore();
  const [progress, setProgress] = useState(8);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!pendingImagePath) {
      router.replace(previousPath || "/home");
      return;
    }
    if (!markScanStarted()) {
      return;
    }

    let cancelled = false;
    const timer = window.setInterval(() => {
      setProgress((value) => (value >= 90 ? value : value + 4));
    }, 400);

    scanPlant({ imagePath: pendingImagePath })
      .then((payload) => {
        if (cancelled) return;
        setProgress(100);
        setResult(payload.result, payload.image_data_url);
        queryClient.invalidateQueries({ queryKey: ["home"] });
        queryClient.invalidateQueries({ queryKey: ["profile"] });
        router.replace("/plant_analysis");
      })
      .catch((err) => {
        console.warn("plant scan failed", err);
        if (cancelled) return;
        clearPending();
        router.replace(previousPath || "/home");
      })
      .finally(() => {
        window.clearInterval(timer);
      });

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [
    pendingImagePath,
    previousPath,
    router,
    setResult,
    clearPending,
    markScanStarted,
    queryClient,
  ]);

  return (
    <main className="relative mx-auto flex w-full max-w-md flex-1 flex-col items-center justify-center gap-6 px-8">
      <PointGridBg />
      <motion.div
        className="relative z-10 flex w-full flex-col items-center gap-4 text-center"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={TRANSITION1}
      >
        <h1 className="font-heading text-2xl font-medium">Analyzing plant…</h1>
        <p className="text-sm text-muted-foreground">
          This can take a few seconds.
        </p>
        <Progress value={progress} aria-label="Plant analysis progress" />
      </motion.div>
    </main>
  );
}
