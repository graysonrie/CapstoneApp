import { Playfair_Display, Noto_Sans } from "next/font/google";
import type { Viewport } from "next";
import "./globals.css";
import AdaptiveWindowChrome from "@/components/window-chrome/AdaptiveWindowChrome";
import MobileNavBar from "@/components/MobileNavBar";
import { QueryProvider } from "@/components/QueryProvider";
import { ThemeProvider } from "@/components/ThemeProvider";
import { cn } from "@/lib/utils";

const playfairDisplayHeading = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-heading",
});

const notoSans = Noto_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

/** Disable pinch / double-tap zoom so the WebView feels like a native app.
 *  viewportFit cover draws under the iOS status bar / home indicator. */
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn(
        "font-sans",
        notoSans.variable,
        playfairDisplayHeading.variable,
      )}
      suppressHydrationWarning
    >
      <body className="antialiased bg-transparent">
        <ThemeProvider>
          <QueryProvider>
            {/* <AdaptiveWindowChrome /> */}
            <div className="min-h-dvh pt-[env(safe-area-inset-top)] pb-[calc(5rem+env(safe-area-inset-bottom))]">
              {children}
            </div>
            <MobileNavBar />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
