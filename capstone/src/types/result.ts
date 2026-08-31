export type Result<T, E> =
  | { type: "ok"; value: T }
  | { type: "err"; error: E };

export const ok = <T>(value: T): Result<T, never> => ({
  type: "ok",
  value,
});

export const err = <E>(error: E): Result<never, E> => ({
  type: "err",
  error,
});