import { Inter, Manrope } from "next/font/google";
import type { Viewport } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/QueryProvider";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthShell } from "@/features/auth/components/AuthShell";
import { cn } from "@/lib/utils";

const manropeHeading = Manrope({
  subsets: ["latin"],
  variable: "--font-heading",
});

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

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
      className={cn("font-sans", inter.variable, manropeHeading.variable)}
      suppressHydrationWarning
    >
      <body className="antialiased bg-transparent">
        <ThemeProvider>
          <QueryProvider>
            {/* <AdaptiveWindowChrome /> */}
            <AuthShell>{children}</AuthShell>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
