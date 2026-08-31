"use client";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ensureFolderCreated } from "@/generated";

export default function SplashScreenPage() {
  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col flex-1 items-center justify-center max-w-[calc(80vw-1rem)] w-full mx-auto">
      <Label className="text-xl">Plant App</Label>
    </div>
  );
}
