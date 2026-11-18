"use client";

import { useAuthFormStore } from "@/features/auth/store/useAuthFormStore";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";
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
import { QueryClient, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { sessionQueryKey } from "./useIsValidSession";

function resetClientSession(queryClient: QueryClient) {
  queryClient.clear();
  useScanStore.getState().reset();
  useAuthFormStore.getState().setValues({ email: "", password: "" });
}

async function routeAfterAuth(router: ReturnType<typeof useRouter>, queryClient: QueryClient) {
  const session = await getSession();
  queryClient.setQueryData(sessionQueryKey, session);
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
    onSuccess: async () => {
      resetClientSession(queryClient);
      await routeAfterAuth(router, queryClient);
    },
  });
}

export function useSignupMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: SignUpParams) => signUp(input),
    onSuccess: async () => {
      resetClientSession(queryClient);
      await routeAfterAuth(router, queryClient);
    },
  });
}

export function useCompleteProfileMutation() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CompleteProfileParams) => completeProfile(input),
    onSuccess: async () => {
      const session = await getSession();
      queryClient.setQueryData(sessionQueryKey, session);
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
      resetClientSession(queryClient);
      router.replace("/login");
    },
  });
}
