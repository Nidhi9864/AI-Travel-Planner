import createClient from "openapi-fetch";

import { getSupabase } from "@/lib/auth/supabase";
import type { components, paths } from "@/lib/api/schema";

/**
 * The typed API client (§7.1, IMD-06): openapi-fetch over the types generated from
 * contracts/openapi.v1.json. Every call carries the Supabase access token and an X-Request-ID.
 * A 401 refreshes the session once and repeats the request once; a second 401 signs out and goes
 * to /sign-in?next=<current path>. Components never call fetch directly; hooks in queries.ts use
 * `api` and `unwrap`.
 */

export type ErrorCode = components["schemas"]["ErrorCode"];
export type ErrorDetail = components["schemas"]["ErrorDetail"];
type ErrorEnvelope = components["schemas"]["ErrorEnvelope"];

/** A non-2xx answer, parsed from the §6.3 error envelope. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: ErrorCode,
    message: string,
    readonly details: ErrorDetail[],
    readonly requestId: string | null,
    readonly retryAfterS: number | null,
  ) {
    super(message);
    this.name = "ApiError";
  }

  static from(response: Response, body: unknown): ApiError {
    const envelope = (body as Partial<ErrorEnvelope> | undefined)?.error;
    if (envelope?.code) {
      return new ApiError(
        response.status,
        envelope.code,
        envelope.message,
        envelope.details ?? [],
        envelope.request_id,
        envelope.retry_after_s ?? null,
      );
    }
    // Not an envelope (a proxy or platform error page): keep the status, show a generic message.
    return new ApiError(
      response.status,
      response.status >= 500 ? "INTERNAL" : "VALIDATION_ERROR",
      "Something went wrong. Please try again.",
      [],
      response.headers.get("X-Request-ID"),
      null,
    );
  }
}

/** NEXT_PUBLIC_API_BASE_URL ends in /api/v1 (§4.5), and the contract paths already start with it. */
export function apiOrigin(
  baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL,
): string {
  if (!baseUrl) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL must be set (see .env.local.example)",
    );
  }
  return baseUrl.replace(/\/+$/, "").replace(/\/api\/v1$/, "");
}

async function accessToken(): Promise<string | null> {
  const { data } = await getSupabase().auth.getSession();
  return data.session?.access_token ?? null;
}

function send(request: Request, token: string | null): Promise<Response> {
  if (token) request.headers.set("Authorization", `Bearer ${token}`);
  if (!request.headers.has("X-Request-ID")) {
    request.headers.set("X-Request-ID", crypto.randomUUID());
  }
  return fetch(request);
}

function redirectToSignIn(): void {
  const next = `${window.location.pathname}${window.location.search}`;
  window.location.assign(`/sign-in?next=${encodeURIComponent(next)}`);
}

/** fetch with the bearer token, one silent session refresh on 401, then sign-out and redirect. */
export async function authFetch(request: Request): Promise<Response> {
  const retry = request.clone(); // the body can be read only once
  const response = await send(request, await accessToken());
  if (response.status !== 401) return response;

  const { data } = await getSupabase().auth.refreshSession();
  const token = data.session?.access_token ?? null;
  if (token) {
    const second = await send(retry, token);
    if (second.status !== 401) return second;
  }
  await getSupabase().auth.signOut({ scope: "local" });
  redirectToSignIn();
  return response;
}

let client: ReturnType<typeof createClient<paths>> | undefined;

/** The one client, created on first use (never at import, so tests and builds need no values). */
export function api(): ReturnType<typeof createClient<paths>> {
  client ??= createClient<paths>({ baseUrl: apiOrigin(), fetch: authFetch });
  return client;
}

/** The data of a 2xx answer, or an ApiError for any other. */
export function unwrap<T>(result: {
  data?: T;
  error?: unknown;
  response: Response;
}): T {
  if (!result.response.ok) throw ApiError.from(result.response, result.error);
  return result.data as T;
}
