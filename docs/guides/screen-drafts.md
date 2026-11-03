# Screen drafts

How a screen part may use a visual draft as a reference, and how the draft is moved into `apps/web` (IMD-117, which replaces IMD-64).

## Purpose

A draft shows what a screen should look like and how it is laid out. It decides nothing else. Behaviour, data, labels, loading, empty and error states, and accessibility come from the task card and specification §7 (§7.5 for each screen, §7.6 for the shared components). When the draft and the card disagree, the card wins.

A draft is optional. A screen run can go ahead without one.

## Who does what

- **The planner** may write a draft prompt for a screen part from §7 and the card.
- **The screen part's owner** builds the draft. Manasvi, as web lead, can build it if the owner asks.
- **The operator** keeps the exported draft outside the repository and gives it to the screen part's run.
- **The screen part's run** moves the look and layout into `apps/web` and writes the card's tests.

## Rules for the Lovable project

Drafts are built in Lovable. The Lovable project:

- is never connected to `het-lathiya/Group12`: no GitHub sync to this repository;
- has no Supabase or other backend connection;
- holds no keys, tokens or real personal data;
- uses SAMPLE data only, with the synthetic destination "Sampleton" and place names that end in "(sample)".

## Hand-off

1. Export the draft's code in one of two ways:
   - use Lovable's GitHub export to a separate repository that you (the drafter) own, then use Download ZIP on that repository; or
   - download the code from Lovable directly.
2. Send the zip to the operator.
3. The operator unzips it outside the repository, at `~/ui_drafts/IMP-NNN/` (the card's ID).

## Porting rules for the screen run

- Copy the JSX structure and the Tailwind classes into the files the card lists.
- Use what the repository already has instead of the draft's own versions:
  - the shadcn/ui components in `apps/web/components/ui/` and the shared states in `apps/web/components/states/`;
  - the generated API client and query hooks in `apps/web/lib/api/` (`client.ts`, `queries.ts`), with TanStack Query;
  - react-hook-form with zod schemas from `apps/web/lib/validation/` for forms.
- Take field names, values and enums from `apps/web/lib/api/schema.d.ts`, not from the draft.
- Throw away the draft's router, mock data, Supabase client, `package.json` and config files.
- The browser shows prices, totals, times and travel gaps exactly as the API returns them and never calculates them (CLAUDE.md §4 rule 5).
- Add no new dependency unless the pull request gives a reason for it.

## What never enters git

- the draft's zip;
- any file from the draft repository, as it was exported;
- any `.env` file.

Stage files by explicit path only, so nothing from `~/ui_drafts/` can be committed by mistake.

## Review

The reviewer checks the screen against the card and §7, not against the draft. A screen that matches the draft but misses a state, label or accessibility rule from the card is not done.

## Commits, pull requests and part records

They follow IMD-61. Every commit is authored by the screen part's owner. Commits, pull-request bodies and part records do not name the drafting tool.
