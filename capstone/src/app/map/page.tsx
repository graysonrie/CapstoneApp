"use client";

import { useEffect, useRef, useState } from "react"
import * as maptiler from "@maptiler/sdk"
import AnimatedButton from "@/components/generic/AnimatedButton";
import { ArrowLeft, LocateFixed, Sprout } from "lucide-react";
import PointGridBg from "@/components/PointGridBg";

export default function MapPage() {

    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maptiler.Map | null>(null);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

    useEffect(() => {
        if (!mapContainer.current) return
        maptiler.config.apiKey = "tPVHaTQyrPlxoSSHXp5D"
        map.current = new maptiler.Map({
            container: mapContainer.current,
            style: "hybrid-v4",
            center: [0, 0],
            zoom: 12,
            minZoom: 2,
            maxZoom: 18
        })

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                ({ coords }) => {
                    const coordinates: [number, number] = [coords.longitude, coords.latitude];
                    setUserLocation(coordinates);
                    map.current?.setCenter(coordinates);
                },
                (error) => {
                    console.error("Unable to get user location:", error);
                }
            )
        }

        return () => {
            map.current?.remove()
            map.current = null
        }
    }, [])

    const centerOnUser = () => {
        if (!userLocation) return;
        map.current?.flyTo({ center: userLocation, zoom: 14, duration: 700 });
    };

    return (
        <div className="fixed inset-x-0 top-[env(safe-area-inset-top)] bottom-[calc(7rem+max(1rem,env(safe-area-inset-bottom)))]">
            <PointGridBg/>
            <div ref={mapContainer} className="absolute inset-0 h-full w-full" />
            <div aria-hidden className="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/35 via-transparent to-black/25" />

            <header className="absolute inset-x-4 top-4 z-10 flex items-center gap-3">
                    <AnimatedButton
                    href="/profile"
                    size="icon"
                    variant="defaultGlass"
                    className="size-12 rounded-full border-white/60 bg-white/75 text-foreground shadow-lg backdrop-blur-xl"
                    aria-label="Back to home"
                    >
                    <ArrowLeft className="size-5" />
                    </AnimatedButton>

                <div className="flex min-w-0 items-center gap-3 rounded-full border border-white/60 bg-white/80 py-2 pl-2.5 pr-5 shadow-lg backdrop-blur-xl">
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        <Sprout className="size-5" aria-hidden />
                    </span>
                    <div className="min-w-0">
                        <h1 className="truncate font-heading text-sm font-semibold text-foreground">Plant map</h1>
                        <p className="truncate text-xs text-muted-foreground">Explore your findings</p>
                    </div>
                </div>
            </header>

            <footer className="absolute inset-x-4 bottom-4 z-10 flex justify-end">
                <AnimatedButton
                    type="button"
                    onClick={centerOnUser}
                    disabled={!userLocation}
                    size="icon"
                    variant="defaultGlass"
                    className="size-12 rounded-full border-white/60 bg-white/85 text-foreground shadow-xl backdrop-blur-xl disabled:opacity-60"
                    aria-label="Center map on your location"
                    title="Center on your location"
                >
                    <LocateFixed className="size-5" />
                </AnimatedButton>
            </footer>
        </div>
    )
}