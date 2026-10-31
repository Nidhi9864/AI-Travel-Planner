# IMP-104 · whole-task part

- Run id: RUN-006
- Owner: Manasvi (Manasvi1704)
- Status: PR_OPEN
- Base commit: a4868a7
- Branch: feat/IMP-104-whole-task
- Reviewer: Krrish (Assassin-byte)
- Traces to: US-122; FR-114; NFR-026; TC-278
- Card steps built: 1 to 7

## Changed files

All paths under `apps/web/` unless stated.

- `components.json`, `lib/utils.ts` (created by `npx shadcn@latest init -b radix -p nova`, step 1).
- `components/ui/button.tsx`, `input.tsx`, `label.tsx`, `dialog.tsx`, `dropdown-menu.tsx`, `sonner.tsx`, `card.tsx`, `skeleton.tsx` (created by `npx shadcn@latest add`, step 1), then changed for the accessible defaults of step 1: buttons and inputs are 44 px high (`min-h-touch`, `size-touch`; the compact `sm`, `xs`, `icon-sm` and `icon-xs` sizes grow to 44 px on touch screens through `pointer-coarse:`), menu items are 44 px rows, the focus ring is the solid `ring` token with an offset instead of `ring/50`, the dialog overlay uses the `overlay` token instead of `bg-black/10`, the primary hover uses `primary-hover` (the generated `primary/80` fails AA), and `sonner.tsx` uses the one light theme instead of `next-themes`.
- `app/globals.css` (modified, step 2): design tokens for Tailwind v4: colours in `:root` mapped in `@theme inline`; spacing (4 px base, `--spacing-touch` 44 px), type scale and the 768 px `md` breakpoint in `@theme`; `prefers-reduced-motion` rule. The generator's dark, chart and sidebar tokens were removed (one light theme, unused).
- `app/layout.tsx` (replaced, step 4): Geist font as `--font-sans`, product metadata, `Providers`.
- `components/shell/Providers.tsx` (created, step 4): `QueryClientProvider` and the toast region. It is a separate client component because the root layout is a server component and cannot create a `QueryClient`.
- `components/shell/AppShell.tsx` (created, step 3): skip link (first focusable element), header with the app name and an account-menu placeholder (Profile link; IMP-109 adds the user and sign-out), top navigation from 768 px, bottom navigation below 768 px with Trips, Itinerary, Costs and Profile, `main` landmark; `variant="public"` for the landing page. Itinerary and Costs link to `/trips/<tripId>/itinerary` and `/costs` when the route has a `tripId`; otherwise they are shown as unavailable (`aria-disabled`, "open a trip first").
- `app/(app)/layout.tsx` (created, step 3): wraps signed-in pages in AppShell.
- `lib/api/queries.ts` (created, step 4): the query-key factory for `trips`, `trip`, `itinerary`, `costs`, `generation` (§7.4); no fetch code.
- `lib/flags.ts` (created, step 4): `isEnabled(name)` reading `NEXT_PUBLIC_FEATURES_DISABLED` (comma- or space-separated), with the nine cut-list names of IMD-11 and the nine EXT names of §4.5.
- `components/states/EmptyState.tsx`, `ErrorState.tsx`, `LoadingSkeleton.tsx` (created, step 5). ErrorState shows the message, the request ID when given and a retry button; it takes `{message, requestId}` so the `ApiError` of IMP-214 fits it.
- `app/(public)/page.tsx` (created, step 5): landing page of §7.5.1 (purpose, links to `/sign-up` and `/sign-in`, the note that plans are drafts from curated sample data with labelled estimates). No API call, no URL from the environment, no live-price or booking claim.
- `app/(app)/dashboard/page.tsx` (created): the (app) placeholder page, showing only the §7.5.3 empty state ("No trips yet", "Create a trip"). IMP-212 builds the real dashboard.
- `vitest.config.ts`, `tests/setup.ts` (created, step 6): jsdom, Testing Library matchers, `@` alias.
- `playwright.config.ts` (created, step 6): webServer `npm run dev` (skipped when `BASE_URL` is set), projects `chromium-360`, `chromium-768`, `chromium-1280`, `chromium-1920`.
- `tests/unit/shell/AppShell.test.tsx` (created, step 7): landmarks, navigation links and `aria-current`, trip-dependent links, skip link (first Tab stop; Enter moves focus to `main`; the next Tab reaches the page), public variant.
- `tests/unit/lib/flags.test.ts`, `tests/unit/states/EmptyState.test.tsx`, `ErrorState.test.tsx`, `LoadingSkeleton.test.tsx` (created; CLAUDE.md §9: tests for the new helpers and interactive components).
- `e2e/smoke.spec.ts` (created, step 7): on `/` and `/dashboard` at each project width, `document.documentElement.scrollWidth <= innerWidth` and no visible control outside the viewport or overflowing its own box.
- `package.json`, `package-lock.json` (modified): dependencies below.
- `.prettierignore` (created): Playwright's `test-results/`, `playwright-report/`, `blob-report/`. They are ignored by git in the root `.gitignore` but Prettier reads only `apps/web/.gitignore`, so `make lint` failed on `test-results/.last-run.json` after an e2e run.
- `app/page.tsx` (deleted, IMP-101 generator file): Next.js cannot have it next to `app/(public)/page.tsx`, which serves the same path `/`.
- `.gitignore` (one line added, IMP-101 generator file): `!.env.local.example`, because `.env.*` ignored the IMP-105 template (RUN-005 follow-up).
- `docs/progress/parts/IMP-104-whole-task.md` (this record), `IMP-104-whole-task-360.png`, `IMP-104-whole-task-1280.png` (created). The card asks for the screenshots in `docs/progress/sprint-1.md`; they are kept with this record (CLAUDE.md §11 item 5).

### Dependencies added

| Package | Kind | Reason |
| --- | --- | --- |
| `radix-ui` | runtime | Radix primitives behind the shadcn dialog, dropdown menu, label and slot (added by the shadcn CLI) |
| `class-variance-authority` | runtime | Button variants (shadcn CLI) |
| `cn` | runtime | Class merging in `lib/utils.ts` and the primitives; the current shadcn CLI installs this package (shadcn-ui/cn) in place of `clsx` + `tailwind-merge` |
| `lucide-react` | runtime | Icons of the primitives and the navigation (shadcn CLI) |
| `sonner` | runtime | Toast (shadcn's replacement for `toast` on the Radix base) |
| `tw-animate-css` | runtime | Open and close animations used by the primitives (shadcn CLI) |
| `@tanstack/react-query` | runtime | Query provider and cache (§7.4, step 4) |
| `shadcn` | dev | Provides `shadcn/tailwind.css` imported by `globals.css` (build time only). The CLI put it in `dependencies`; moved to `devDependencies` so the production tree stays free of its advisories |
| `vitest` (already present), `jsdom`, `@testing-library/react`, `@testing-library/dom` (its peer), `@testing-library/jest-dom`, `@testing-library/user-event` | dev | Component tests (step 6) |
| `@playwright/test` | dev | Viewport smoke spec (step 6); Chromium installed with `npx playwright install chromium` |

`next-themes`, added by `shadcn add sonner`, was removed again: the app has one light theme.

### Colour contrast (step 2)

Ratios computed from the OKLCH tokens (WCAG 2 relative luminance):

| Pair | Ratio | Needed |
| --- | --- | --- |
| foreground on background | 17.06 | 4.5 |
| primary-foreground on primary | 6.93 | 4.5 |
| secondary-foreground on secondary | 13.03 | 4.5 |
| muted-foreground on muted / on background | 6.07 / 6.72 | 4.5 |
| accent-foreground on accent | 12.31 | 4.5 |
| primary (links) on background / on accent | 7.03 / 5.83 | 4.5 |
| destructive on background / on destructive 10 % | 6.53 / 5.98 | 4.5 |
| ring on background | 7.03 | 3 |
| input border on background | 3.89 | 3 |

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `make test-web ARGS='AppShell'` (TC-278 unit) | `Tests  5 passed (5)` |
| `npm run e2e --prefix apps/web -- smoke` (TC-278 e2e, 4 widths × 2 pages) | `8 passed (6.6s)` |
| `make e2e ARGS='smoke'` | `8 passed (6.0s)` |
| `make lint` | `All matched files use Prettier code style!`; exit 0 (ruff `All checks passed!`, ESLint no output) |
| `make typecheck` | `✓ Types generated successfully`; exit 0 (mypy and `tsc --noEmit` clean) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | API unit `74 passed, 1 warning in 2.44s`; contract `no tests ran in 0.01s`; API `13 passed, 1 warning in 0.45s`; authz `no tests ran in 0.01s`; web `Tests  12 passed (12)`; exit 0 |
| `make check` | `Tests  12 passed (12)`; exit 0 (includes `openapi-check: not yet implemented (IMP-214)`) |
| `npm run build --prefix apps/web` | `○  (Static)  prerendered as static content`; routes `/`, `/_not-found`, `/dashboard` |
| `UPDATE_SCREENSHOTS=1 npm run e2e -- smoke` (in `apps/web`, screenshots) | `8 passed (11.3s)` |
| `npm audit --omit=dev` / `npm audit` (apps/web) | `found 0 vulnerabilities` / `21 vulnerabilities (2 low, 19 moderate)` (all dev-only; CI fails on critical) |
| Grep of `app`, `components`, `lib` for raw colours, URLs, `NEXT_PUBLIC_SUPABASE`/`API_BASE_URL`, `eslint-disable`, `ts-ignore`, `any` | no match |

Manual check in Chromium at 360 and 1280 px on `/dashboard`: Tab shows the skip link, Enter then Tab lands on "Create a trip" inside `main`; the bottom bar shows at 360 px and the header navigation at 1280 px.

## Not run

| Command | Reason |
| --- | --- |
| axe scan of §7.5.1 | `@axe-core/playwright` is not in this run's dependency list; the axe suite belongs to the E2E card (IMP-216) |

## Screenshots

- [Landing at 360 px](IMP-104-whole-task-360.png)
- [Landing at 1280 px](IMP-104-whole-task-1280.png)

They are rewritten only when the smoke spec runs with `UPDATE_SCREENSHOTS=1`, so routine e2e runs do not change committed files.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| At 360, 768, 1280 and 1920 px the landing page and `/dashboard` show no horizontal scroll and no clipped control (US-122 AC1-AC2, FR-114, TC-278) | verified | `e2e/smoke.spec.ts`, 8 of 8 passed (scrollWidth check and control-box check per width); screenshots |
| AppShell exposes header, nav and main landmarks and a working skip link (unit test) | verified | `tests/unit/shell/AppShell.test.tsx`, 5 of 5 passed; manual keyboard check in Chromium |
| `make test-web` and `make lint` pass; `npm run build --prefix apps/web` succeeds | verified | Commands above, exit 0 |

## Blockers

None.

## Proposed decisions

- PD-104-A (Toast): the shadcn registry no longer offers `toast` for Radix projects ("The toast component is only available for Base UI projects. Use the sonner component instead."). The §7.6 Toast is provided by sonner: the `Toaster` region from `components/ui/sonner.tsx` is mounted once in `Providers`, and pages call sonner's `toast()`. No `components/states/Toast.tsx` wrapper is created in this card; the first card that shows a toast may add one under the name Toast.
- PD-104-B (class merging): `lib/utils.ts` re-exports `cn` from the `cn` package (shadcn-ui/cn), which the current shadcn CLI installs in place of `clsx` + `tailwind-merge`.
- PD-104-C (trip-scoped navigation): the phone and desktop navigation take the trip from the route's `tripId` parameter; outside a trip, Itinerary and Costs are shown as unavailable items rather than links.
- PD-104-D (evidence screenshots): the smoke spec writes the two screenshots only with `UPDATE_SCREENSHOTS=1`.

## Open issues

- `make e2e` is no longer a stub: the IMP-101 Makefile target already runs `npx playwright test --pass-with-no-tests` once `apps/web/playwright.config.ts` exists, so `make e2e ARGS='smoke'` ran and passed here. The e2e workflow, user fixture and axe scan stay with IMP-216.
- Specification disagreement: §4.1 lists `apps/web/lib/api/` as "S1 (IMP-104 client stub)", while the run prompt assigns `lib/api/client.ts` to IMP-214. No client file was created.
- §7.5.1 "Signed-in users see 'Go to dashboard'" needs the session of IMP-109; the landing page shows the sign-up and sign-in links to everyone until then.
- The §4.3 ESLint `no-restricted-imports` area rules (Provisional) are not part of this card and were not added.
- Vitest prints a Vite notice that `vitest.config.ts` is ESM in a package without `"type": "module"`; it is a warning only and the tests run.
- Next.js 16 refuses a second `next dev` in the same folder; Playwright reuses a running server on port 3000 locally (`reuseExistingServer`), but a dev server on another port must be stopped first.
- `next/font/google` downloads Geist at build time (unchanged from the starter); an offline build would fail.
