"use client";

import type { ReactNode } from "react";
import Image from "next/image";
import { Images, X } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ImageViewerProps {
  src: string;
  alt: string;
  children: ReactNode;
  className?: string;
}

export default function ImageViewer({
  src,
  alt,
  children,
  className,
}: ImageViewerProps) {
  const reduceMotion = useReducedMotion();

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button type="button" className={className} aria-label={`View full-size image: ${alt}`}>
          {children}
        </button>
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        aria-describedby={undefined}
        className="fixed inset-0 z-[100] flex h-dvh w-screen max-w-none translate-x-0 translate-y-0 flex-col gap-0 rounded-none bg-gradient-to-b from-zinc-900 via-zinc-950 to-black p-0 text-white ring-0 motion-reduce:!animate-none sm:max-w-none"
      >
        <header className="flex items-center gap-3 border-b border-white/10 pl-[max(1.25rem,env(safe-area-inset-left))] pr-[max(1.25rem,env(safe-area-inset-right))] pb-4 pt-[max(1rem,env(safe-area-inset-top))]">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-white/10 text-white/85">
            <Images aria-hidden className="size-5" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wider text-white/65">Photo viewer</p>
            <DialogTitle className="mt-1 truncate text-sm font-medium leading-normal">
              {alt}
            </DialogTitle>
          </div>
          <DialogClose asChild>
            <button
              type="button"
              aria-label="Close image"
              className="flex size-11 shrink-0 items-center justify-center rounded-full bg-white/10 text-white ring-1 ring-white/20 transition-colors hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <X aria-hidden className="size-6" />
            </button>
          </DialogClose>
        </header>
        <div
          className="min-h-0 flex-1 pl-[max(1rem,env(safe-area-inset-left))] pr-[max(1rem,env(safe-area-inset-right))] py-5"
          style={{ perspective: 1200 }}
        >
          <motion.div
            className="relative size-full"
            initial={reduceMotion ? false : { rotateY: 180, scale: 0.9, opacity: 0 }}
            animate={{ rotateY: 0, scale: 1, opacity: 1 }}
            transition={reduceMotion ? { duration: 0 } : { duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            style={{ transformStyle: "preserve-3d" }}
          >
            <div className="absolute inset-0" style={{ backfaceVisibility: "hidden" }}>
              <Image
                src={src}
                alt={alt}
                fill
                sizes="100vw"
                unoptimized
                className="object-contain"
              />
            </div>
            <div
              aria-hidden
              className="absolute inset-0 flex items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-900 to-zinc-900 ring-1 ring-white/15"
              style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
            >
              <Images className="size-12 text-white/60" />
            </div>
          </motion.div>
        </div>
      </DialogContent>
    </Dialog>
  );
}