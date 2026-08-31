"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import RepeatingBg from "@/components/RepeatingBg";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import LoginForm from "@/features/auth/components/LoginForm";
import SignupForm from "@/features/auth/components/SignupForm";
import { LeafIcon } from "lucide-react";

export default function LoginPage() {
  const [tab, setTab] = useState("login");

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col gap-8 p-8 justify-center">
      <LoginForm />
    </main>
  );
}
