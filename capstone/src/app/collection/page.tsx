"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Input } from "@/components/ui/input";
import { PlantRarity } from "@/features/profile/types/profileTypes";
import FoundPlantComponent from "@/features/profile/components/FoundPlantComponent";
import { getProfile } from "@/generated";
import { TRANSITION1 } from "@/types/motionConstants";
import { useQuery } from "@tanstack/react-query";
import { HomeIcon, Search, Sprout, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { CollectionPlant } from "@/features/plant_scan/types";
import { Card } from "@/components/ui/card";


export default function PlantCollectionPage() {

    const query = useQuery({
        queryKey: ["profile"],
        queryFn: getProfile
    })

    const userData = query.data
    const foundPlants = userData?.found_plants ?? []
    const stats = userData?.stats;
    
    const [searchFilter, setSearchFilter] = useState("")

    const applyPlantFilter = (plant: CollectionPlant) => (
        plant.common_name.toLowerCase().includes(searchFilter.trim().toLowerCase())
        ||
        plant.scientific_name.toLowerCase().includes(searchFilter.trim().toLowerCase())
    )

    const filteredPlants = foundPlants.filter(applyPlantFilter)

    return (
        <>
            <PointGridBg/>
            <div className="sticky top-4 z-20 mx-auto flex w-full max-w-md items-center gap-3 px-4">
                <AnimatedButton
                href="/home"
                size="icon"
                variant="defaultGlass"
                className="size-16 shrink-0 rounded-full"
                aria-label="Home"
                >
                    <HomeIcon className="size-8" />
                </AnimatedButton>
                <div className="relative min-w-0 flex-1">
                    <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2" />
                    <Input 
                    className="pl-10 pr-10"
                    aria-label="Search plants" 
                    placeholder="Search for fav plant :)"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    />
                    {searchFilter && (
                        <button
                        type="button"
                        aria-label="Clear search"
                        onClick={() => setSearchFilter("")}
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-muted-foreground hover:text-foreground"
                        >
                            <X className="size-4" />
                        </button>
                    )}
                </div>
            </div>
            <motion.div
                className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col gap-5 px-4 pb-8 pt-6"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={TRANSITION1}
            >
                <div className="flex flex-col gap-1 px-1">
                    <h1 className="font-heading text-3xl font-semibold">My Collection</h1>
                    <p className="text-sm text-muted-foreground">Every plant you&apos;ve discovered</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <StatTile label="Total Found" value={stats?.scans ?? 0}></StatTile>
                    <StatTile label="Unique Plants" value={stats?.unique_species ?? 0}></StatTile>
                </div>
                {filteredPlants.length === 0 && !query.isLoading && (
                    <div className="flex flex-col items-center gap-2 py-12 text-center text-muted-foreground">
                        <Sprout className="size-10" />
                        <p className="text-sm">
                            {foundPlants.length === 0
                                ? "No plants yet. Scan one to start your collection!"
                                : "No plants match your search."}
                        </p>
                    </div>
                )}
                <motion.div
                    className="grid grid-cols-2 gap-3"
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ ...TRANSITION1, delay: 0.15 }}
                >
                <AnimatePresence mode="popLayout">
                {filteredPlants.map((plant) => (
                    <motion.div
                    key={plant.id}
                    className="h-full"
                    layout
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={TRANSITION1}
                    >
                        <FoundPlantComponent
                        id={plant.id}
                        imageBase64={plant.image_base64}
                        commonName={plant.common_name}
                        scientificName={plant.scientific_name}
                        rarity={plant.rarity as PlantRarity}
                        foundOn={plant.found_on}
                        />
                    </motion.div>
                ))}
                </AnimatePresence>
                </motion.div>
            
            </motion.div>
        </>
    )
}

function StatTile({ label, value, onClick }: { label: string; value: number | string, onClick?: () => void}) {
  return (
        <Card size="sm" className="flex-row items-center justify-center gap-2 rounded-full px-4 py-2 text-center" onClick={onClick}>
            <p className="font-heading text-base font-medium">{value}</p>
            <p className="text-xs text-muted-foreground">{label}</p>
    </Card>
  );
}
