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
import { useSignupMutation } from "@/features/auth/hooks/useAuthMutations";
import { getErrorMessage } from "@/lib/error";
import { useAuthFormStore } from "../store/useAuthFormStore";
import AnimatedButton from "@/components/generic/AnimatedButton";
import { motion } from "motion/react";
import { TRANSITION1 } from "@/types/motionConstants";

export default function SignupForm() {
  const { name, password, email, setValues } = useAuthFormStore();
  const signUpMutation = useSignupMutation();

  function handleSubmit(event: React.ChangeEvent<HTMLFormElement>) {
    event.preventDefault();
    signUpMutation.mutate({ email, password });
  }

  return (
    <motion.div
      className=""
      initial={{ scale: 0.8 }}
      animate={{ scale: 1 }}
      transition={TRANSITION1}
    >
      <div className="flex w-full justify-center py-8">
        <h1 className=" text-semibold text-7xl font-brand">Welcome</h1>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <FieldGroup className="gap-5">
          <Field>
            <FieldLabel htmlFor="login-name" className="text-md">
              Name
            </FieldLabel>
            <InputGroup className="h-15">
              <InputGroupAddon>
                <User aria-hidden className="size-5" />
              </InputGroupAddon>
              <InputGroupInput
                id="login-name"
                type="name"
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
                placeholder="your_email@example.com"
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
                placeholder="Minimum 8 characters"
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

        {signUpMutation.isError ? (
          <FieldError>{getErrorMessage(signUpMutation.error)}</FieldError>
        ) : null}

        <AnimatedButton
          type="submit"
          size="lg"
          className="w-full "
          disabled={signUpMutation.isPending}
        >
          {signUpMutation.isPending ? "Signing up…" : "Sign up"}
        </AnimatedButton>
      </form>
    </motion.div>
  );
}
