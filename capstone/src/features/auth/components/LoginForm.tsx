"use client";

import { Lock, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { MIN_PASSWORD_LENGTH } from "@/features/auth/api/auth";
import { useLoginMutation } from "@/features/auth/hooks/useAuthMutations";
import { useAuthFormStore } from "../store/useAuthFormStore";

export default function LoginForm() {
  const { password, email, setValues } = useAuthFormStore();
  const loginMutation = useLoginMutation();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    loginMutation.mutate({ email, password });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <FieldGroup className="gap-5">
        <Field>
          <FieldLabel htmlFor="login-email" className="text-md px-4">
            Email
          </FieldLabel>
          <InputGroup className="h-15">
            <InputGroupAddon>
              <Mail aria-hidden className="size-5" />
            </InputGroupAddon>
            <InputGroupInput
              id="login-email"
              type="email"
              autoComplete="email"
              placeholder="your_email@example.com"
              value={email}
              onChange={(event) => setValues({ email: event.target.value })}
              required
              className="text-lg"
            />
          </InputGroup>
        </Field>
        <Field>
          <FieldLabel htmlFor="login-password" className="text-md px-4">
            Password
          </FieldLabel>
          <InputGroup className="h-15">
            <InputGroupAddon>
              <Lock aria-hidden className="size-5" />
            </InputGroupAddon>
            <InputGroupInput
              id="login-password"
              type="password"
              autoComplete="current-password"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(event) => setValues({ password: event.target.value })}
              required
              minLength={MIN_PASSWORD_LENGTH}
              className="text-lg"
            />
          </InputGroup>
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
        className="w-full "
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}
