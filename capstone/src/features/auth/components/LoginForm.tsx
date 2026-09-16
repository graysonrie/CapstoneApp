"use client";

import { Lock, Mail } from "lucide-react";
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
import { getErrorMessage } from "@/lib/error";
import { useAuthFormStore } from "../store/useAuthFormStore";
import { motion } from "motion/react";
import AnimatedButton from "@/components/generic/AnimatedButton";
import { TRANSITION1 } from "@/types/motionConstants";

export default function LoginForm() {
  const { password, email, setValues } = useAuthFormStore();
  const loginMutation = useLoginMutation();

  function handleSubmit(event: React.ChangeEvent<HTMLFormElement>) {
    event.preventDefault();
    loginMutation.mutate({ email, password });
  }

  return (
    <motion.div
      initial={{ scale: 0.8 }}
      animate={{ scale: 1 }}
      transition={TRANSITION1}
      className="pt-4"
    >
      <div className="flex w-full py-8">
        <h1 className="font-semibold text-3xl font-brand pl-3">Log In</h1>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-10">
        <FieldGroup className="gap-10">
          <Field>
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
                className="text-lg "
              />
            </InputGroup>
          </Field>
          <Field>
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
          <FieldError>{getErrorMessage(loginMutation.error)}</FieldError>
        ) : null}

        <AnimatedButton
          type="submit"
          size="lg"
          className="w-full"
          disabled={loginMutation.isPending}
        >
          {loginMutation.isPending ? "Logging in…" : "Log In"}
        </AnimatedButton>
      </form>
    </motion.div>
  );
}
