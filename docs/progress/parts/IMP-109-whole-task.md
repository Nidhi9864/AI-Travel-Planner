# IMP-109 · whole-task part

- Run id: RUN-008
- Owner: Krrish (Assassin-byte)
- Status: PR_OPEN
- Base commit: 99c7510 (rebased from db02416 after IMP-106 merged; unit, lint, type, build and e2e results below were taken on db02416 and `make check` was repeated after the rebase)
- Branch: feat/IMP-109-whole-task
- Reviewer: Manasvi (Manasvi1704)
- Traces to: US-010, US-011; FR-001, FR-002; NFR-013; TC-051 to TC-054, TC-056; E2E-01 (auth part)
- Card steps built: 1 to 6

## Changed files

- `apps/web/lib/auth/supabase.ts` (created, step 1): `getSupabase()` creates the one browser client on first use, never at import, so tests and `next build` need no values. It uses `createBrowserClient` from `@supabase/ssr` with `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` only. `supabaseConfig()` names the two variables when they are missing.
- `apps/web/lib/auth/useSession.ts` (created, step 1): returns `{status: loading | signed_in | signed_out, session, user, accessToken, signOut}` and subscribes to `onAuthStateChange`. On a `pageshow` that restores a page from the back-forward cache, it reads the stored session again (FR-002 AC3). `signOut()` runs `supabase.auth.signOut()`, then `queryClient.clear()`, then `router.replace("/sign-in")`.
- `apps/web/lib/auth/redirect.ts` (created): `safeNextPath()` accepts only a same-site path that starts with a single `/`. Anything else falls back to `/dashboard`: `//host`, `/\host`, absolute URLs, `javascript:`, control characters, and relative paths without a leading `/`.
- `apps/web/lib/validation/auth.ts` (created, §7.3): `signUpSchema` (email format, trimmed; password required and at least 8 characters) and `signInSchema` (email format; password required only). Each rule has a field-level message.
- `apps/web/app/auth/callback/route.ts` (created, step 3): `GET` exchanges `code` for a session with `createServerClient` (`@supabase/ssr`), which writes the session cookies the browser client reads. It then redirects to the safe `next` or `/dashboard`. A missing or failed code goes to `/sign-in?error=confirmation`.
- `apps/web/app/(public)/sign-up/page.tsx` and `apps/web/app/(public)/sign-in/page.tsx` (created, steps 2 and 3): thin server pages (§7.1). The public AppShell is static; the form reads `next` (and `error` on sign-in) from the query string and streams in behind `<Suspense>`, because `cacheComponents` is on.
- `apps/web/components/auth/SignUpForm.tsx`, `SignInForm.tsx`, `PasswordInput.tsx`, `AuthCard.tsx`, `messages.ts` (created; the client components the pages render):
  - Both forms use react-hook-form with `zodResolver`. Each input has a label, and each error is tied to its field with `aria-describedby` and `aria-invalid`.
  - The show or hide toggle is a real 44 px button with `aria-pressed`.
  - While a form submits, its inputs are disabled and the button shows a spinner (`motion-safe` only).
  - After sign-up, the same neutral `role="status"` notice appears both when no session starts and when Supabase reports an existing account (`user_already_exists` / `email_exists`). When the project skips confirmation, sign-up continues signed in.
  - `weak_password` from Supabase is shown on the password field.
  - Rate limiting (HTTP 429 or the `over_*_rate_limit` codes) shows "Too many attempts. Try again later."
  - Every other sign-in failure shows only "Email or password is incorrect." A network failure shows a connection message.
  - A user who is already signed in and opens `/sign-in` is sent to `/dashboard`. The session is checked once on arrival, so the check does not race the redirect to `next`.
- `apps/web/components/shell/AuthGuard.tsx` (created, step 4):
  - While the session loads, it shows `LoadingSkeleton`. When signed out, it calls `router.replace("/sign-in?next=<path and query>")`. When signed in, it renders the page inside an `AuthContext`, read with `useAuth()`, that holds the user and `signOut`. Nothing private renders before the session is known or after it ends.
  - A sign-out started from the menu does not add `next` back to the private page.
- `apps/web/app/(app)/layout.tsx` (modified, Manasvi's file, step 4): the wrap only, `<AuthGuard><AppShell>{children}</AppShell></AuthGuard>`, and its comment. **Reason:** card step 4 puts AuthGuard in this layout. It wraps AppShell, so the shell's account menu sits inside the guard's context.
- `apps/web/components/shell/AppShell.tsx` (modified, Manasvi's file, `AccountMenu` only): inside AuthGuard, the menu label shows the user's email and a "Sign out" item calls `useAuth().signOut()`. On public pages, `useAuth()` is null and the menu is unchanged. **Reason:** sign-out needs a control (FR-002 AC3, step 4), and IMP-104 left this placeholder for the purpose ("IMP-109 adds the signed-in user and sign-out"). The run prompt lists only `layout.tsx` as a change to Manasvi's files, so this edit is flagged here and in the pull request for the reviewer, who owns the file. No other line of AppShell changed, and its unit tests pass unchanged.
- `apps/web/e2e/fixtures/users.ts` (created, step 5):
  - A Playwright `users` fixture that creates confirmed users with the local stack's admin API (`auth.admin.createUser`, `email_confirm: true`).
  - It reads `SUPABASE_SERVICE_ROLE_KEY` and `NEXT_PUBLIC_SUPABASE_URL` from the environment of the e2e run only, and refuses any host other than `127.0.0.1` or `localhost`.
  - Passwords are random per user, and addresses are unique (`e2e-<tag>-<uuid>@example.test`).
  - After each test it deletes every user it created or tracked; afterwards the local `auth.users` held 0 `e2e-%` rows.
- `apps/web/e2e/auth.spec.ts` (created, step 5): five journeys, run at each of the four project widths:
  - sign-up field errors, no request sent, keyboard toggle and 44 px target (TC-053);
  - valid sign-up, with exactly one account (TC-051);
  - duplicate email: neutral notice, still one account, nothing signed in (TC-052);
  - wrong password: generic message;
  - the full journey (TC-054, TC-056): a signed-out `/dashboard` goes to `/sign-in?next=%2Fdashboard`, sign-in lands on `/dashboard` with no horizontal scroll, reload keeps the session, `/sign-in` while signed in returns to `/dashboard`, the account menu names the user and signs out, and Back to the earlier dashboard entry ends on `/sign-in` with neither the heading nor the email present.

  The spec signs in or up at most four times per width, to stay inside the local limit of 30 per 5 minutes.
- `apps/web/tests/unit/shell/AuthGuard.test.tsx` (created, step 6, TC-054): with Supabase and the router mocked, it checks:
  - the skeleton while loading;
  - the redirect to `/sign-in?next=%2Ftrips%2Fabc%2Fitinerary%3Fday%3D2` when signed out;
  - children when signed in;
  - hiding and redirecting when the session ends in another tab;
  - sign-out calling `signOut`, clearing the query cache and replacing with `/sign-in` exactly once.
- `apps/web/tests/unit/validation/auth.test.ts`, `apps/web/tests/unit/auth/redirect.test.ts`, `apps/web/tests/unit/auth/AuthForms.test.tsx` (created): the schema rules and messages; 15 `safeNextPath` cases; the forms (errors tied to fields, weak password, signed-in continuation with `emailRedirectTo`, an identical notice for a new and an existing address, "Try again later", keyboard toggle, generic sign-in error, signed-in redirect from `/sign-in`, confirmation-link error).
- `apps/web/package.json`, `apps/web/package-lock.json` (modified): `@supabase/supabase-js` 2.118.0, `@supabase/ssr` 0.12.7, `react-hook-form` 7.91.0, `zod` 4.6.7, `@hookform/resolvers` 7.0.0. No new advisory: `npm audit` reports the same 21 low and moderate findings as `main`, and none is critical.
- `docs/progress/parts/IMP-109-whole-task-signup-errors-360.png` (created): sign-up field errors at 360 px.
- This record (created).

## Screenshot

[Sign-up field errors at 360 px](IMP-109-whole-task-signup-errors-360.png). It shows the email error, the password error under its hint, and the focused show or hide toggle; there is no horizontal scroll. It was taken by `auth.spec.ts` with `UPDATE_SCREENSHOTS=1`.

## Commands run

Local keys: `make stack-up`, then `API_URL`, `ANON_KEY` and `SERVICE_ROLE_KEY` from `supabase status -o env` were exported in a subshell as `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` for the e2e command only. No key was printed or written to a file. `apps/web/.env.local` does not exist, and neither it nor `apps/api/.env` was read.

| Command | Result line (quoted exactly) |
| --- | --- |
| `make test-web ARGS='AuthGuard'` (no `NEXT_PUBLIC_*` set) | `      Tests  5 passed (5)` |
| `make stack-up` | `Starting database from backup...`, exit 0 |
| `make e2e ARGS='auth'` (first run) | `  12 passed (28.5s)` with 8 failed. Two locators also matched Next.js's own `role="alert"` route announcer, and the sign-in and sign-up pages read `searchParams` outside Suspense; both fixed |
| `make e2e ARGS='auth'` (second run) | `  20 passed (21.6s)` |
| `UPDATE_SCREENSHOTS=1 make e2e ARGS='auth'` (final run, with the signed-in dashboard width check) | `  20 passed (19.0s)` |
| `make e2e ARGS='smoke'` (IMP-104's spec, to measure the impact) | `/` 4 passed; `/dashboard` 4 failed (`getByRole('heading', { name: /your trips/i, level: 1 })` not found; signed-out visitors now go to `/sign-in`; fixed in RUN-008b) |
| `make lint` | `All matched files use Prettier code style!` |
| `make typecheck` | `✓ Types generated successfully` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | `      Tests  48 passed (48)`; last line `   Duration  4.23s (environment 64%, setup 14%, tests 13%, import 7%, transform 2%)` |
| `make check` | exit 0; last line `   Duration  3.71s (environment 57%, tests 18%, setup 12%, import 10%, transform 3%, worker 1%)` |
| `make db-up`, then `make check` after the rebase on 99c7510 (main now has the IMP-106 database tests) | exit 0; test-api `======================== 44 passed, 1 warning in 2.08s =========================`, test-authz `1 passed`, test-web `      Tests  48 passed (48)`; last line `   Duration  4.35s (environment 65%, tests 13%, setup 13%, import 7%, transform 2%)` |
| `npm run build --prefix apps/web` (no `NEXT_PUBLIC_*` set) | exit 0; `/` ○, `/dashboard` ○, `/sign-in` ◐, `/sign-up` ◐, `/auth/callback` ƒ; last line `ƒ  (Dynamic)            server-rendered on demand` |
| `grep` for `SERVICE_ROLE`, `service_role` or `SUPABASE_SERVICE` in `apps/web/.next/static/chunks/*.js` | `no service-role reference in any browser chunk` |
| `psql` on the local stack: `select count(*) from auth.users where email like 'e2e-%@example.test'` after the runs | `0` |
| `make stack-down` | see the SYNC REPORT (run after this record was committed) |

## Not run

| Command | Reason |
| --- | --- |
| axe scan (`@axe-core/playwright`) of `/sign-in` and `/sign-up` | §7.9 runs it in the E2E suite, but the dependency is not part of this card (narrowing note a); see Open issues. Labels, field errors, the keyboard toggle, 44 px targets and 360 px width are checked by the specs above. |
| Sign-up with email confirmation on | The local stack has `enable_confirmations = false`. The confirmation path (neutral notice and the `/auth/callback` code exchange) is covered by unit tests and by the TC-051 assertion, which accepts either outcome; not run end to end. |

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| Valid sign-up creates an account and signs in or asks for confirmation (FR-001 AC1, TC-051) | verified | e2e TC-051 at 4 widths: the dashboard opens and the admin API counts exactly 1 account; unit tests for both outcomes |
| Duplicate email shows a neutral message and no second account (FR-001 AC2, TC-052); weak or empty password rejected per field (FR-001 AC3, TC-053) | verified | e2e TC-052: the notice equals the new-account notice, no alert, 1 account, not signed in. e2e TC-053: per-field errors and no sign-up request. Schema and form unit tests |
| Valid credentials open /dashboard (FR-002 AC1, TC-054); after sign-out, Back shows no private data (FR-002 AC3, TC-056) | verified | e2e journey at 4 widths; the AuthGuard unit test for sign-out (cache cleared, history replaced) |
| Visiting an (app) route signed out redirects to /sign-in (unit test) | verified | `make test-web ARGS='AuthGuard'`: 5 passed (redirect with `next`); also e2e `/dashboard` → `/sign-in?next=%2Fdashboard` |
| e2e auth.spec.ts passes against the local stack (E2E-01 part) | verified | `make e2e ARGS='auth'`: `  20 passed (19.0s)` |

## Blockers

None for this part.

## Proposed decisions

- **PD-IMP-109-1 (smoke spec) — resolved in this pull request (RUN-008b, see below):** `e2e/smoke.spec.ts` (IMP-104, Manasvi) checks `/dashboard` signed out, and AuthGuard now redirects that visit to `/sign-in`, so the `/dashboard` entry fails at all four widths. Proposed fix, by the file's owner or with their agreement: sign in with the `users` fixture of `e2e/fixtures/users.ts` before visiting `/dashboard`. The auth journey here already checks the signed-in dashboard for horizontal scroll at each width. CI does not run e2e, so no required check is affected.
- **PD-IMP-109-2 (instant-navigation validation):** with `cacheComponents`, `next dev` logs `Route "/dashboard": Could not validate that a segment in your UI has instant navigation` (development only; the build is unaffected). AuthGuard renders (app) pages only after reading the browser session, as §7.1 and §7.2 require, so Next.js cannot prerender those pages to validate them. A layout-level `export const instant = false` does not silence it; validation is per page. Options: `export const instant = false` in each (app) page, or `experimental.instantInsights.validationLevel: 'manual-warning'` in `next.config.ts`. Both files belong to other members, so neither was changed.

## RUN-008b: smoke spec fix (PD-IMP-109-1)

- Run id: RUN-008b (fix of RUN-008, same pull request #194)
- Owner: Krrish (Assassin-byte)
- Status: PR_OPEN
- Base commit: 99c7510 (unchanged; `main` had not moved)

**Changed file:** `apps/web/e2e/smoke.spec.ts` (modified, Manasvi's file from IMP-104). **Reason:** this card's AuthGuard made the spec's signed-out visit to `/dashboard` fail.
- The existing checks moved, unchanged, into one helper, `expectFitsViewport`, which runs for both pages at all four widths: the level-1 heading is visible, `document.documentElement.scrollWidth <= innerWidth`, and the clipped-control check (no control outside the viewport and none whose content overflows it). None was removed, skipped or loosened.
- The screenshot branch is unchanged. `UPDATE_SCREENSHOTS` was unset in every run, and `md5sum -c` confirmed that `IMP-104-whole-task-360.png` and `IMP-104-whole-task-1280.png` are unchanged.
- `/dashboard` first creates a confirmed user with `e2e/fixtures/users.ts` and signs in through `/sign-in?next=%2Fdashboard`. The user is deleted after the test, and the local `auth.users` held 0 `e2e-%` rows after the runs.
- New check: `smoke: a signed-out visit to /dashboard lands on /sign-in`, which asserts the URL `/sign-in?next=%2Fdashboard` and the "Sign in" heading.
- The `/` check still needs no Supabase values. It passed with none set.

| Command | Result line (quoted exactly) |
| --- | --- |
| `make stack-up` | exit 0 (keys passed to the e2e commands as environment variables from `supabase status -o env`, as in RUN-008; none printed or written) |
| `make e2e ARGS='smoke'` | `  12 passed (14.3s)` (`/` ×4, `/dashboard` signed in ×4, signed-out redirect ×4) |
| `make e2e ARGS='smoke -g "smoke: / fits"'` with no `NEXT_PUBLIC_*` or service-role value set | `  4 passed (5.6s)` |
| `make e2e ARGS='auth'` | `  20 passed (23.0s)` |
| `make test-web` | `      Tests  48 passed (48)` |
| `make lint` | `All matched files use Prettier code style!` |
| `make typecheck` | `✓ Types generated successfully` |
| `make db-up`, then `make check` | exit 0; test-api `======================== 44 passed, 1 warning in 2.48s =========================`, test-authz `1 passed`, test-web `      Tests  48 passed (48)`; last line `   Duration  4.15s (environment 61%, tests 16%, setup 12%, import 8%, transform 3%)` |
| `make stack-down` | see the SYNC REPORT (run after this record was committed) |

## Open issues

- **API-03 in AuthGuard:** §7.2 says AuthGuard loads `['me']` (API-03) once. API-03 does not exist yet, so this card does not call it (narrowing note e); a comment marks the place in `AuthGuard.tsx`. The card that delivers API-03 (IMP-601) adds the query, and `CurrentUser` then creates the profile on that first call (IMD-14).
- **AppShell account menu:** changed outside the prompt's file list; see Changed files. The reviewer owns the file.
- **Email confirmation is off on the local stack.** A new address is signed in at once there, while an existing address gets the neutral notice. With confirmation on (planned for hosted projects, IMP-113), both cases show the same notice. Enumeration resistance therefore depends on that hosted setting, which this record flags for IMP-113.
- **axe:** add `@axe-core/playwright` scans of `/sign-in` and `/sign-up` when the E2E accessibility card adds the dependency.
- **Local rate limit:** the local stack allows 30 sign-ins and sign-ups per 5 minutes per IP (`supabase/config.toml`). A full auth run uses 16, so two runs within 5 minutes can hit "Try again later". Wait between runs or raise the local limit (IMP-105's file).
