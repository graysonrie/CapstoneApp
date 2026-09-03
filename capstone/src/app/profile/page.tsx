"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  FAKE_PROFILE,
  PlantRarity,
} from "@/features/profile/types/profileTypes";
import { chronoUtcDateTimeToUserFriendlyFormat } from "@/lib/utils";
import { HomeIcon } from "lucide-react";

const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> =
  {
    Common: "outline",
    Uncommon: "secondary",
    Rare: "default",
  };

export default function ProfilePage() {
  const { firstName, lastName, joinedAtDate, rank, stats, foundPlants } =
    FAKE_PROFILE;
  const xpPercent = Math.round((rank.xp / rank.xpToNext) * 100);

  const initials = `${firstName[0]}${lastName[0]}`.toUpperCase();
  const displayName = `${firstName} ${lastName}`;
  const joinedLabel = `Joined ${chronoUtcDateTimeToUserFriendlyFormat(joinedAtDate)}`;

  return (
    <>
      <PointGridBg />
      <div className="sticky top-4 left-4 z-20 self-start">
        <AnimatedButton
          href="/home"
          size="icon"
          variant="glass"
          className="size-16 rounded-full"
          aria-label="Home"
        >
          <HomeIcon className="size-8" />
        </AnimatedButton>
      </div>

      <main className="relative mx-auto flex w-full max-w-md flex-1 flex-col gap-6 px-6 py-8 z-10">
        <header className="flex flex-col items-center gap-3 text-center">
          <Avatar className="size-24">
            <AvatarFallback className="bg-primary/20 font-heading text-2xl text-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div>
            <h1 className="font-heading text-2xl font-medium">{displayName}</h1>
            <p className="text-sm text-muted-foreground">{joinedLabel}</p>
          </div>
        </header>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardDescription>Current rank</CardDescription>
                <CardTitle className="text-xl">{rank.name}</CardTitle>
              </div>
              <Badge>Lv. {rank.level}</Badge>
            </div>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Progress value={xpPercent} aria-label="XP toward next rank" />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>
                {rank.xp.toLocaleString()} / {rank.xpToNext.toLocaleString()} XP
              </span>
              <span>Next: {rank.nextRank}</span>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-3">
          <StatTile label="Scans" value={stats.scans} />
          <StatTile label="Species" value={stats.uniqueSpecies} />
          <StatTile label="Streak" value={`${stats.streakDays}d`} />
        </div>

        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-lg font-medium">Found plants</h2>
          <div className="grid grid-cols-2 gap-3">
            {foundPlants.map((plant) => (
              <Card key={plant.id} size="sm" className="gap-3">
                <div
                  className={`mx-4 h-20 rounded-2xl ${plant.tileClass}`}
                  aria-hidden
                />
                <CardHeader className="gap-1">
                  <CardTitle className="leading-tight">
                    {plant.commonName}
                  </CardTitle>
                  <CardDescription className="italic">
                    {plant.scientificName}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex items-center justify-between gap-2">
                  <Badge variant={RARITY_VARIANT[plant.rarity]}>
                    {plant.rarity}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {plant.foundAt}
                  </span>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}

function StatTile({ label, value }: { label: string; value: number | string }) {
  return (
    <Card size="sm" className="items-center py-4 text-center">
      <p className="font-heading text-xl font-medium">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </Card>
  );
}
