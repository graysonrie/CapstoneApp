"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Camera, Home, LogIn, User } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: Home },
  { href: "/plant_screenshot", label: "Scan", icon: Camera },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/login", label: "Login", icon: LogIn },
] as const;

export default function MobileNavBar() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-50 mx-4 mb-[max(1rem,env(safe-area-inset-bottom))] rounded-full border border-background bg-background/60 backdrop-blur-sm"
    >
      <ul className="mx-auto flex h-16 max-w-lg items-stretch justify-around px-2">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);

          return (
            <li key={href} className="flex flex-1">
              <Link
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex flex-1 flex-col items-center justify-center gap-0.5 text-xs font-medium transition-colors active:scale-95",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon
                  className="size-5"
                  strokeWidth={isActive ? 2.5 : 2}
                  aria-hidden
                />
                <span>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
