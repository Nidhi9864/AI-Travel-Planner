# FRONTEND_UI_BUILDER_ADDENDUM — AI Travel Planner

Addendum to the Implementation Specification v1.3 and `ORCHESTRATOR_PROMPT.md`, 28 October 2026. It changes **how frontend parts are produced**, not what the web app is. For frontend parts, where this addendum and the planner prompt differ, this addendum wins. Every contract of the specification (§3, §6, §7, CLAUDE.md) stays as written. To be recorded as decision **IMD-64** (section 9).

---

## 1. What changes and what stays

**Changes**

- Screens and components may first be drafted in an **AI UI builder** chosen by the operator: Lovable, v0, Bolt or similar ("the builder").
- The builder is a **design and drafting tool**. Its code never goes to the team repository directly. Claude Code ports the draft into `apps/web` in a normal run, with commits authored by the part owner (IMD-61).

**Stays the same**

- The web app stack of §7 and CLAUDE.md §2: Next.js App Router, TypeScript strict, Tailwind CSS, shadcn/ui, TanStack Query, react-hook-form + zod, openapi-fetch with the generated types, MapLibre.
- Every rule of §7:
  - The browser talks only to the API and Supabase Auth.
  - It never computes prices, totals, times or travel gaps.
  - Labels and honesty rules (§7.8).
  - Accessibility and the 360 px layout (§7.9).
  - Loading, empty and error states.
- Card IDs, parts, owners, points, tests and gates.

**Why the builder never syncs with the team repository.** Lovable cannot be connected to an existing repository: connecting creates a new repository. Since 13 May 2026 it generates TanStack Start apps (React + Vite before that), with no choice of framework and no Next.js. Its GitHub sync would also write commits that are not authored by the part owner. Treating the builder's output as a reference that Claude Code ports keeps one repository, one stack and the authorship rules. (Lovable FAQ, checked 28 Oct 2026: https://docs.lovable.dev/introduction/faq.) v0 by Vercel generates Next.js code, so its drafts port with less work. Any builder may be used under the same rules.

---

## 2. Which parts use the builder

- **Use the builder (UI-first parts):** parts that create or substantially change a **page or a visual component**, for example:
  - Manasvi's and Krrish's screen parts;
  - the screen parts of other members, such as Jeel's explore page and place detail drawer, Malhar's PlacePicker, Manal's TripActionsMenu, Het's profile page;
  - the extension screens: describe-a-trip, Today, packing, WhyThisPlacePanel, BudgetFitPanel, ForecastBanner, OptimiseDayDialog, DayExplanation, ContextCard.
- **Skip the builder (direct Claude Code runs):** parts that are wiring or infrastructure only. Examples are the web skeleton and toolchain, the auth client, the query hooks, the generated API client, the zod schemas, the E2E suites, the axe and accessibility test parts, and the keyboard-move logic without new visuals. The planner decides per part and states it in one line. The operator can override with `UI-SKIP`.

---

## 3. The flow for a UI-first part

1. **Planner:** on `NEXT` (or `UI <IMP-NNN part>`), it prints a **UI BUILDER PROMPT** with ID `UI-NNN`, using the template in section 6, plus one line on what to export.
2. **Operator or part owner:**
   - Paste the prompt into the builder and iterate visually. For corrections, ask the planner with `UI-REFINE <UI-ID> <what is wrong>`.
   - Do not connect the builder to Supabase, auth or any backend, and do not paste keys into it.
3. **Export** the draft:
   - Download it as a ZIP, or use the builder's own separate private repository. Never the team repository.
   - Copy **only the files for this screen or component** into the clone at `design/ui-builder/<IMP-NNN>-<part-slug>/`. Optionally add a screenshot `screen.png`.
   - Once per clone, add the line `design/ui-builder/` to `.git/info/exclude`. This file is local to your clone and is never committed, so the drafts stay untracked.
4. **Operator:** type `UI-READY <UI-ID> <folder>` in the planner chat.
5. **Planner:** print the **PORT RUN** prompt. This is the normal RUN template plus the UI SOURCE block of section 7, in the normal RUN-NNN numbering.
6. **From here on, as for every run:**
   - Claude Code ports, wires, tests and commits as the part owner, then opens the pull request and prints the SYNC REPORT.
   - The operator sends `REPORT`, the reviewer approves, and the PR goes through Rebase and merge.
   - The operator sends `MERGED`.

The builder step costs no extra points: it is part of the part's existing estimate.

---

## 4. Commands added to the planner

| Operator types | Planner does |
| --- | --- |
| `UI-SETUP` | Prints the one-time **builder setup prompt** (section 5) for a new builder project. Do this once before the first UI-first part. |
| `UI <IMP-NNN> <part-slug>` | Prints the UI BUILDER PROMPT for that part (section 6), with a new `UI-NNN` ID. It also happens automatically when `NEXT` picks a UI-first part. |
| `UI-REFINE <UI-ID> <what is wrong>` | Prints a short follow-up prompt for the builder that fixes only what was named, with the same constraints. |
| `UI-READY <UI-ID> <folder>` | Prints the PORT RUN prompt (section 7). |
| `UI-SKIP <UI-ID or IMP-NNN part>` | Drops the builder step and prints a normal RUN prompt for Claude Code. |

**Ledger.** A UI-first part moves through `UI_DRAFTING` (UI prompt issued) and then `UI_READY` (drafts in place). After that it follows the normal states.

---

## 5. One-time builder setup prompt (`UI-SETUP` prints this, filled in)

```text
You are drafting the user interface of "AI Travel Planner", a web app where a signed-in traveller describes a trip and gets a day-by-day itinerary that is feasible, costed and editable. This builder project is a visual draft only: another tool will port the screens into a separate Next.js codebase.

Hard constraints for every screen in this project:
- React + TypeScript, Tailwind CSS and shadcn/ui components only. lucide-react icons. No other UI kit.
- No backend of any kind: do not connect Supabase, do not add authentication, databases, edge functions, API routes or environment variables. Every screen uses typed mock data from a local file named mock-data.ts, with every value marked SAMPLE.
- Never compute prices, totals, times or travel durations in the UI: they arrive in the data and are only displayed.
- Every price, opening time and AI-written text shows its label: prices and hours as "Curated, checked on <date>" / "Estimate" / "Unavailable" (never a guessed value); travel times as "Estimated travel time from a routing service" / "Estimated travel time (distance based)"; model-written text with a small "AI-written" badge; totals always carry "Estimate". No screen says or implies that a price, opening time or route is live or verified, and no screen offers booking.
- Fixture data shows a banner "SAMPLE data, not a real destination".
- Accessibility: semantic HTML, every control reachable and operable by keyboard with a visible focus ring, labels on all inputs, colour contrast at least 4.5:1, nothing conveyed by colour alone.
- Responsive from 360 px wide phones to desktop; no horizontal scrolling at 360 px.
- Every data view has four states: loading (skeleton), empty (short message + next action), error (message + retry), and normal.

- Severity and labels use text and an icon as well as colour.

Design system: calm, trustworthy travel product. Neutral background, one primary colour (teal), one accent (amber) used only for warnings and highlights, rounded-lg cards, generous spacing, Inter font (the team may change these once, in this setup prompt only). Create a small style guide page first (colours, type scale, buttons, inputs, badges, cards, alerts) and reuse it on every screen.
```

---

## 6. UI BUILDER PROMPT template (one per UI-first part)

The planner fills every field from §7.5 (the screen), §7.6 (components), §7.8 (labels), §7.9 (accessibility) and the §6 schemas of the endpoints the screen reads. It uses only names that exist there.

```text
=== UI-<NNN> · <IMP-NNN> <card title> · part: <part-slug> · owner <Member> ===
Build (or update) this screen/component in the existing design system of this project. Visual draft only; keep every constraint of the setup prompt.

SCREEN: <route from §7.5, e.g. /trips/[tripId]/itinerary>  —  <one-line purpose>
LAYOUT: <regions in order, from §7.5 "Layout, components"; desktop and 360 px behaviour>
COMPONENTS: <names exactly as §7.6, e.g. DayColumn, ItineraryItemCard, SourceBadge, AiBadge>; put each in its own file named after the component.
DATA (mock-data.ts, SAMPLE values, field names exactly as the API returns them):
  <TypeScript interfaces copied from the §6 response schema(s) the screen reads, trimmed to the fields shown>
  <2-3 realistic SAMPLE records, including one with a missing price and one AI-written note>
INTERACTIONS: <buttons, forms, dialogs, drag and drop, keyboard alternatives; what each one would call (just a stub function named after the endpoint, e.g. onRemoveItem → API-27)>
STATES: loading · empty "<text>" · error "<text>" · <screen-specific: e.g. stale plan banner, generation in progress, feature switched off = entry point hidden>
LABELS AND COPY: <exact user-facing texts from §7 and §7.8>
ACCESSIBILITY: <screen-specific items from §7.9, e.g. move up/down buttons as the keyboard alternative to dragging>
DO NOT: add backend calls, auth, Supabase, env vars, new libraries beyond shadcn/ui, lucide-react and (only if this screen needs them) dnd-kit or a map placeholder box; do not compute any money or time.
DONE WHEN: <3-5 visual checks the operator can see, e.g. "each item card shows time, name, price with label, travel time with label">
EXPORT: the files of <component list> and mock-data.ts.
```

---

## 7. PORT RUN additions (to the normal RUN template)

The planner adds this block to the RUN prompt, after `YOUR PART`, for every part that has a `UI_READY` draft:

```text
UI SOURCE (reference only): design/ui-builder/<IMP-NNN>-<part-slug>/  (untracked; never commit, move or copy it wholesale)
PORT RULES:
  1. Rebuild the screen in apps/web following §7 and the module of §3 (MOD-F0x): App Router route under app/(app)/..., components in apps/web/components/<area>/ with the §7.6 names, shadcn/ui primitives from apps/web/components/ui.
  2. Keep the draft's layout, spacing, colours and copy where they match §7; where the draft differs from §7 (copy, labels, states, components), §7 wins. List the differences in the part record.
  3. Replace all mock data with the generated API client and the TanStack Query hooks of §7.4 (query keys and invalidation as listed). Field names come from contracts/openapi.v1.json; never hand-write response types.
  4. Remove anything the builder added that §7 forbids: Supabase database calls, auth code (the app's AuthGuard and lib/auth are used), env vars, routers other than Next.js, client-side money or time arithmetic, extra UI libraries.
  5. Add "use client" only where interaction needs it; keep data fetching through the hooks.
  6. Write the component tests listed in the card (Vitest + Testing Library), including loading, empty and error states and keyboard operation, and run make test-web, make lint, make typecheck; run make e2e ARGS='--grep <tag>' when the card names a journey.
  7. Before pushing, confirm: git ls-files design/ prints nothing; grep -R "mock-data" apps/web prints nothing outside tests.
```

**Extra checks in the planner's REPORT validation for port runs:**

- `files_changed` contains no `design/` path.
- No new dependency other than ones already in the §7 stack, unless a proposed decision says why.
- The part record lists where the screen intentionally differs from the draft.

---

## 8. Planner rules for UI-first parts

- Write UI prompts only from the specification. Never invent screens, fields, texts or endpoints. Mark every mock value as SAMPLE.
- Never put secrets, real user data, staging URLs or keys in a builder prompt.
- One UI prompt per part. A shared visual component used by several parts (for example SourceBadge or AiBadge) is drafted once, by the owner of the first part that needs it, and reused.
- For extension screens (EXT), draft only when the extension is planned in that sprint. A `CUT` extension gets no UI prompt.
- If the builder's draft cannot meet §7, for example because it needs a library outside the stack, prefer `UI-SKIP` and a direct Claude Code run over a long porting fight.
- The builder step adds no Claude Code commits. Only the PORT RUN commits, authored by the part owner.

---

## 9. One-time setup for this addendum

1. **Planner context:** add this file to the Claude Project knowledge (done if you see it there). Append this line to the project instructions, after the planner prompt:
   `Frontend parts: follow FRONTEND_UI_BUILDER_ADDENDUM.md; it adds the UI builder step and the commands UI-SETUP, UI, UI-REFINE, UI-READY and UI-SKIP.`
2. **Repository:** copy this file into `Group12/docs/spec/` with the other documents. The planner adds it to the IMP-101 file list, so it is committed unchanged with the document set.
3. **Local ignore:** add the line `design/ui-builder/` to `Group12/.git/info/exclude`.
4. **Decision:** after IMP-101 merges, the planner issues a short decision run (owner Manasvi, reviewer Kirtan) that adds IMD-64 to `docs/spec/DECISION_REGISTER.md`. Text: "Frontend screens may be drafted in an AI UI builder as untracked references and are ported into apps/web by Claude Code under §7; builder code is never synced to or committed in the repository; part owners author the port commits (IMD-61)." Status: Confirmed, team decision of 28 October 2026.
