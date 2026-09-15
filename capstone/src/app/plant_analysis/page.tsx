"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";
import type { PlantRarity } from "@/features/plant_scan/types";
import { TRANSITION1 } from "@/types/motionConstants";
import { HomeIcon } from "lucide-react";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> =
  {
    Common: "outline",
    Uncommon: "secondary",
    Rare: "default",
    SuperRare: "default",
    Exotic: "default",
  };

export default function PlantAnalysisPage() {
  const router = useRouter();
  const { result, imageSrc, previousPath } = useScanStore();

  useEffect(() => {
    if (!result) {
      router.replace(previousPath || "/home");
    }
  }, [result, previousPath, router]);

  if (!result) {
    return null;
  }

  const { scan, xp_awarded, daily_match, is_new_species, leveled_up } = result;
  const { identification, summary, sections, identification_notes } = scan;
  const commonName = identification.common_name ?? "Unknown plant";
  const scientificName = identification.scientific_name ?? "";

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
        className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col gap-5 px-6 py-8"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={TRANSITION1}
      >
        {imageSrc ? (
          <img
            src={imageSrc}
            alt={commonName}
            className="h-56 w-full rounded-3xl object-cover"
          />
        ) : null}

        <header className="flex flex-col gap-2 text-center">
          <h1 className="font-heading text-2xl font-medium">{commonName}</h1>
          {scientificName ? (
            <p className="italic text-muted-foreground">{scientificName}</p>
          ) : null}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {identification.rarity ? (
              <Badge variant={RARITY_VARIANT[identification.rarity]}>
                {identification.rarity}
              </Badge>
            ) : null}
            <Badge variant="outline">{identification.confidence} confidence</Badge>
          </div>
        </header>

        {daily_match ? (
          <Card className="border-primary/40 bg-primary/10">
            <CardHeader>
              <CardTitle>Today&apos;s plant found!</CardTitle>
              <CardDescription>
                You found {daily_match.common_name}. +{xp_awarded} XP
                {is_new_species ? " (includes new-species bonus)" : ""}.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : null}

        {xp_awarded > 0 && !daily_match ? (
          <p className="text-center text-sm font-medium text-primary">
            +{xp_awarded} XP{leveled_up ? " · You leveled up!" : ""}
          </p>
        ) : null}

        {xp_awarded > 0 && daily_match && leveled_up ? (
          <p className="text-center text-sm font-medium text-primary">
            You leveled up!
          </p>
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{summary}</p>
          </CardContent>
        </Card>

        <FactCard title="Appearance" body={sections.appearance} />
        {sections.native_range ? (
          <FactCard title="Native range" body={sections.native_range} />
        ) : null}

        {sections.care ? (
          <Card>
            <CardHeader>
              <CardTitle>Care</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground">
              {sections.care.light ? <p>Light: {sections.care.light}</p> : null}
              {sections.care.watering ? (
                <p>Water: {sections.care.watering}</p>
              ) : null}
              {sections.care.soil ? <p>Soil: {sections.care.soil}</p> : null}
              {sections.care.temperature ? (
                <p>Temperature: {sections.care.temperature}</p>
              ) : null}
            </CardContent>
          </Card>
        ) : null}

        {sections.interesting_facts.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Interesting facts</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="flex list-disc flex-col gap-2 pl-5 text-sm text-muted-foreground">
                {sections.interesting_facts.map((fact) => (
                  <li key={fact}>{fact}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ) : null}

        {sections.toxicity ? (
          <Card>
            <CardHeader>
              <CardTitle>Toxicity</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground">
              {sections.toxicity.humans ? (
                <p>Humans: {sections.toxicity.humans}</p>
              ) : null}
              {sections.toxicity.pets ? (
                <p>Pets: {sections.toxicity.pets}</p>
              ) : null}
            </CardContent>
          </Card>
        ) : null}

        {identification_notes.reasoning_summary ||
        identification_notes.uncertainty ? (
          <Card>
            <CardHeader>
              <CardTitle>Identification notes</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground">
              {identification_notes.reasoning_summary ? (
                <p>{identification_notes.reasoning_summary}</p>
              ) : null}
              {identification_notes.uncertainty ? (
                <p>{identification_notes.uncertainty}</p>
              ) : null}
            </CardContent>
          </Card>
        ) : null}
      </motion.div>
    </>
  );
}

function FactCard({ title, body }: { title: string; body: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{body}</p>
      </CardContent>
    </Card>
  );
}
