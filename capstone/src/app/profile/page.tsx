"use client";

import { useState } from "react";
import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
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
import { useLogoutMutation } from "@/features/auth/hooks/useAuthMutations";
import type { PlantRarity } from "@/features/plant_scan/types";
import { chronoUtcDateTimeToUserFriendlyFormat } from "@/lib/utils";
import { TRANSITION1 } from "@/types/motionConstants";
import { HomeIcon } from "lucide-react";
import { motion } from "motion/react";
import { useQuery } from "@tanstack/react-query";
import { getProfile } from "@/generated";

const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> =
  {
    Common: "outline",
    Uncommon: "secondary",
    Rare: "default",
    SuperRare: "default",
    Exotic: "default",
  };

export default function ProfilePage() {
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });
  const logoutMutation = useLogoutMutation();
  const [signOutOpen, setSignOutOpen] = useState(false);

  const profile = profileQuery.data;
  const firstName = profile?.first_name ?? "";
  const lastName = profile?.last_name ?? "";
  const rank = profile?.rank;
  const stats = profile?.stats;
  const foundPlants = profile?.found_plants ?? [];
  const xpPercent = rank
    ? Math.round((rank.xp / Math.max(rank.xp_to_next, 1)) * 100)
    : 0;

  const initials = `${firstName[0] ?? ""}${lastName[0] ?? ""}`.toUpperCase() || "?";
  const displayName = [firstName, lastName].filter(Boolean).join(" ") || "Plant explorer";
  const joinedLabel = profile?.joined_at
    ? `Joined ${chronoUtcDateTimeToUserFriendlyFormat(profile.joined_at)}`
    : "";

  return (
    <>
      <PointGridBg />
      <div className="sticky top-4 left-4 z-20 self-start">
        <AnimatedButton
          href="/home"
          size="icon"
          variant="defaultGlass"
          className="size-16 rounded-full"
          aria-label="Home"
        >
          <HomeIcon className="size-8" />
        </AnimatedButton>
      </div>

      <motion.div
        className="relative mx-auto flex w-full max-w-md flex-1 flex-col gap-6 px-6 py-8 z-10"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={TRANSITION1}
      >
        <header className="flex flex-col items-center gap-3 text-center">
          <Avatar className="size-24">
            <AvatarFallback className="bg-primary/20 font-heading text-2xl text-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div>
            <h1 className="font-heading text-2xl font-medium">{displayName}</h1>
            {joinedLabel ? (
              <p className="text-sm text-muted-foreground">{joinedLabel}</p>
            ) : null}
          </div>
        </header>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardDescription>Current rank</CardDescription>
                <CardTitle className="text-xl">
                  {rank?.name ?? "Weed Eater"}
                </CardTitle>
              </div>
              <Badge>Lv. {rank?.level ?? 1}</Badge>
            </div>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Progress value={xpPercent} aria-label="XP toward next rank" />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>
                {(rank?.xp ?? 0).toLocaleString()} /{" "}
                {(rank?.xp_to_next ?? 30).toLocaleString()} XP
              </span>
              <span>Next: {rank?.next_rank ?? "Gardener"}</span>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-3">
          <StatTile label="Scans" value={stats?.scans ?? 0} />
          <StatTile label="Species" value={stats?.unique_species ?? 0} />
          <StatTile label="Streak" value={`${stats?.streak_days ?? 0}d`} />
        </div>

        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-lg font-medium">Found plants</h2>
          {foundPlants.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Scan a plant to start your collection.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {foundPlants.map((plant) => (
                <Card key={plant.id} size="sm" className="gap-3">
                  {plant.image_base64 ? (
                    <img
                      src={plant.image_base64}
                      alt=""
                      className="mx-4 h-20 rounded-2xl object-cover"
                    />
                  ) : (
                    <div className="mx-4 h-20 rounded-2xl bg-muted" aria-hidden />
                  )}
                  <CardHeader className="gap-1">
                    <CardTitle className="leading-tight">
                      {plant.common_name}
                    </CardTitle>
                    <CardDescription className="italic">
                      {plant.scientific_name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex items-center justify-between gap-2">
                    {plant.rarity ? (
                      <Badge variant={RARITY_VARIANT[plant.rarity]}>
                        {plant.rarity}
                      </Badge>
                    ) : (
                      <span />
                    )}
                    <span className="text-xs text-muted-foreground">
                      {plant.found_on}
                    </span>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>

        <AnimatedButton
          type="button"
          size="lg"
          variant="destructive"
          className="mt-4 w-full"
          disabled={logoutMutation.isPending}
          onClick={() => setSignOutOpen(true)}
        >
          {logoutMutation.isPending ? "Signing out…" : "Sign out"}
        </AnimatedButton>

        <AlertDialog open={signOutOpen} onOpenChange={setSignOutOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                You will be signed out and returned to the login screen.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                variant="destructive"
                onClick={() => logoutMutation.mutate()}
              >
                Sign out
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </motion.div>
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
