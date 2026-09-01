"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { logIn, LogInParams, signUp, SignUpParams } from "@/generated";
import { sessionQueryKey } from "./useIsValidSession";

function useAuthSuccess() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return () => {
    queryClient.setQueryData(sessionQueryKey, true);
    router.push("/home");
  };
}

export function useLoginMutation() {
  const onAuthSuccess = useAuthSuccess();

  return useMutation({
    mutationFn: (input: LogInParams) => logIn(input),
    onSuccess: onAuthSuccess,
  });
}

export function useSignupMutation() {
  const onAuthSuccess = useAuthSuccess();

  return useMutation({
    mutationFn: (input: SignUpParams) => signUp(input),
    onSuccess: onAuthSuccess,
  });
}
