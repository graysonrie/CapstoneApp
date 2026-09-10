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
  InputGroupInput,
} from "@/components/ui/input-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { USAGE_INTENT_OPTIONS } from "@/features/auth/constants";
import { useCompleteProfileMutation } from "@/features/auth/hooks/useAuthMutations";
import { getErrorMessage } from "@/lib/error";
import { TRANSITION1 } from "@/types/motionConstants";
import { motion } from "motion/react";

export default function SetupPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [usageIntent, setUsageIntent] = useState("");
  const completeProfileMutation = useCompleteProfileMutation();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!usageIntent) return;
    completeProfileMutation.mutate({
      firstName,
      lastName,
      usageIntent,
    });
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
          <h1 className="font-brand text-6xl">Almost there</h1>
          <p className="text-muted-foreground">
            Tell us a bit about yourself to get started.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <FieldGroup className="gap-5">
            <Field>
              <FieldLabel htmlFor="setup-first-name" className="text-md">
                First name
              </FieldLabel>
              <InputGroup className="h-15">
                <InputGroupInput
                  id="setup-first-name"
                  type="text"
                  autoComplete="given-name"
                  placeholder="First name"
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                  required
                  className="text-lg"
                />
              </InputGroup>
            </Field>

            <Field>
              <FieldLabel htmlFor="setup-last-name" className="text-md">
                Last name
              </FieldLabel>
              <InputGroup className="h-15">
                <InputGroupInput
                  id="setup-last-name"
                  type="text"
                  autoComplete="family-name"
                  placeholder="Last name"
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                  required
                  className="text-lg"
                />
              </InputGroup>
            </Field>

            <Field>
              <FieldLabel htmlFor="setup-usage-intent" className="text-md">
                How do you plan on using this app?
              </FieldLabel>
              <Select value={usageIntent} onValueChange={setUsageIntent}>
                <SelectTrigger id="setup-usage-intent" className="h-15 w-full text-lg">
                  <SelectValue placeholder="Select an option" />
                </SelectTrigger>
                <SelectContent>
                  {USAGE_INTENT_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option} className="text-lg">
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
          </FieldGroup>

          {completeProfileMutation.isError ? (
            <FieldError>
              {getErrorMessage(completeProfileMutation.error)}
            </FieldError>
          ) : null}

          <AnimatedButton
            type="submit"
            size="lg"
            className="w-full"
            disabled={completeProfileMutation.isPending || !usageIntent}
          >
            {completeProfileMutation.isPending ? "Saving…" : "Get Started"}
          </AnimatedButton>
        </form>
      </motion.div>
    </main>
  );
}
