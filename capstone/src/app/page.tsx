"use client";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { getSession, ping } from "@/generated";
import { useAppStore } from "@/stores/useAppStore";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SplashScreenPage() {
  const { setValues } = useAppStore();
  const router = useRouter();

  useEffect(() => {
    ping()
      .then(() => {
        getSession()
          .then((session) => {
            if (!session) {
              router.replace("/login");
              return;
            }
            if (!session.profileComplete) {
              router.replace("/setup");
              return;
            }
            router.replace("/home");
          })
          .catch((err) => {
            console.warn(`failed to get session: ${err}`);
            router.replace("/login");
          });
      })
      .catch((err) => {
        console.warn(`failed to ping server: ${err}`);
        setValues({ isConfirmedOffline: true });
        router.replace("/home");
      });
  }, [router, setValues]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col flex-1 items-center justify-center max-w-[calc(80vw-1rem)] w-full mx-auto">
      <Label className="text-xl">Plant App</Label>
      <Button>
        <Link href="/home">Home</Link>
      </Button>
    </div>
  );
}
