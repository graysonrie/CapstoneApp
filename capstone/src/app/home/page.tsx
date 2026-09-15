"use client";

import { useEffect } from "react";
import { Check, User, WifiOff } from "lucide-react";
import { motion } from "motion/react";
import { useQuery } from "@tanstack/react-query";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useHomeStore } from "@/features/home/store/useHomeStore";
import type { DailyPlantQuest, PlantRarity } from "@/features/plant_scan/types";
import { useAppStore } from "@/stores/useAppStore";
import { TRANSITION1 } from "@/types/motionConstants";
import { getHome } from "@/generated";

const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> =
  {
    Common: "outline",
    Uncommon: "secondary",
    Rare: "default",
    SuperRare: "default",
    Exotic: "default",
  };

export default function HomePage() {
  const { isFirstVisit, showOfflineNotice, setValues } = useHomeStore();
  const { isConfirmedOffline } = useAppStore();
  const homeQuery = useQuery({
    queryKey: ["home"],
    queryFn: getHome,
  });

  const firstName = homeQuery.data?.first_name ?? "";
  const quests = homeQuery.data?.quests ?? [];
  const foundCount = quests.filter((q) => q.found).length;
  const totalCount = quests.length || 3;
  const progressPercent = Math.round((foundCount / totalCount) * 100);

  useEffect(() => {
    if (!isFirstVisit) return;

    setValues({
      isFirstVisit: false,
      ...(isConfirmedOffline ? { showOfflineNotice: true } : {}),
    });
  }, [setValues, isFirstVisit, isConfirmedOffline]);

  return (
    <>
      <PointGridBg />
      <div className="sticky top-4 right-4 z-20 mr-4 self-end">
        <AnimatedButton
          href="/profile"
          size="icon"
          variant="defaultGlass"
          className="size-16 rounded-full"
          aria-label="Profile"
        >
          <User className="size-8" />
        </AnimatedButton>
      </div>

      <motion.div
        className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col gap-6 px-6 py-8"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={TRANSITION1}
      >
        <header className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-heading text-2xl font-medium">
            Good morning{firstName ? ` ${firstName}` : ""}
          </h1>
          <p className="text-sm text-muted-foreground">
            Find today&apos;s plants and earn XP.
          </p>
        </header>

        {showOfflineNotice && (
          <Alert>
            <WifiOff />
            <AlertTitle>You&apos;re offline</AlertTitle>
            <AlertDescription>
              Scanning may be limited until you reconnect.
            </AlertDescription>
          </Alert>
        )}

        {homeQuery.isError ? (
          <Alert>
            <AlertTitle>Couldn&apos;t load today&apos;s plants</AlertTitle>
            <AlertDescription>
              Check that you&apos;re signed in and the server is running.
            </AlertDescription>
          </Alert>
        ) : null}

        <section className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-heading font-medium">Today</span>
            <span className="text-muted-foreground">
              {foundCount} of {totalCount} found
            </span>
          </div>
          <Progress value={progressPercent} aria-label="Daily quest progress" />
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-lg font-medium">
            Today&apos;s plants
          </h2>
          <ul className="flex flex-col gap-3">
            {quests.map((quest, index) => (
              <motion.li
                key={quest.key}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ ...TRANSITION1, delay: 0.08 * index }}
              >
                <QuestCard quest={quest} />
              </motion.li>
            ))}
          </ul>
        </section>
      </motion.div>
    </>
  );
}

function QuestCard({ quest }: { quest: DailyPlantQuest }) {
  return (
    <Card size="sm" className="flex-row items-center gap-0 py-4">
      {quest.image_base64 ? (
        <img
          src={quest.image_base64}
          alt=""
          className="ml-4 size-16 shrink-0 rounded-2xl object-cover"
        />
      ) : (
        <div
          className="ml-4 size-16 shrink-0 rounded-2xl bg-muted"
          aria-hidden
        />
      )}
      <div className="flex min-w-0 flex-1 flex-col">
        <CardHeader className="gap-1">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="leading-tight">{quest.common_name}</CardTitle>
            <Badge variant={RARITY_VARIANT[quest.rarity]}>{quest.rarity}</Badge>
          </div>
          <CardDescription className="italic">
            {quest.scientific_name}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between gap-2 pb-4">
          <span className="text-xs text-muted-foreground">
            +{quest.xp_reward} XP
          </span>
          {quest.found ? (
            <span className="flex items-center gap-1 text-xs font-medium text-primary">
              <Check className="size-3.5" aria-hidden />
              Found
            </span>
          ) : (
            <span className="text-xs text-muted-foreground">Not found yet</span>
          )}
        </CardContent>
      </div>
    </Card>
  );
}
