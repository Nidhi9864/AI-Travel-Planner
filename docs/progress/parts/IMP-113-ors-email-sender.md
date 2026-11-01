# IMP-113 · ors-email-sender part

- Run id: RUN-014
- Owner: Junaid (Junaid-Kureshi)
- Status: template ready, outcome pending (HUMAN card: Junaid obtains the key, decides the staging setting and runs the sign-up test)
- Base commit: daeb8e0
- Branch: feat/IMP-113-accounts-keys (one pull request for the card's three parts, as the run prompt asks)
- Reviewer: Manasvi (Manasvi1704)
- Traces to: US-004 (AC2); NFR-013
- Card steps prepared: templates for step 4 and for the OpenRouteService key. No decision, tier, limit, date or test result was entered, and every result field reads "TO BE FILLED BY JUNAID".

## Changed files

- `docs/decisions/accounts.md` (modified): section 2, with two parts.
  - **OpenRouteService key:** key obtained (yes/no), plan or tier as shown, the limits shown for the endpoints the routing client uses, stored in the password manager and Render settings (yes/no), and the date.
  - **Email confirmation on staging:**
    - the on or off decision and its reason;
    - the sender (the Supabase default or the optional sender of section 1);
    - the non-team sign-up test, with its date and result.

    It says to record the test only as "a non-team address", never the address itself. Under it is the note that IMP-109's no-enumeration behaviour depends on confirmation being on, and why.
- `docs/progress/parts/IMP-113-ors-email-sender.md` (this record).

No code, migration, contract or environment variable name changed.

## Commands and results

The checks ran once for the card, on the final text of all three sections. Section 2 contains only Markdown.

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| `grep -n -E '<key, token, credential URL, e-mail and URL patterns>' accounts.md secrets.md` | `secret-pattern grep: 1 matches`: the repository path `docs/progress/parts/IMP-109-whole-task.md`, which this section cites, matched the long-token pattern (a false positive) |
| The same grep with `/` removed from the long-token pattern | `secret-pattern grep (paths excluded): 0 matches` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  4.19s (environment 56%, tests 16%, setup 15%, import 9%, transform 3%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed` |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| A sign-up from a non-team address receives the confirmation e-mail, or confirmation is off and documented (US-004 AC2) | not verified | Pending Junaid: the section 2 decision and test fields are empty |
| No key value appears in the repository (secret scan green, TC-354) | not verified in this record | Shown by the CI `guards` job (gitleaks) on the pull request; the local grep found no key, token, credential URL or e-mail address |

## Outcome needed from Junaid

1. **OpenRouteService key:**
   - key obtained (yes/no);
   - the plan or tier as the account page shows it;
   - the limits shown for the endpoints the routing client uses;
   - stored in the password manager and the Render settings (yes/no);
   - the date.
2. **Staging email confirmation:** the on or off decision with its reason. If it is off, write down the enumeration consequence noted under section 2.
3. **Sender:** the Supabase default, or the optional sender. If it is the optional sender, Kirtan also fills its row in section 1.
4. **Non-team sign-up test:** the date and the result (e-mail received, and the link opened the staging web app and signed in), recorded without the address.

## Blockers

None for the templates. The outcome is blocked on the member actions above, and the sign-up test needs the staging Supabase project and the staging web app (IMP-112).

## Proposed decisions

None.

## Open issues

- **Confirmation-link redirect URLs.** For the confirmation link to reach IMP-109's `/auth/callback` route on staging, the staging Supabase Auth settings must allow the staging web URL as a redirect. This is a setup step for whoever configures the project, and the sign-up test above shows whether it works.
- **Production setting.** The card asks only for the staging decision. Whether production uses the same setting is left to IMP-801.
