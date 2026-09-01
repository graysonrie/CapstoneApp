"use client";
import { Label } from "@/components/ui/label";
import { isValidSession } from "@/generated";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SplashScreenPage() {
  const router = useRouter();

  useEffect(() => {
    isValidSession().then((isValid) => {
      if (isValid) {
        router.replace("/home");
      } else {
        router.replace("/login");
      }
    });
  }, [router]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col flex-1 items-center justify-center max-w-[calc(80vw-1rem)] w-full mx-auto">
      <Label className="text-xl">Plant App</Label>
    </div>
  );
}
