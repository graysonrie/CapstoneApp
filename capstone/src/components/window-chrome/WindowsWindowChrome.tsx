"use client";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { cn } from "@/lib/utils";
import { Icon } from "@iconify/react";
import { ReactNode } from "react";

interface WindowsWindowChromeProps {
  appIconAndTitle?: ReactNode;
}

export default function WindowsWindowChrome({
  appIconAndTitle,
}: WindowsWindowChromeProps) {
  const handleMinimize = async () => {
    const appWindow = getCurrentWindow();
    await appWindow.minimize();
  };

  const handleMaximize = async () => {
    const appWindow = getCurrentWindow();
    await appWindow.toggleMaximize();
  };

  const handleClose = async () => {
    const appWindow = getCurrentWindow();
    await appWindow.close();
  };

  return (
    <div
      data-tauri-drag-region
      className="flex h-10 items-center justify-between px-4"
    >
      <div className="flex items-center gap-2">
        {/* App icon and title goes here */}
        {appIconAndTitle}
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={handleMinimize}
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-sm",
            "hover:bg-muted-foreground/10 transition-colors"
          )}
          aria-label="Minimize"
        >
          <Icon icon="mdi:minimize" className="h-4 w-4" />
        </button>
        <button
          onClick={handleMaximize}
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-sm",
            "hover:bg-muted-foreground/10 transition-colors"
          )}
          aria-label="Maximize"
        >
          <Icon icon="mdi:maximize" className="h-4 w-4" />
        </button>
        <button
          onClick={handleClose}
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-sm",
            "hover:bg-destructive hover:text-destructive-foreground transition-colors"
          )}
          aria-label="Close"
        >
          <Icon icon="mdi:close" className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
