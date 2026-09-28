"use client";

import { useEffect, useRef, useState } from "react"
import * as maptiler from "@maptiler/sdk"
import AnimatedButton from "@/components/generic/AnimatedButton";
import { ArrowLeft, LocateFixed, Sprout } from "lucide-react";
import PointGridBg from "@/components/PointGridBg";
import { useQuery } from "@tanstack/react-query";
import { getUserImageLocations } from "@/generated";

export default function MapPage() {

    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maptiler.Map | null>(null);
    const markers = useRef<maptiler.Marker[]>([]);
    const [mapInstance, setMapInstance] = useState<maptiler.Map | null>(null);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

    const imageLocationsQuery = useQuery({
        queryKey: ["imageLocations"],
        queryFn: getUserImageLocations
    })
    const imageLocations = imageLocationsQuery.data ?? []
    const locatedImages = imageLocations.filter((image) => image.location)

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
        setMapInstance(map.current)

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                ({ coords }) => {
                    const coordinates: [number, number] = [coords.longitude, coords.latitude];
                    setUserLocation(coordinates);
                },
                (error) => {
                    console.error("Unable to get user location:", error);
                }
            )
        }

        console.log(imageLocations)

        return () => {
            map.current?.remove()
            map.current = null
        }
    }, [])

    useEffect(() => {
        if (!mapInstance || locatedImages.length > 0 || !userLocation) return;
        mapInstance.setCenter(userLocation);
    }, [mapInstance, userLocation, locatedImages.length]);

    useEffect(() => {
        if (!mapInstance || !imageLocationsQuery.data) return;

        markers.current.forEach((marker) => marker.remove());
        markers.current = [];

        const points: [number, number][] = [];

        for (const image of imageLocationsQuery.data) {
            if (!image.location) continue;

            const coordinates: [number, number] = [
                image.location.longitude,
                image.location.latitude,
            ];
            points.push(coordinates);

            const markerElement = document.createElement("button");
            markerElement.type = "button";
            markerElement.setAttribute(
                "aria-label",
                `View photo of ${image.common_name}`,
            );
            markerElement.style.cssText = [
                "width:48px",
                "height:48px",
                "padding:3px",
                "border:2px solid white",
                "border-radius:50%",
                "overflow:hidden",
                "background:#287d46",
                "box-shadow:0 3px 12px rgb(0 0 0 / 35%)",
                "cursor:pointer",
            ].join(";");

            if (image.thumbnail_data_url) {
                const thumbnail = document.createElement("img");
                thumbnail.src = image.thumbnail_data_url;
                thumbnail.alt = "";
                thumbnail.draggable = false;
                thumbnail.style.cssText = "width:100%;height:100%;border-radius:50%;object-fit:cover";
                markerElement.append(thumbnail);
            } else {
                markerElement.textContent = image.common_name.slice(0, 1).toUpperCase();
                markerElement.style.cssText += ";color:white;font:700 18px/1 sans-serif";
            }

            const popupContent = document.createElement("div");
            popupContent.style.cssText = "width:190px;overflow:hidden;border-radius:8px";
            if (image.thumbnail_data_url) {
                const popupImage = document.createElement("img");
                popupImage.src = image.thumbnail_data_url;
                popupImage.alt = image.common_name;
                popupImage.style.cssText = "display:block;width:190px;height:130px;object-fit:cover";
                popupContent.append(popupImage);
            }
            const caption = document.createElement("p");
            caption.textContent = image.common_name;
            caption.style.cssText = "margin:0;padding:8px 10px;font:600 13px/1.3 sans-serif;color:#202820";
            popupContent.append(caption);

            const popup = new maptiler.Popup({ offset: 28, maxWidth: "220px" })
                .setDOMContent(popupContent);
            const marker = new maptiler.Marker({ element: markerElement, anchor: "bottom" })
                .setLngLat(coordinates)
                .setPopup(popup)
                .addTo(mapInstance);
            markers.current.push(marker);
        }

        if (points.length === 1) {
            mapInstance.flyTo({ center: points[0], zoom: 14, duration: 700 });
        } else if (points.length > 1) {
            const longitudes = points.map(([longitude]) => longitude);
            const latitudes = points.map(([, latitude]) => latitude);
            mapInstance.fitBounds(
                [
                    [Math.min(...longitudes), Math.min(...latitudes)],
                    [Math.max(...longitudes), Math.max(...latitudes)],
                ],
                { padding: 72, maxZoom: 14 },
            );
        }

        return () => {
            markers.current.forEach((marker) => marker.remove());
            markers.current = [];
        };
    }, [mapInstance, imageLocationsQuery.data]);

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