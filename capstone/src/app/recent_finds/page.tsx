"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import ImageViewer from "@/components/generic/ImageViewer";
import PointGridBg from "@/components/PointGridBg";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { PlantRarity } from "@/features/plant_scan/types";
import { getRecentFinds, getSession, type RecentFind } from "@/generated";
import { useQuery } from "@tanstack/react-query";
import { ArrowBigLeft, CalendarDays, Leaf, Sprout, UserRound } from "lucide-react";
import Image from "next/image"

const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> = {
  Common: "outline",
  Uncommon: "secondary",
  Rare: "default",
  SuperRare: "default",
  Exotic: "default",
};

function Find({ recentFind }: { recentFind: RecentFind }) {
  const { find, first_name, last_name } = recentFind;
  const discoverer = [first_name, last_name]
    .map((name) => name?.trim())
    .filter(Boolean)
    .join(" ") || "A Leaf Freak";

  return (
    <Card size="sm" className="gap-0 bg-card shadow-lg ring-1 ring-foreground/20 dark:ring-foreground/25">
      <div className="flex items-start gap-4 px-4">
        <div className="size-24 shrink-0 overflow-hidden rounded-2xl bg-muted sm:size-28">
          {find.image_base64 ? (
            <ImageViewer
              src={find.image_base64}
              alt={`Photo of ${find.common_name}`}
              className="block size-full cursor-zoom-in focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-foreground"
            >
              <Image
                src={find.image_base64}
                alt=""
                className="size-full object-cover"
                width={112}
                height={112}
              />
            </ImageViewer>
          ) : (
            <div className="flex size-full items-center justify-center" aria-label="No plant photo available">
              <Leaf aria-hidden className="size-9 text-card-foreground/50" />
            </div>
          )}
        </div>
        <CardHeader className="min-w-0 flex-1 gap-1 px-0">
          <CardTitle className="break-words leading-tight">{find.common_name}</CardTitle>
          <CardDescription className="break-words italic text-card-foreground">
            {find.scientific_name}
          </CardDescription>
          {find.rarity ? (
            <Badge variant={RARITY_VARIANT[find.rarity]} className="mt-1 w-fit">
              {find.rarity}
            </Badge>
          ) : null}
        </CardHeader>
      </div>
      <CardContent className="mt-3 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-t border-card-foreground/10 pt-3 text-xs text-card-foreground/80">
        <span className="flex min-w-0 items-center gap-1.5">
          <UserRound aria-hidden className="size-4 shrink-0" />
          Found by {discoverer}
        </span>
        <span className="flex items-center gap-1.5">
          <CalendarDays aria-hidden className="size-4 shrink-0" />
          {find.found_on}
        </span>
      </CardContent>
    </Card>
  );
}

export default function RecentFindsPage() {

    const session = useQuery({
        queryKey: ["session"],
        queryFn: getSession
    })
    const userID = session.data?.userId
    const recentFinds = useQuery({
        queryKey: ["recent_finds", userID],
        enabled: userID != null,
        queryFn: () => {
            if (userID == null) throw new Error("No signed-in user");
            return getRecentFinds({ count: 50, offset: 0, userExclude: userID });
        },
    })

    return (
        <>
            <PointGridBg/>
            <header className="sticky top-4 z-20 mx-auto flex w-full max-w-md items-center gap-3 px-4">
                <AnimatedButton
                    href="/home"
                    size="icon"
                    variant="defaultGlass"
                    className="size-16 shrink-0 rounded-full"
                    aria-label="Back to home"
                >
                    <ArrowBigLeft aria-hidden className="size-8" />
                </AnimatedButton>
                <div className="flex min-w-0 flex-col gap-1 px-1">
                    <h1 className="font-heading text-3xl font-semibold leading-tight">Community Finds</h1>
                    <p className="text-sm text-muted-foreground">Recent discoveries from other Leaf Freaks</p>
                </div>
            </header>
            <div className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col gap-4 px-4 pb-8 pt-6">
                {session.isLoading || (userID != null && recentFinds.isLoading) ? (
                    <div className="flex flex-1 flex-col items-center justify-center gap-4 py-8 text-center" role="status">
                        <span className="flex size-16 items-center justify-center rounded-full bg-muted text-card-foreground">
                            <Leaf aria-hidden className="size-9 animate-spin motion-reduce:animate-none" />
                        </span>
                        <p className="text-sm text-foreground">Loading community finds...</p>
                    </div>
                ) : session.isError || (userID != null && recentFinds.isError) ? (
                    <Alert>
                        <AlertTitle>Couldn&apos;t load community finds</AlertTitle>
                        <AlertDescription>
                            Check your connection and try again.
                        </AlertDescription>
                        <AnimatedButton
                            variant="outline"
                            className="mt-2 justify-self-start"
                            onClick={() => {
                                if (session.isError) void session.refetch();
                                else void recentFinds.refetch();
                            }}
                        >
                            Try again
                        </AnimatedButton>
                    </Alert>
                ) : userID == null ? (
                    <Alert>
                        <AlertTitle>Sign in to see community finds</AlertTitle>
                        <AlertDescription>Your session has ended. Sign in to explore discoveries.</AlertDescription>
                    </Alert>
                ) : recentFinds.data?.length === 0 ? (
                    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-5 py-8 text-center" role="status">
                        <span className="flex size-16 items-center justify-center rounded-full bg-muted text-card-foreground">
                            <Sprout aria-hidden className="size-8" />
                        </span>
                        <div>
                            <h2 className="font-heading text-lg font-medium">No community finds yet</h2>
                            <p className="mt-2 text-sm text-foreground">
                                When other Leaf Freaks discover plants, you&apos;ll see them here.
                            </p>
                        </div>
                    </div>
                ) : (
                    recentFinds.data?.map((find) => (
                        <Find key={find.find.id} recentFind={find} />
                    ))
                )}
            </div>
        </>
    )
}