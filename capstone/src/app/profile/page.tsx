/* eslint-disable @next/next/no-img-element */
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
import { chronoUtcDateTimeToUserFriendlyFormat } from "@/lib/utils";
import { TRANSITION1 } from "@/types/motionConstants";
import { HomeIcon, MapIcon } from "lucide-react";
import { motion } from "motion/react";
import { useQuery } from "@tanstack/react-query";
import { getProfile } from "@/generated";
import FoundPlantComponent from "@/features/profile/components/FoundPlantComponent";
import { PlantRarity } from "@/features/profile/types/profileTypes";

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

  const initials =
    `${firstName[0] ?? ""}${lastName[0] ?? ""}`.toUpperCase() || "?";
  const displayName =
    [firstName, lastName].filter(Boolean).join(" ") || "Plant explorer";
  const joinedLabel = profile?.joined_at
    ? `Joined ${chronoUtcDateTimeToUserFriendlyFormat(profile.joined_at)}`
    : "";

  return (
    <>
      <PointGridBg />
      <div className="sticky top-4 z-20 flex w-full items-start justify-between px-4">
        <AnimatedButton
          href="/home"
          size="icon"
          variant="defaultGlass"
          className="size-16 rounded-full"
          aria-label="Home"
        >
          <HomeIcon className="size-8" />
        </AnimatedButton>
        <AnimatedButton
          href="/map"
          size="icon" 
          variant="defaultGlass"
          className="size-16 rounded-full"
        >
          <MapIcon className="size-8"/>
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
                  {rank?.name ?? "Unknown"}
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
          <StatTile label="Scans" value={stats?.scans ?? 0} onClick={() => window.location.href = "/collection"}/>
          <StatTile label="Species" value={stats?.unique_species ?? 0} />
          <StatTile label="Streak" value={`${stats?.streak_days ?? 0}d`} />
        </div>

        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-lg font-medium">Recent finds</h2>
          {foundPlants.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Scan a plant to start your collection.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {foundPlants.slice(0, 4).map((plant) => (
                <FoundPlantComponent
                  key={plant.id}
                  id={plant.id}
                  imageBase64={plant.image_base64}
                  commonName={plant.common_name}
                  scientificName={plant.scientific_name}
                  rarity={plant.rarity as PlantRarity}
                  foundOn={plant.found_on}
                />
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

function StatTile({ label, value, onClick }: { label: string; value: number | string, onClick?: () => void}) {
  return (
    <Card size="sm" className="items-center py-4 text-center" onClick={onClick}>
      <p className="font-heading text-xl font-medium">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </Card>
  );
}
