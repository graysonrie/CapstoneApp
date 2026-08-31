"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useSignupMutation } from "@/features/auth/hooks/useAuthMutations";

export default function SignupForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const signupMutation = useSignupMutation();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    signupMutation.mutate({ name, email, password });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <FieldGroup className="gap-5">
        <Field>
          <FieldLabel htmlFor="signup-name">Name</FieldLabel>
          <Input
            id="signup-name"
            type="text"
            autoComplete="name"
            placeholder="Your name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="signup-email">Email</FieldLabel>
          <Input
            id="signup-email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="signup-password">Password</FieldLabel>
          <Input
            id="signup-password"
            type="password"
            autoComplete="new-password"
            placeholder="••••••••"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </Field>
      </FieldGroup>

      {signupMutation.isError ? (
        <FieldError>
          {signupMutation.error instanceof Error
            ? signupMutation.error.message
            : "Something went wrong"}
        </FieldError>
      ) : null}

      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={signupMutation.isLoading}
      >
        {signupMutation.isLoading ? "Creating account…" : "Create account"}
      </Button>
    </form>
  );
}
