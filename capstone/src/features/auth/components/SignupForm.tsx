"use client";

import { Lock, Mail, User } from "lucide-react";
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
import { useSignupMutation } from "@/features/auth/hooks/useAuthMutations";
import { useAuthFormStore } from "../store/useAuthFormStore";

export default function SignupForm() {
  const { name, email, password, setValues } = useAuthFormStore();
  const signupMutation = useSignupMutation();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    signupMutation.mutate({ name, email, password });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <FieldGroup className="gap-5">
        <Field>
          <FieldLabel htmlFor="signup-name" className="text-md px-4">
            Name
          </FieldLabel>
          <InputGroup className="h-15">
            <InputGroupAddon>
              <User aria-hidden className="size-5" />
            </InputGroupAddon>
            <InputGroupInput
              id="signup-name"
              type="text"
              autoComplete="name"
              placeholder="Richter Belmont"
              value={name}
              onChange={(event) => setValues({ name: event.target.value })}
              required
              className="text-lg"
            />
          </InputGroup>
        </Field>
        <Field>
          <FieldLabel htmlFor="signup-email" className="text-md px-4">
            Email
          </FieldLabel>
          <InputGroup className="h-15">
            <InputGroupAddon>
              <Mail aria-hidden className="size-5" />
            </InputGroupAddon>
            <InputGroupInput
              id="signup-email"
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
          <FieldLabel htmlFor="signup-password" className="text-md px-4">
            Password
          </FieldLabel>
          <InputGroup className="h-15">
            <InputGroupAddon>
              <Lock aria-hidden className="size-5" />
            </InputGroupAddon>
            <InputGroupInput
              id="signup-password"
              type="password"
              autoComplete="new-password"
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
        disabled={signupMutation.isPending}
      >
        {signupMutation.isPending ? "Creating account…" : "Create account"}
      </Button>
    </form>
  );
}
