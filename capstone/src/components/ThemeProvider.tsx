"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Force the system theme if you are using a mica background
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      forcedTheme="light"
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
