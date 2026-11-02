import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const auth = {
  getSession: vi.fn(),
  refreshSession: vi.fn(),
  signOut: vi.fn(),
};
vi.mock("@/lib/auth/supabase", () => ({ getSupabase: () => ({ auth }) }));

import { ApiError, apiOrigin, authFetch } from "@/lib/api/client";

const session = (token: string | null) => ({
  data: { session: token ? { access_token: token } : null },
});

function envelope(status: number) {
  return new Response(
    JSON.stringify({
      error: {
        code: "UNAUTHENTICATED",
        message: "Please sign in again.",
        request_id: "req-1",
        details: [],
        retry_after_s: null,
      },
    }),
    { status },
  );
}

describe("apiOrigin", () => {
  it("drops the /api/v1 suffix that the contract paths already carry", () => {
    expect(apiOrigin("http://localhost:8000/api/v1")).toBe(
      "http://localhost:8000",
    );
    expect(apiOrigin("https://api.example.test/api/v1/")).toBe(
      "https://api.example.test",
    );
  });
});

describe("ApiError.from", () => {
  it("parses the error envelope", () => {
    const body = {
      error: {
        code: "STALE_PLAN",
        message: "Reload.",
        request_id: "r",
        details: [{ field: "plan_revision", message: "old" }],
        retry_after_s: null,
      },
    };
    const error = ApiError.from(new Response(null, { status: 409 }), body);
    expect(error).toMatchObject({
      status: 409,
      code: "STALE_PLAN",
      message: "Reload.",
      requestId: "r",
      details: [{ field: "plan_revision", message: "old" }],
    });
  });

  it("falls back to a generic message for a body that is not an envelope", () => {
    const error = ApiError.from(new Response(null, { status: 502 }), "<html>");
    expect(error.code).toBe("INTERNAL");
    expect(error.status).toBe(502);
  });
});

describe("authFetch", () => {
  const fetchMock = vi.fn<(request: Request) => Promise<Response>>();
  const assign = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("location", {
      pathname: "/trips/1",
      search: "?tab=costs",
      assign,
    });
    auth.getSession.mockResolvedValue(session("old"));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.resetAllMocks();
  });

  it("sends the bearer token and a request ID", async () => {
    fetchMock.mockResolvedValue(new Response("{}", { status: 200 }));
    await authFetch(new Request("http://api.test/api/v1/me"));
    const sent = fetchMock.mock.calls[0][0];
    expect(sent.headers.get("Authorization")).toBe("Bearer old");
    expect(sent.headers.get("X-Request-ID")).toMatch(/^[0-9a-f-]{36}$/);
  });

  it("refreshes once on 401 and repeats the request with the new token", async () => {
    fetchMock
      .mockResolvedValueOnce(envelope(401))
      .mockResolvedValueOnce(new Response("{}", { status: 200 }));
    auth.refreshSession.mockResolvedValue(session("new"));
    const response = await authFetch(
      new Request("http://api.test/api/v1/trips", {
        method: "POST",
        body: '{"a":1}',
      }),
    );
    expect(response.status).toBe(200);
    const retried = fetchMock.mock.calls[1][0];
    expect(retried.headers.get("Authorization")).toBe("Bearer new");
    expect(await retried.text()).toBe('{"a":1}');
    expect(assign).not.toHaveBeenCalled();
  });

  it("signs out and redirects to sign-in after a second 401", async () => {
    fetchMock.mockImplementation(async () => envelope(401));
    auth.refreshSession.mockResolvedValue(session("new"));
    const response = await authFetch(new Request("http://api.test/api/v1/me"));
    expect(response.status).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(auth.signOut).toHaveBeenCalledWith({ scope: "local" });
    expect(assign).toHaveBeenCalledWith(
      "/sign-in?next=%2Ftrips%2F1%3Ftab%3Dcosts",
    );
  });
});
