import type { LoginInput, SignupInput, User } from "@/features/auth/types";

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createMockUser(email: string, name?: string): User {
  return {
    id: crypto.randomUUID(),
    email,
    name: name?.trim() || email.split("@")[0] || "Plant Lover",
  };
}

export async function login(input: LoginInput): Promise<User> {
  await delay(500);

  if (!input.email.trim() || !input.password) {
    throw new Error("Email and password are required");
  }

  return createMockUser(input.email);
}

export async function signup(input: SignupInput): Promise<User> {
  await delay(500);

  if (!input.name.trim() || !input.email.trim() || !input.password) {
    throw new Error("Name, email, and password are required");
  }

  return createMockUser(input.email, input.name);
}
