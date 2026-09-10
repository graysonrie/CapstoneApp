"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  completeProfile,
  CompleteProfileParams,
  getSession,
  logIn,
  LogInParams,
  logOut,
  signUp,
  SignUpParams,
} from "@/generated";
import { sessionQueryKey } from "./useIsValidSession";

async function routeAfterAuth(
  router: ReturnType<typeof useRouter>,
  queryClient: ReturnType<typeof useQueryClient>,
) {
  const session = await getSession();
  queryClient.setQueryData(sessionQueryKey, session !== null);
  if (!session) {
    router.push("/login");
    return;
  }
  if (!session.profileComplete) {
    router.push("/setup");
    return;
  }
  router.push("/home");
}

export function useLoginMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: LogInParams) => logIn(input),
    onSuccess: () => routeAfterAuth(router, queryClient),
  });
}

export function useSignupMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: SignUpParams) => signUp(input),
    onSuccess: () => routeAfterAuth(router, queryClient),
  });
}

export function useCompleteProfileMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CompleteProfileParams) => completeProfile(input),
    onSuccess: () => {
      queryClient.setQueryData(sessionQueryKey, true);
      router.push("/home");
    },
  });
}

export function useLogoutMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => logOut(),
    onSuccess: () => {
      queryClient.setQueryData(sessionQueryKey, false);
      router.replace("/login");
    },
  });
}
