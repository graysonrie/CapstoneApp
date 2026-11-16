"use client";

import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { getLeaderboard, getSession, type LeaderboardUser, type SessionInfo } from "@/generated";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { ArrowBigLeft } from "lucide-react";

interface LeaderboardUserProps {
    user: LeaderboardUser;
    position: number;
    loggedInUser: SessionInfo;
}

function LeaderboardCard({user, position, loggedInUser}: LeaderboardUserProps) {
    const firstName = user.first_name.trim();
    const lastName = user.last_name.trim();
    const displayName = [firstName, lastName].filter(Boolean).join(" ") || "Plant explorer";
    const initials = `${firstName[0] ?? ""}${lastName[0] ?? ""}`.toUpperCase() || "?";
    const isCurrentUser = user.id === loggedInUser.userId;

    return (
        <Card size="sm" className={cn(
            "gap-0 bg-card shadow-lg ring-1 ring-foreground/20 dark:ring-foreground/25",
            isCurrentUser && "bg-[color-mix(in_oklab,var(--card)_65%,var(--primary))] ring-2 ring-foreground"
        )}>
            <div className="flex items-center gap-3 px-4">
                <span className="w-7 shrink-0 text-center text-sm font-semibold tabular-nums text-card-foreground" aria-label={`Position ${position}`}>
                    {position}
                </span>
                <Avatar className="size-12 shrink-0" aria-hidden="true">
                    <AvatarFallback className="bg-primary/20 font-heading text-foreground">
                        {initials}
                    </AvatarFallback>
                </Avatar>
                <div className="min-w-0 flex-1">
                    <CardTitle className="break-words">{displayName}{isCurrentUser && <span className="ml-1 font-normal">(You)</span>}</CardTitle>
                    <CardDescription className="break-words text-card-foreground">{user.rank_title}</CardDescription>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                    <Badge variant="outline" className="border-card-foreground/30 text-card-foreground">Lv. {user.level}</Badge>
                    <span className="text-sm text-card-foreground">{user.xp.toLocaleString()} XP</span>
                </div>
            </div>
        </Card>
    )
}


export default function LeaderboardPage() {
    const session = useQuery({
        queryKey: ["session"],
        queryFn: getSession
    });
    const loggedInUser = session.data;
    const leaders = useQuery({
        queryKey: ["get_leaderboard", loggedInUser?.userId],
        queryFn: getLeaderboard,
        enabled: loggedInUser != null
    })

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
                    <ArrowBigLeft className="size-8" />
                </AnimatedButton>
                <div className="flex flex-col gap-1 px-1">
                    <h1 className="font-heading text-3xl font-semibold">Leaderboard</h1>
                    <p className="text-sm text-foreground">See how you stack up with the other LeafFreaks</p>
                </div>
            </div>
            <div className="flex w-full flex-col gap-4 py-8 px-4">
                {session.isLoading || (loggedInUser != null && leaders.isLoading) ? (
                    <p role="status">Loading leaderboard...</p>
                ) : session.isError || (loggedInUser != null && leaders.isError) ? (
                    <Alert>
                        <AlertTitle>Couldn&apos;t load leaderboard</AlertTitle>
                        <AlertDescription>Check your connection and try again.</AlertDescription>
                        <AnimatedButton variant="outline" className="mt-2 justify-self-start" onClick={() => {
                            if (session.isError) void session.refetch();
                            else void leaders.refetch();
                        }}>
                            Try again
                        </AnimatedButton>
                    </Alert>
                ) : loggedInUser == null ? (
                    <Alert>
                        <AlertTitle>Sign in to see the leaderboard</AlertTitle>
                        <AlertDescription>Your session has ended. Sign in to see the leaderboard.</AlertDescription>
                    </Alert>
                ) : leaders.data?.length === 0 ? (
                    <p role="status">No leaderboard entries yet.</p>
                ) : (
                    leaders.data?.map((v, index) => <LeaderboardCard key={v.id} user={v} position={index + 1} loggedInUser={loggedInUser}/>)
                )}
            </div>
        </>
    )
}