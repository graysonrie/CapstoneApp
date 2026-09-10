"use client";

import { useState } from "react";
import AnimatedButton from "@/components/generic/AnimatedButton";
import PointGridBg from "@/components/PointGridBg";
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
import {
  confirmPasswordReset,
  requestPasswordReset,
} from "@/generated";
import { getErrorMessage } from "@/lib/error";
import { TRANSITION1 } from "@/types/motionConstants";
import { KeyRound, Lock, Mail } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

type Step = "request" | "confirm";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const requestMutation = useMutation({
    mutationFn: () => requestPasswordReset({ email }),
    onSuccess: (returnedCode) => {
      setDevCode(returnedCode);
      setFormError(null);
      setStep("confirm");
    },
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      confirmPasswordReset({
        email,
        code,
        newPassword,
      }),
    onSuccess: () => {
      router.replace("/login");
    },
  });

  function handleRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    requestMutation.mutate();
  }

  function handleConfirm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (newPassword !== confirmPassword) {
      setFormError("Passwords do not match");
      return;
    }
    if (newPassword.length < 8) {
      setFormError("Password must be at least 8 characters");
      return;
    }
    setFormError(null);
    confirmMutation.mutate();
  }

  return (
    <main className="relative mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-8 px-8">
      <PointGridBg />
      <motion.div
        className="relative z-10 flex flex-col gap-6"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={TRANSITION1}
      >
        <div className="flex w-full flex-col items-center gap-2 py-4 text-center">
          <h1 className="font-brand text-6xl">
            {step === "request" ? "Reset password" : "Enter code"}
          </h1>
          <p className="text-muted-foreground">
            {step === "request"
              ? "We'll send a reset code to your email."
              : "Enter the code from your email and choose a new password."}
          </p>
        </div>

        {step === "request" ? (
          <form onSubmit={handleRequest} className="flex flex-col gap-6">
            <FieldGroup className="gap-5">
              <Field>
                <FieldLabel htmlFor="reset-email" className="text-md">
                  Email
                </FieldLabel>
                <InputGroup className="h-15">
                  <InputGroupAddon>
                    <Mail aria-hidden className="size-5" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="reset-email"
                    type="email"
                    autoComplete="email"
                    placeholder="your_email@example.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                    className="text-lg"
                  />
                </InputGroup>
              </Field>
            </FieldGroup>

            {requestMutation.isError ? (
              <FieldError>{getErrorMessage(requestMutation.error)}</FieldError>
            ) : null}

            <AnimatedButton
              type="submit"
              size="lg"
              className="w-full"
              disabled={requestMutation.isPending}
            >
              {requestMutation.isPending ? "Sending…" : "Send reset code"}
            </AnimatedButton>
          </form>
        ) : (
          <form onSubmit={handleConfirm} className="flex flex-col gap-6">
            {devCode ? (
              <p className="rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
                Dev code: <span className="font-mono font-medium">{devCode}</span>
              </p>
            ) : null}

            <FieldGroup className="gap-5">
              <Field>
                <FieldLabel htmlFor="reset-code" className="text-md">
                  Reset code
                </FieldLabel>
                <InputGroup className="h-15">
                  <InputGroupAddon>
                    <KeyRound aria-hidden className="size-5" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="reset-code"
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    placeholder="6-digit code"
                    value={code}
                    onChange={(event) => setCode(event.target.value)}
                    required
                    className="text-lg"
                  />
                </InputGroup>
              </Field>

              <Field>
                <FieldLabel htmlFor="reset-new-password" className="text-md">
                  New password
                </FieldLabel>
                <InputGroup className="h-15">
                  <InputGroupAddon>
                    <Lock aria-hidden className="size-5" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="reset-new-password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="Minimum 8 characters"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    required
                    className="text-lg"
                  />
                </InputGroup>
              </Field>

              <Field>
                <FieldLabel htmlFor="reset-confirm-password" className="text-md">
                  Confirm password
                </FieldLabel>
                <InputGroup className="h-15">
                  <InputGroupAddon>
                    <Lock aria-hidden className="size-5" />
                  </InputGroupAddon>
                  <InputGroupInput
                    id="reset-confirm-password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="Re-enter password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    required
                    className="text-lg"
                  />
                </InputGroup>
              </Field>
            </FieldGroup>

            {formError ? <FieldError>{formError}</FieldError> : null}
            {confirmMutation.isError ? (
              <FieldError>{getErrorMessage(confirmMutation.error)}</FieldError>
            ) : null}

            <AnimatedButton
              type="submit"
              size="lg"
              className="w-full"
              disabled={confirmMutation.isPending}
            >
              {confirmMutation.isPending ? "Resetting…" : "Reset password"}
            </AnimatedButton>
          </form>
        )}

        <div className="flex flex-col items-center">
          <Link href="/login" className="font-bold text-primary hover:underline">
            Back to log in
          </Link>
        </div>
      </motion.div>
    </main>
  );
}
