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
  const pendingImagePath = useScanStore((state) => state.pendingImagePath);
  const previousPath = useScanStore((state) => state.previousPath);
  const result = useScanStore((state) => state.result);
  const setResult = useScanStore((state) => state.setResult);
  const clearPending = useScanStore((state) => state.clearPending);
  const markScanStarted = useScanStore((state) => state.markScanStarted);
  const [progress, setProgress] = useState(8);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (result) {
      router.replace("/plant_analysis");
    }
  }, [result, router]);

  useEffect(() => {
    if (result) {
      return;
    }
    if (!pendingImagePath) {
      router.replace(previousPath || "/home");
      return;
    }
    if (!markScanStarted()) {
      return;
    }

    const timer = window.setInterval(() => {
      setProgress((value) => (value >= 90 ? value : value + 4));
    }, 400);

    scanPlant({ imagePath: pendingImagePath })
      .then((payload) => {
        setProgress(100);
        setResult(payload.result, payload.image_data_url);
        queryClient.invalidateQueries({ queryKey: ["home"] });
        queryClient.invalidateQueries({ queryKey: ["profile"] });
      })
      .catch((err) => {
        console.warn("plant scan failed", err);
        clearPending();
        router.replace(previousPath || "/home");
      })
      .finally(() => {
        window.clearInterval(timer);
      });

    return () => {
      window.clearInterval(timer);
    };
  }, [
    pendingImagePath,
    previousPath,
    result,
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
