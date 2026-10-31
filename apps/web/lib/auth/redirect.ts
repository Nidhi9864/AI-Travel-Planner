/** Where a signed-in user lands when no (valid) `next` is given (§7.2). */
export const DEFAULT_AFTER_SIGN_IN = "/dashboard";

const BASE = "https://same-site.invalid";

/**
 * The `next` parameter as a same-site path, or /dashboard. Only a relative path that starts with a
 * single "/" is accepted, so `next` can never send the user to another site (no open redirect):
 * "//evil.example", "/\\evil.example", "https://…", "javascript:…" and control characters all
 * fall back to the default.
 */
export function safeNextPath(next: string | null | undefined): string {
  if (!next || !next.startsWith("/") || next.startsWith("//")) {
    return DEFAULT_AFTER_SIGN_IN;
  }
  // Browsers treat "\" like "/" and drop tabs and newlines, which would turn "/\evil" into "//evil".
  if (/[\\\u0000-\u001f\u007f]/.test(next)) {
    return DEFAULT_AFTER_SIGN_IN;
  }
  let url: URL;
  try {
    url = new URL(next, BASE);
  } catch {
    return DEFAULT_AFTER_SIGN_IN;
  }
  if (url.origin !== BASE) {
    return DEFAULT_AFTER_SIGN_IN;
  }
  return `${url.pathname}${url.search}${url.hash}`;
}
