"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useLoginMutation } from "@/features/auth/hooks/useAuthMutations";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const loginMutation = useLoginMutation();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    loginMutation.mutate({ email, password });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <FieldGroup className="gap-5">
        <Field>
          <FieldLabel htmlFor="login-email">Email</FieldLabel>
          <Input
            id="login-email"
            type="email"
            autoComplete="email"
            placeholder="prof_morris@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="login-password">Password</FieldLabel>
          <Input
            id="login-password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </Field>
      </FieldGroup>

      {loginMutation.isError ? (
        <FieldError>
          {loginMutation.error instanceof Error
            ? loginMutation.error.message
            : "Something went wrong"}
        </FieldError>
      ) : null}

      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}
