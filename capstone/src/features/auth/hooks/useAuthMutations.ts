"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { login, signup } from "@/features/auth/api/auth";
import { useAuthStore } from "@/features/auth/store/useAuthStore";
import type { LoginInput, SignupInput, User } from "@/features/auth/types";

function useAuthSuccess() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);

  return (user: User) => {
    setUser(user);
    router.push("/home");
  };
}

export function useLoginMutation() {
  const onAuthSuccess = useAuthSuccess();

  return useMutation({
    mutationFn: (input: LoginInput) => login(input),
    onSuccess: onAuthSuccess,
  });
}

export function useSignupMutation() {
  const onAuthSuccess = useAuthSuccess();

  return useMutation({
    mutationFn: (input: SignupInput) => signup(input),
    onSuccess: onAuthSuccess,
  });
}
