# IMP-113 · accounts-secrets-register part

- Run id: RUN-014
- Owner: Kirtan (kirtan-S111), card lead
- Status: template ready, outcome pending (HUMAN card: Kirtan creates the accounts, holds the keys and records the facts)
- Base commit: daeb8e0
- Branch: feat/IMP-113-accounts-keys (one pull request for the card's three parts, as the run prompt asks)
- Reviewer: Manasvi (Manasvi1704)
- Traces to: US-004; NFR-013, NFR-037; OD-06, OD-15
- Card steps prepared: templates for steps 1 and 2 (step 5 allows the template only). No account fact, member, login, key or date was entered, and every result field reads "TO BE FILLED BY KIRTAN".

## Changed files

- `docs/decisions/accounts.md` (created). This part writes the header, the no-values rule and section 1:
  - **Accounts table:** one row per account (the GitHub repository, Vercel, Render, Supabase staging, Supabase production per OD-15, Google AI Studio, OpenRouteService and the optional email sender). Columns: purpose, owner role, owner member, team-owned login (yes/no), password-manager entry (yes/no), created on.
  - **GitHub access note:** only the repository owner (het-lathiya) can approve the Render and Vercel GitHub access to `het-lathiya/Group12`.
  - **Supabase projects table:** OD-15 (one or two projects, and whether the plan allows two active projects), OD-06 (hosted token verification mode; the OD-06 owner is Het) and the date the secrets register was checked against the stores.
- `docs/secrets.md` (modified):
  - an "Owner member" column on every register row, "TO BE FILLED BY KIRTAN";
  - the missing `SUPABASE_URL` row (§4.5 lists it with the secret Supabase variables);
  - a note that `GEMINI_MODEL_ID` is not secret and is recorded in accounts.md section 3, and that IMP-112 adds rows for the deploy workflows' own GitHub Actions secrets;
  - the opening paragraph now points to accounts.md.

  The owner roles, stores and rotation rules of IMP-105 are unchanged, and no value was added.
- `docs/progress/parts/IMP-113-accounts-secrets-register.md` (this record).

No code, migration, contract or environment variable name changed.

## Secret variables of §4.5 in the register

| Variable (§4.5 secret groups) | Row in `docs/secrets.md` |
| --- | --- |
| `DATABASE_URL`, `TEST_DATABASE_URL` | present (IMP-105) |
| `SUPABASE_URL` | added here |
| `SUPABASE_JWKS_URL`, `SUPABASE_JWT_SECRET` | present (IMP-105) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | present (IMP-105; public by design) |
| `ORS_API_KEY` | present (IMP-105) |
| `GEMINI_API_KEY` | present (IMP-105) |
| `FINETUNED_API_KEY` | present (IMP-105; empty in Stage 1) |
| `SUPABASE_SERVICE_ROLE_KEY` | present (IMP-105; local only) |

## Commands and results

The secret-pattern grep ran on the final versions of `docs/decisions/accounts.md` (all three sections) and `docs/secrets.md`. It looked for:

- Google, OpenAI-style and GitHub key prefixes;
- JWTs;
- long tokens of 32 or more characters;
- URLs with credentials, any `http(s)://` URL, and e-mail addresses.

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| `grep -n -E '<key, token, credential URL, e-mail and URL patterns>' accounts.md secrets.md` | `secret-pattern grep: 1 matches`: the repository path `docs/progress/parts/IMP-109-whole-task.md` matched the long-token pattern (a false positive) |
| The same grep with `/` removed from the long-token pattern | `secret-pattern grep (paths excluded): 0 matches` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  4.19s (environment 56%, tests 16%, setup 15%, import 9%, transform 3%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed` |

gitleaks is not installed locally; the CI `guards` job runs it on the pull request.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Each account has a named owner and a password-manager entry by the end of week 1 (US-004 AC1) | not verified | Pending Kirtan: the section 1 owner member, login and password-manager columns are empty |
| No key value appears in the repository (secret scan green, TC-354) | not verified in this record | Shown by the CI `guards` job (gitleaks) on the pull request; the local grep above found no key, token, credential URL or e-mail address |

## Outcome needed from Kirtan

1. **Accounts:** for each of the eight accounts in section 1 of `docs/decisions/accounts.md`, record:
   - the owner member;
   - team-owned login (yes/no);
   - password-manager entry (yes/no);
   - the created-on date (or "not created" for the optional email sender, and for the production project if OD-15 ends with one project).
2. **GitHub access:** ask het-lathiya to approve the Render and Vercel GitHub access to `het-lathiya/Group12`.
3. **OD-15:** one or two Supabase projects, and whether the plan in use allows two active projects, with the date checked.
4. **OD-06:** the hosted token verification mode (JWKS or HS256), agreed with Het, its owner.
5. **Secrets register:** the "Owner member" of every row in `docs/secrets.md`, and the date the rows were checked against the stores.

## Blockers

None for the templates. The outcome is blocked on the member actions above.

## Proposed decisions

None.

## Open issues

- **Single pull request.** The card says "one branch and pull request per part". The run prompt asks for one branch and one draft pull request for all three parts, with each commit authored by its part's owner.
- **Card test reviewer.** The card's test is "Review by Junaid; CI guards job green", but Junaid owns a part of this card. The run prompt names Manasvi as the pull-request reviewer; Junaid's review of the filled-in record is still pending.
- **Deploy-workflow secrets.** Their names (for example the staging connection string and the Render deploy hook) are set by IMP-112, which adds their register rows; this part invents no names.
