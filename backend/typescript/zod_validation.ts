// validation.ts
// Reusable Zod schemas for API request bodies, with typed error messages
// and a safe-parse helper that returns a discriminated union result
// instead of throwing, for easy use in route handlers / middleware.

import { z, ZodSchema, ZodError } from "zod";

// --- Shared primitive schemas -------------------------------------------------

export const emailSchema = z
  .string({ required_error: "Email is required" })
  .trim()
  .email("Email must be a valid address");

export const passwordSchema = z
  .string({ required_error: "Password is required" })
  .min(8, "Password must be at least 8 characters long")
  .regex(/[0-9]/, "Password must contain at least one digit");

export const paginationSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

// --- Request body schemas ------------------------------------------------------

export const signUpRequestSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  displayName: z
    .string()
    .min(2, "Display name must be at least 2 characters")
    .max(50, "Display name must be at most 50 characters")
    .optional(),
});

export const loginRequestSchema = z.object({
  email: emailSchema,
  password: z.string({ required_error: "Password is required" }),
});

export type SignUpRequest = z.infer<typeof signUpRequestSchema>;
export type LoginRequest = z.infer<typeof loginRequestSchema>;

// --- Safe parse helper ----------------------------------------------------------

export interface ValidationFailure {
  success: false;
  errors: { path: string; message: string }[];
}

export interface ValidationSuccess<T> {
  success: true;
  data: T;
}

export type ValidationResult<T> = ValidationSuccess<T> | ValidationFailure;

// Flattens Zod's nested issue list into a flat, API-friendly error array.
function formatZodError(error: ZodError): ValidationFailure {
  return {
    success: false,
    errors: error.issues.map((issue) => ({
      path: issue.path.join("."),
      message: issue.message,
    })),
  };
}

// Parses `input` against `schema`, never throws; callers should check `.success`.
export function safeParseRequest<T>(
  schema: ZodSchema<T>,
  input: unknown
): ValidationResult<T> {
  const result = schema.safeParse(input);
  return result.success
    ? { success: true, data: result.data }
    : formatZodError(result.error);
}
