"use client";

import { useState } from "react";
import LoginForm from "@/features/auth/components/LoginForm";
import SignupForm from "@/features/auth/components/SignupForm";
import { Swirl } from "@/components/ui/canvas-effects/Swirl";
import { LeafIcon } from "lucide-react";

function Title() {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="flex items-center gap-2">
        <LeafIcon className="size-5 text-primary/50" />

        <p className="text-center pr-5 text-lg font-bold font-title tracking-tight text-foreground/50">
          LeafFreak
        </p>
      </div>
      <p className="text-center uppercase text-sm font-medium text-muted-foreground/50">
        Become a freak of nature
      </p>
    </div>
  );
}

export default function LoginPage() {
  // Default to sign up page
  const [signUp, setSignUp] = useState(true);

  return (
    <>
      <div className="inset-0 fixed">
        <Swirl />
      </div>

      <div className="relative flex flex-1 flex-col">
        <header className="pointer-events-none absolute inset-x-0 top-0 z-10 px-8 pt-8">
          <Title />
        </header>

        <main className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col items-center justify-center gap-8 px-8">
          <div className="w-full">
            {!signUp ? <LoginForm /> : <SignupForm />}
          </div>
          {!signUp ? (
            <div className="flex w-full flex-col items-center gap-8 text-lg font-brand">
              <div className="flex flex-col items-center">
                <p>New to PlantApp?</p>
                <p
                  className="cursor-pointer text-xl font-semibold text-primary hover:underline"
                  onClick={() => setSignUp(true)}
                >
                  Sign Up
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center text-lg font-brand">
              <p>Already have an account?</p>
              <p
                className="cursor-pointer text-xl font-semibold text-primary hover:underline"
                onClick={() => setSignUp(false)}
              >
                Log In
              </p>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
