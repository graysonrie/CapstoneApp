const FALLBACK = "Something went wrong";

/**
 * Tauri `invoke` rejects with a string (or a `{ message }` object), not an
 * `Error`. TanStack Query stores that rejection as-is, so `instanceof Error`
 * is usually false.
 */
export function getErrorMessage(error: unknown, fallback = FALLBACK): string {
  if (typeof error === "string") {
    const trimmed = error.trim();
    return trimmed || fallback;
  }

  if (error instanceof Error) {
    const trimmed = error.message.trim();
    return trimmed || fallback;
  }

  if (typeof error === "object" && error !== null && "message" in error) {
    const message = error.message;
    if (typeof message === "string") {
      const trimmed = message.trim();
      return trimmed || fallback;
    }
  }

  return fallback;
}
