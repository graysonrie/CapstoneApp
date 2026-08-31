"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import LoginForm from "@/features/auth/components/LoginForm";
import SignupForm from "@/features/auth/components/SignupForm";

const formVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 32 : -32,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -32 : 32,
    opacity: 0,
  }),
};

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [direction, setDirection] = useState(1);
  const isLogin = mode === "login";

  function showSignup() {
    setDirection(1);
    setMode("signup");
  }

  function showLogin() {
    setDirection(-1);
    setMode("login");
  }

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col overflow-x-hidden px-8 justify-center">
      <div className="flex flex-col justify-center gap-8 py-8">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={mode}
            custom={direction}
            variants={formVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: "easeOut" }}
            className="flex flex-col gap-8"
          >
            <p className="text-center text-xl font-bold">
              {isLogin ? "Log In" : "Sign Up"}
            </p>
            {isLogin ? <LoginForm /> : <SignupForm />}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex justify-center pb-[max(1.5rem,env(safe-area-inset-bottom))]">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={mode}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.16 }}
          >
            {isLogin ? (
              <Button
                type="button"
                variant="link"
                className="h-auto text-base"
                onClick={showSignup}
              >
                Don&apos;t have an account? Sign Up
              </Button>
            ) : (
              <Button
                type="button"
                variant="link"
                className="h-auto text-base"
                onClick={showLogin}
              >
                Already have an account? Log In
              </Button>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </main>
  );
}
