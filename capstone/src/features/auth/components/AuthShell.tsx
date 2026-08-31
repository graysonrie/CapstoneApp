"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import MobileNavBar from "@/components/mobile-nav-bar";
import { toUser } from "@/features/auth/api/auth";
import { useAuthStore } from "@/features/auth/store/useAuthStore";
import { getSupabase } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";

export function AuthShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const isSessionReady = useAuthStore((state) => state.isSessionReady);
  const setUser = useAuthStore((state) => state.setUser);
  const clearUser = useAuthStore((state) => state.clearUser);
  const setSessionReady = useAuthStore((state) => state.setSessionReady);

  useEffect(() => {
    const supabase = getSupabase();
    let cancelled = false;

    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) {
        return;
      }
      if (data.session?.user) {
        setUser(toUser(data.session.user));
      } else {
        clearUser();
      }
      setSessionReady(true);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(toUser(session.user));
      } else {
        clearUser();
      }
      setSessionReady(true);
    });

    return () => {
      cancelled = true;
      subscription.unsubscribe();
    };
  }, [setUser, clearUser, setSessionReady]);

  const isLoginRoute = pathname === "/login";
  const shouldRedirectToLogin =
    isSessionReady && !user && !isLoginRoute;
  const shouldRedirectFromLogin =
    isSessionReady && !!user && isLoginRoute;

  useEffect(() => {
    if (shouldRedirectToLogin) {
      router.replace("/login");
    } else if (shouldRedirectFromLogin) {
      router.replace("/home");
    }
  }, [shouldRedirectToLogin, shouldRedirectFromLogin, router]);

  const showNav = isSessionReady && !!user;

  return (
    <>
      <div
        className={cn(
          "flex min-h-dvh flex-col pt-[env(safe-area-inset-top)]",
          showNav
            ? "pb-[calc(5rem+env(safe-area-inset-bottom))]"
            : "pb-[env(safe-area-inset-bottom)]",
        )}
      >
        {shouldRedirectToLogin ? null : children}
      </div>
      {showNav ? <MobileNavBar /> : null}
    </>
  );
}
