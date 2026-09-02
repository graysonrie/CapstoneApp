"use client";

import { useState } from "react";
import LoginForm from "@/features/auth/components/LoginForm";
import SignupForm from "@/features/auth/components/SignupForm";
import PointGridBg from "@/components/PointGridBg";

export default function LoginPage() {
  const [signUp, setSignUp] = useState(false);

  return (
    <main className="relative mx-auto items-center flex w-full max-w-md flex-1 flex-col gap-8 px-8 justify-center">
      <PointGridBg />
      <div className="w-full">{!signUp ? <LoginForm /> : <SignupForm />}</div>
      {!signUp ? (
        <div className="flex-col flex items-center">
          <p className="">Don&apos;t have an account?</p>
          <p
            className="font-bold text-primary hover:underline cursor-pointer"
            onClick={() => setSignUp(true)}
          >
            Sign Up
          </p>
        </div>
      ) : (
        <div className="flex-col flex items-center">
          <p className="">Already have an account?</p>
          <p
            className="font-bold text-primary hover:underline cursor-pointer"
            onClick={() => setSignUp(false)}
          >
          Log In 
          </p>
        </div>
      )}
    </main>
  );
}
