"use client";

import { useState } from "react";
import LoginForm from "@/features/auth/components/LoginForm";
import SignupForm from "@/features/auth/components/SignupForm";
import PointGridBg from "@/components/PointGridBg";
import Link from "next/link";

export default function LoginPage() {
  // Default to sign up page
  const [signUp, setSignUp] = useState(true);

  return (
    <main className="relative mx-auto items-center flex w-full max-w-md flex-1 flex-col gap-8 px-8 justify-center">
      <div className="w-full">{!signUp ? <LoginForm /> : <SignupForm />}</div>
      {!signUp ? (
        <div className="flex-col flex w-full items-center gap-8 text-lg font-brand">
          <div className="flex-col items-center flex">
            <p className="">New to PlantApp?</p>
            <p
              className="font-semibold text-primary hover:underline cursor-pointer text-xl"
              onClick={() => setSignUp(true)}
            >
              Sign Up
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-col flex items-center text-lg font-brand">
          <p className="">Already have an account?</p>
          <p
            className="font-semibold text-primary hover:underline cursor-pointer text-xl"
            onClick={() => setSignUp(false)}
          >
            Log In
          </p>
        </div>
      )}
    </main>
  );
}
