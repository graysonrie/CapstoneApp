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
import { useLoginMutation } from "@/features/auth/hooks/useAuthMutations";
import { useAuthFormStore } from "../store/useAuthFormStore";

export default function LoginForm() {
  const { name, password, email, setValues } = useAuthFormStore();
  const loginMutation = useLoginMutation();

  function handleSubmit(event: React.ChangeEvent<HTMLFormElement>) {
    event.preventDefault();
    loginMutation.mutate({ email, password });
  }

  return (
    <div className="">
      <div className="flex w-full justify-center py-8">
        <h1 className=" text-semibold text-7xl font-brand">Welcome</h1>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <FieldGroup className="gap-5">
          <Field>
            <FieldLabel htmlFor="login-email" className="text-md">
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
                placeholder="Email"
                value={email}
                onChange={(event) => setValues({ email: event.target.value })}
                required
                className="text-lg"
              />
            </InputGroup>
          </Field>
          <Field>
            <FieldLabel htmlFor="login-password" className="text-md">
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
                placeholder="Password"
                value={password}
                onChange={(event) =>
                  setValues({ password: event.target.value })
                }
                required
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
          {loginMutation.isPending ? "Logging in…" : "Log In"}
        </Button>
      </form>
    </div>
  );
}
