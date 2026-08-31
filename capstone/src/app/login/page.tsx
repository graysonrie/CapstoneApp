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
    <main className="mx-auto flex w-full max-w-md flex-col gap-8 px-6 py-10">
      <header className="flex flex-col gap-2 text-center">
        <div className="flex w-full items-center justify-center gap-2 rounded-xl border border-border bg-background/80 p-2 pr-4 shadow-lg">
          <LeafIcon className="text-green-600" />
          <h1 className="font-heading text-2xl font-semibold tracking-tight">
            Prof Morris App
          </h1>
        </div>
      </header>

      <Card className="rounded-xl shadow-lg">
        <CardContent>
          <Tabs value={tab} onValueChange={setTab} className="w-full gap-6">
            <TabsList className="grid w-full grid-cols-2 rounded-2xl">
              <TabsTrigger
                value="login"
                className="rounded-xl"
                // apparently this doesn't fix the mobile issue
                onPointerDown={() => setTab("login")}
              >
                Login
              </TabsTrigger>
              <TabsTrigger
                value="signup"
                className="rounded-xl"
                onPointerDown={() => setTab("signup")}
              >
                Sign up
              </TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <LoginForm />
            </TabsContent>
            <TabsContent value="signup">
              <SignupForm />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      <RepeatingBg />
    </main>
  );
}
