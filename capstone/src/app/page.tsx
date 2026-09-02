"use client";
import { Label } from "@/components/ui/label";
import { isValidSession, ping } from "@/generated";
import { useAppStore } from "@/stores/useAppStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SplashScreenPage() {
  const { setValues } = useAppStore();
  const router = useRouter();

  // TODO: remove when done testing
  const autoSkipToHomePage = true;

  useEffect(() => {
    if (autoSkipToHomePage) {
      router.replace("/home");
      setValues({ isConfirmedOffline: true });
      return;
    }

    ping()
      .then(() => {
        isValidSession().then((isValid) => {
          if (isValid) {
            router.replace("/home");
          } else {
            router.replace("/login");
          }
        });
      })
      .catch((err) => {
        console.warn(`failed to ping server: ${err}`);
        setValues({ isConfirmedOffline: true });
        router.replace("/home");
      });
  }, [router, setValues, autoSkipToHomePage]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col flex-1 items-center justify-center max-w-[calc(80vw-1rem)] w-full mx-auto">
      <Label className="text-xl">Plant App</Label>
    </div>
  );
}
