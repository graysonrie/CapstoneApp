"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";
import type { PlantGeoData, PlantRarity } from "@/features/plant_scan/types";
import { getPlantGeoDistribution } from "@/generated";
import { TRANSITION1 } from "@/types/motionConstants";
import * as maptiler from "@maptiler/sdk";
import {
  ArrowBigLeft,
  Droplets,
  Leaf,
  MapPin,
  PawPrint,
  Sparkles,
  Sun,
  Thermometer,
  TriangleAlert,
} from "lucide-react";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";

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
  const hasReward = xp_awarded > 0 || Boolean(daily_match) || leveled_up;

  return (
    <>
      <PointGridBg />
      <motion.main
        className="relative z-10 mx-auto flex w-full max-w-5xl flex-1 flex-col gap-5 px-4 py-5 sm:gap-6 sm:px-6 sm:py-8"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={TRANSITION1}
      >
        <section className="relative isolate flex min-h-80 flex-col justify-end overflow-hidden rounded-4xl bg-gradient-to-br from-primary/30 via-secondary to-muted shadow-lg sm:min-h-[26rem]">
          {imageSrc ? (
            <img
              src={imageSrc}
              alt={`Photo of ${commonName}`}
              className="absolute inset-0 z-0 size-full object-cover"
            />
          ) : (
            <Leaf
              aria-hidden
              className="absolute inset-0 z-0 m-auto size-28 text-primary/35"
            />
          )}
          <div className="absolute inset-0 z-10 bg-gradient-to-t from-black/80 via-black/20 to-black/20" />

          <AnimatedButton
            href={previousPath || "/home"}
            size="icon"
            variant="defaultGlass"
            className="absolute left-4 top-4 z-20 size-12 rounded-full border-white/30 bg-black/20 text-white hover:bg-black/40 sm:left-5 sm:top-5"
            aria-label="Back"
          >
            <ArrowBigLeft className="size-6" />
          </AnimatedButton>

          <div className="relative z-20 flex flex-col gap-3 p-5 text-white sm:p-8">
            <div className="flex flex-wrap gap-2">
              {identification.rarity ? (
                <Badge
                  variant={RARITY_VARIANT[identification.rarity]}
                  className="border-white/30 bg-black/25 text-white backdrop-blur-sm"
                >
                  {identification.rarity}
                </Badge>
              ) : null}
              <Badge className="border-white/30 bg-black/25 text-white backdrop-blur-sm">
                {identification.confidence} confidence
              </Badge>
            </div>
            <div>
              <h1 className="font-heading text-3xl font-semibold leading-tight sm:text-5xl">
                {commonName}
              </h1>
              {scientificName ? (
                <p className="mt-1 text-base italic text-white/80 sm:text-lg">
                  {scientificName}
                </p>
              ) : null}
              {identification.family ? (
                <p className="mt-2 text-sm text-white/75">
                  {identification.family} family
                </p>
              ) : null}
            </div>
          </div>
        </section>

        {hasReward ? (
          <Card className="border-primary/40 bg-primary/10">
            <CardContent className="flex items-start gap-4 py-5">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary/15 text-primary">
                <Sparkles aria-hidden className="size-5" />
              </span>
              <div className="min-w-0">
                <CardTitle>
                  {daily_match ? "Daily plant discovered!" : "Scan rewards"}
                </CardTitle>
                <CardDescription className="mt-1">
                  {daily_match
                    ? `You found ${daily_match.common_name}.`
                    : is_new_species
                      ? "A new species added to your collection."
                      : "Your discovery has been added to your collection."}
                  {xp_awarded > 0 ? ` +${xp_awarded} XP.` : ""}
                  {is_new_species && daily_match
                    ? " Includes the new-species bonus."
                    : ""}
                  {leveled_up ? " You leveled up!" : ""}
                </CardDescription>
              </div>
            </CardContent>
          </Card>
        ) : null}

        <Card className="border-primary/15">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Leaf aria-hidden className="size-5 text-primary" />
              At a glance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-7 text-muted-foreground sm:text-base">
              {summary}
            </p>
          </CardContent>
        </Card>

        <div className="grid gap-5 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf aria-hidden className="size-5 text-primary" />
                Plant profile
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <TextSection title="Appearance" body={sections.appearance} />
              {sections.native_range ? (
                <TextSection
                  title="Native range"
                  body={sections.native_range}
                  icon={<MapPin aria-hidden className="size-4" />}
                />
              ) : null}
            </CardContent>
          </Card>

          {scientificName ? (
            <PlantDistributionMap
              key={scientificName}
              scientificName={scientificName}
              className="lg:col-span-2"
            />
          ) : null}

          {sections.care ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sun aria-hidden className="size-5 text-primary" color="#df8e1d"/>
                  Care guide
                </CardTitle>
                <CardDescription>
                  Recommendations for helping this plant thrive
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 sm:grid-cols-2">
                {sections.care.light ? (
                  <CareItem
                    icon={<Sun aria-hidden className="size-4" color="#df8e1d"/>}
                    label="Light"
                    body={sections.care.light}
                  />
                ) : null}
                {sections.care.watering ? (
                  <CareItem
                    icon={<Droplets aria-hidden className="size-4" color="#1e66f5"/>}
                    label="Water"
                    body={sections.care.watering}
                  />
                ) : null}
                {sections.care.soil ? (
                  <CareItem
                    icon={<Leaf aria-hidden className="size-4" color="#40a02b"/>}
                    label="Soil"
                    body={sections.care.soil}
                  />
                ) : null}
                {sections.care.temperature ? (
                  <CareItem
                    icon={<Thermometer aria-hidden className="size-4" color="#e64553"/>}
                    label="Temperature"
                    body={sections.care.temperature}
                  />
                ) : null}
              </CardContent>
            </Card>
          ) : null}

          {sections.interesting_facts.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles aria-hidden className="size-5 text-primary" />
                  Interesting facts
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                {sections.interesting_facts.map((fact, index) => (
                  <p
                    key={`${index}-${fact}`}
                    className="border-l-2 border-primary/40 pl-4 text-sm leading-6 text-muted-foreground"
                  >
                    {fact}
                  </p>
                ))}
              </CardContent>
            </Card>
          ) : null}

          {sections.toxicity ? (
            <Card className="border-amber-500/25 bg-amber-500/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PawPrint aria-hidden className="size-5 text-amber-600" />
                  Toxicity &amp; safety
                </CardTitle>
                <CardDescription>
                  Keep these notes in mind around people and pets
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                {sections.toxicity.humans ? (
                  <TextSection
                    title="People"
                    body={sections.toxicity.humans}
                  />
                ) : null}
                {sections.toxicity.pets ? (
                  <TextSection title="Pets" body={sections.toxicity.pets} />
                ) : null}
              </CardContent>
              <CardFooter>
                <div className="w-full rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-amber-950 dark:text-amber-100">
                  <TextSection
                  title="Warning"
                  body="We took our best guess at identifying this plant, but mistakes can happen. Only handle and consume plants if you're certain they are safe."
                  icon={<TriangleAlert className="size-5 text-amber-600 dark:text-amber-400" />}
                  />
                </div>
              </CardFooter>
            </Card>
          ) : null}
        </div>

        {identification_notes.reasoning_summary ||
        identification_notes.uncertainty ? (
          <details className="group rounded-3xl border border-border/70 bg-card/80 px-5 py-4 shadow-sm backdrop-blur-sm">
            <summary className="cursor-pointer list-none font-heading text-base font-medium marker:hidden">
              <span className="flex items-center justify-between gap-3">
                How we identified this plant
                <span className="text-sm text-muted-foreground transition-transform group-open:rotate-180">
                  ↓
                </span>
              </span>
            </summary>
            <div className="mt-4 flex flex-col gap-4 border-t pt-4 text-sm leading-6 text-muted-foreground">
              {identification_notes.reasoning_summary ? (
                <TextSection
                  title="Reasoning"
                  body={identification_notes.reasoning_summary}
                />
              ) : null}
              {identification_notes.uncertainty ? (
                <TextSection
                  title="Uncertainty"
                  body={identification_notes.uncertainty}
                />
              ) : null}
            </div>
          </details>
        ) : null}
      </motion.main>
    </>
  );
}

function PlantDistributionMap({
  scientificName,
  className,
}: {
  scientificName: string;
  className?: string;
}) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [observations, setObservations] = useState<PlantGeoData[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const points = useMemo(
    () =>
      observations.filter(
        (
          observation,
        ): observation is PlantGeoData & {
          decimalLatitude: number;
          decimalLongitude: number;
        } =>
          observation.decimalLatitude != null &&
          observation.decimalLongitude != null &&
          Number.isFinite(observation.decimalLatitude) &&
          Number.isFinite(observation.decimalLongitude) &&
          Math.abs(observation.decimalLatitude) <= 90 &&
          Math.abs(observation.decimalLongitude) <= 180,
      ),
    [observations],
  );

  useEffect(() => {
    let active = true;

    getPlantGeoDistribution({ scientificName })
      .then((response) => {
        if (!active) return;
        setObservations(response.results);
        setTotalCount(response.count);
        console.log(response)
      })
      .catch((cause: unknown) => {
        if (!active) return;
        setError(
          cause instanceof Error
            ? cause.message
            : typeof cause === "string"
              ? cause
              : "Could not load distribution data.",
        );
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [scientificName]);

  useEffect(() => {
    const container = mapContainer.current;
    if (isLoading || error || points.length === 0 || !container) return;

    maptiler.config.apiKey = "tPVHaTQyrPlxoSSHXp5D";
    const map = new maptiler.Map({
      container,
      style: "streets-v2",
      center: [0, 15],
      zoom: 0.8,
      minZoom: 0,
      maxZoom: 12,
      navigationControl: false,
      geolocateControl: false,
      terrainControl: false,
      fullscreenControl: false,
      scaleControl: false,
    });

    const data: GeoJSON.FeatureCollection<GeoJSON.Point> = {
      type: "FeatureCollection",
      features: points.map((point) => ({
        type: "Feature",
        properties: {},
        geometry: {
          type: "Point",
          coordinates: [point.decimalLongitude, point.decimalLatitude],
        },
      })),
    };
    const addHeatmap = () => {
      maptiler.helpers.addHeatmap(map, {
        data,
        radius: 5,
        intensity: 1.0,
      });
      setMapLoaded(true);
    };

    if (map.isStyleLoaded()) {
      addHeatmap();
    } else {
      map.once("load", addHeatmap);
    }

    if (points.length === 1) {
      map.setCenter([points[0].decimalLongitude, points[0].decimalLatitude]);
      map.setZoom(3);
    } else {
      const west = Math.min(...points.map((point) => point.decimalLongitude));
      const east = Math.max(...points.map((point) => point.decimalLongitude));
      const south = Math.min(...points.map((point) => point.decimalLatitude));
      const north = Math.max(...points.map((point) => point.decimalLatitude));
      if (west === east && south === north) {
        map.setCenter([west, south]);
        map.setZoom(3);
      } else {
        const longitudePadding = west === east ? 0.1 : 0;
        const latitudePadding = south === north ? 0.1 : 0;
        map.fitBounds(
          [
            [
              Math.max(-180, west - longitudePadding),
              Math.max(-90, south - latitudePadding),
            ],
            [
              Math.min(180, east + longitudePadding),
              Math.min(90, north + latitudePadding),
            ],
          ],
          { padding: 36, maxZoom: 5 },
        );
      }
    }

    return () => {
      map.off("load", addHeatmap);
      map.remove();
    };
  }, [error, isLoading, points]);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin aria-hidden className="size-5 text-primary" />
          Where it has been observed
        </CardTitle>
        <CardDescription>
          GBIF occurrence records show reported observations, not the plant’s
          exact native range.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div
            className="flex h-64 items-center justify-center rounded-2xl bg-muted/60 text-sm text-muted-foreground"
            role="status"
          >
            Loading observation data...
          </div>
        ) : error ? (
          <div
            className="flex h-64 items-center justify-center rounded-2xl bg-muted/60 px-5 text-center text-sm text-muted-foreground"
            role="status"
          >
            Distribution data is unavailable right now: {error}
          </div>
        ) : points.length === 0 ? (
          <div className="flex h-64 items-center justify-center rounded-2xl bg-muted/60 px-5 text-center text-sm text-muted-foreground">
            No georeferenced observations were found for this identification.
          </div>
        ) : (
          <>
            <div className="relative overflow-hidden rounded-2xl">
              <div
                ref={mapContainer}
                className="h-64 w-full bg-muted sm:h-80"
                aria-label={`Heatmap of ${scientificName} observation records`}
              />
              {!mapLoaded ? (
                <div
                  className="pointer-events-none absolute inset-0 flex items-center justify-center bg-background/30 text-sm text-muted-foreground"
                  role="status"
                >
                  Preparing map...
                </div>
              ) : null}
            </div>
            <p className="mt-3 text-xs text-muted-foreground">
              Showing {points.length} mapped observations
              {totalCount > points.length ? ` from ${totalCount} records` : ""}.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function TextSection({
  title,
  body,
  icon,
}: {
  title: string;
  body: string;
  icon?: ReactNode;
}) {
  return (
    <section className="flex flex-col gap-1.5">
      <h2 className="flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </h2>
      <p className="text-sm leading-6 text-muted-foreground">{body}</p>
    </section>
  );
}

function CareItem({
  icon,
  label,
  body,
}: {
  icon: ReactNode;
  label: string;
  body: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-2xl bg-muted/60 p-3">
      <span className="mt-0.5 shrink-0 text-primary">{icon}</span>
      <div className="min-w-0">
        <h2 className="text-sm font-semibold">{label}</h2>
        <p className="mt-1 text-sm leading-5 text-muted-foreground">{body}</p>
      </div>
    </div>
  );
}
