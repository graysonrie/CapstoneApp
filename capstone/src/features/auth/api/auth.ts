import type { User as SupabaseUser } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase/client";
import type { LoginInput, SignupInput, User } from "@/features/auth/types";

export const MIN_PASSWORD_LENGTH = 8;

export function toUser(supabaseUser: SupabaseUser): User {
  const email = supabaseUser.email ?? "";
  const metadataName = supabaseUser.user_metadata?.name;
  const name =
    typeof metadataName === "string" && metadataName.trim()
      ? metadataName.trim()
      : email.split("@")[0] || "Plant Lover";

  return {
    id: supabaseUser.id,
    email,
    name,
  };
}

function validateEmailAndPassword(email: string, password: string) {
  if (!email.trim()) {
    throw new Error("Email is required");
  }
  if (!password) {
    throw new Error("Password is required");
  }
  if (password.length < MIN_PASSWORD_LENGTH) {
    throw new Error("Password must be at least 8 characters");
  }
}

export async function login(input: LoginInput): Promise<User> {
  validateEmailAndPassword(input.email, input.password);

  const { data, error } = await getSupabase().auth.signInWithPassword({
    email: input.email.trim(),
    password: input.password,
  });

  if (error) {
    throw new Error(error.message);
  }
  if (!data.user) {
    throw new Error("Login failed");
  }

  return toUser(data.user);
}

export async function signup(input: SignupInput): Promise<User> {
  if (!input.name.trim()) {
    throw new Error("Name is required");
  }
  validateEmailAndPassword(input.email, input.password);

  const { data, error } = await getSupabase().auth.signUp({
    email: input.email.trim(),
    password: input.password,
    options: {
      data: { name: input.name.trim() },
    },
  });

  if (error) {
    throw new Error(error.message);
  }
  if (!data.user) {
    throw new Error("Sign up failed");
  }
  if (!data.session) {
    throw new Error(
      "Check your email to confirm your account before signing in",
    );
  }

  return toUser(data.user);
}
