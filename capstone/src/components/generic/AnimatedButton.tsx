"use client";
import { cva, type VariantProps } from "class-variance-authority";
import { motion } from "motion/react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const HOVER_SCALE = 1.2;
const REST_SCALE = 1 / HOVER_SCALE;
const TAP_SCALE = 0.9 * REST_SCALE;

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-4xl border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-[color,background-color,border-color,box-shadow] outline-none select-none touch-manipulation focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/80",
        glass:
          "backdrop-blur-sm bg-primary/80 border-2 border-primary to-primary text-primary-foreground hover:bg-secondary/60 hover:border-secondary/80",

        outline:
          "border-border bg-background hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:bg-transparent dark:hover:bg-input/30",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-[color-mix(in_oklch,var(--secondary),var(--foreground)_5%)] aria-expanded:bg-secondary aria-expanded:text-secondary-foreground",
        ghost:
          "hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:hover:bg-muted/50",
        destructive:
          "bg-destructive/10 text-destructive hover:bg-destructive/20 focus-visible:border-destructive/40 focus-visible:ring-destructive/20 dark:bg-destructive/20 dark:hover:bg-destructive/30 dark:focus-visible:ring-destructive/40",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default:
          "h-9 gap-1.5 px-3 has-data-[icon=inline-end]:pr-2.5 has-data-[icon=inline-start]:pl-2.5",
        xs: "h-6 gap-1 px-2.5 text-xs has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1 px-3 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        lg: "h-14 gap-1.5 text-lg px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
        icon: "size-9",
        "icon-xs": "size-6 [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
  },
);

const MotionLink = motion.create(Link);

type AnimatedButtonBase = VariantProps<typeof buttonVariants> & {
  className?: string;
  children?: React.ReactNode;
  disabled?: boolean;
};

type AnimatedButtonAsButton = AnimatedButtonBase &
  Omit<React.ComponentProps<typeof motion.button>, keyof AnimatedButtonBase | "href"> & {
    href?: undefined;
  };

type AnimatedButtonAsLink = AnimatedButtonBase &
  Omit<
    React.ComponentProps<typeof MotionLink>,
    keyof AnimatedButtonBase | "href"
  > & {
    href: string;
  };

type AnimatedButtonProps = AnimatedButtonAsButton | AnimatedButtonAsLink;

function useCanHover() {
  const [canHover, setCanHover] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(hover: hover) and (pointer: fine)");
    const update = () => setCanHover(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return canHover;
}

export default function AnimatedButton({
  className,
  children,
  size = "default",
  variant = "default",
  disabled,
  href,
  ...props
}: AnimatedButtonProps) {
  const canHover = useCanHover();
  const classes = cn(
    buttonVariants({ variant, size, className }),
    "origin-center",
  );
  const sharedMotion = {
    initial: false as const,
    animate: { scale: REST_SCALE },
    whileHover: !disabled && canHover ? { scale: 1 } : undefined,
    whileTap: !disabled ? { scale: TAP_SCALE } : undefined,
    transition: { duration: 0.1 },
  };

  if (href) {
    const { onClick, ...linkProps } = props as Omit<
      AnimatedButtonAsLink,
      "href"
    >;

    return (
      <MotionLink
        href={href}
        className={classes}
        aria-disabled={disabled || undefined}
        tabIndex={disabled ? -1 : undefined}
        {...linkProps}
        {...sharedMotion}
        onClick={(event) => {
          if (disabled) {
            event.preventDefault();
            return;
          }
          onClick?.(event);
        }}
      >
        {children}
      </MotionLink>
    );
  }

  const { type = "button", ...buttonProps } = props as AnimatedButtonAsButton;

  return (
    <motion.button
      type={type}
      disabled={disabled}
      className={classes}
      {...buttonProps}
      {...sharedMotion}
    >
      {children}
    </motion.button>
  );
}
