"use client";
import WindowsWindowChrome from "./WindowsWindowChrome";
import { ReactNode } from "react";

interface AdaptiveWindowChromeProps {
  /** The app icon and title to display in the window chrome for Windows targets */
  appIconAndTitle?: ReactNode;
}

export default function AdaptiveWindowChrome({
  appIconAndTitle,
}: AdaptiveWindowChromeProps) {
  return <WindowsWindowChrome appIconAndTitle={appIconAndTitle} />;
}
