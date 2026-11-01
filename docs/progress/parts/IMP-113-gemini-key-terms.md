# IMP-113 · gemini-key-terms part

- Run id: RUN-014
- Owner: Nidhi (Nidhi9864)
- Status: template ready, outcome pending (HUMAN card: Nidhi reads the official pages, creates the key and records the facts)
- Base commit: daeb8e0
- Branch: feat/IMP-113-accounts-keys (one pull request for the card's three parts, as the run prompt asks)
- Reviewer: Manasvi (Manasvi1704)
- Traces to: US-004 (AC3); NFR-013, NFR-037; OD-04, OD-14
- Card steps prepared: the template for step 3. No tier, term, rate limit, model identifier, page, URL or date was entered, and every result field reads "TO BE FILLED BY NIDHI".

## Changed files

- `docs/decisions/accounts.md` (modified): section 3, Gemini.
  - **Results table:**
    - tier (free or paid);
    - the data-use terms accepted, and what they say about prompts and responses on that tier;
    - the rate limits shown for the chosen model;
    - the chosen `GEMINI_MODEL_ID`;
    - the spending control for the billed key (NFR-037);
    - the key stored in the password manager and the Render settings (yes/no);
    - the date.
  - **Model ID rules:** the §8 rules for the identifier (one specific stable ID, never `-latest` or a preview ID), with no candidate picked.
  - **Pages read:** a table of the official pages read, with title, URL and date.
  - **Where the key lives:** only in the password manager and the hosting dashboards (CLAUDE.md §6), never in pull-request CI, and with no `GOOGLE_API_KEY`.

  It also says that the IMP-301 spike confirms the model and records the API style (OD-14) in `docs/decisions/gemini-setup.md`.
- `docs/progress/parts/IMP-113-gemini-key-terms.md` (this record).

No code, migration, contract or environment variable name changed.

## Commands and results

The checks ran once for the card, on the final text of all three sections. Section 3 contains only Markdown, and the grep found no URL in it.

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| `grep -n -E '<key, token, credential URL, e-mail and URL patterns>' accounts.md secrets.md` | `secret-pattern grep: 1 matches`: a repository path in section 2 matched the long-token pattern (a false positive) |
| The same grep with `/` removed from the long-token pattern | `secret-pattern grep (paths excluded): 0 matches` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  4.19s (environment 56%, tests 16%, setup 15%, import 9%, transform 3%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed` |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Gemini tier, terms and model identifier are recorded with the date (US-004 AC3) | not verified | Pending Nidhi: the section 3 fields are empty |
| No key value appears in the repository (secret scan green, TC-354) | not verified in this record | Shown by the CI `guards` job (gitleaks) on the pull request; the local grep found no key, token, credential URL or e-mail address |

## Outcome needed from Nidhi

1. **Tier:** free or paid.
2. **Data-use terms:** the terms accepted, by name, and what they say about the use of prompts and responses on that tier.
3. **Rate limits:** those shown for the chosen model, copied as shown.
4. **`GEMINI_MODEL_ID`:** the chosen identifier, following the §8 rules (to be confirmed by the IMP-301 spike, OD-04).
5. **Spending control:** for the billed key, set (yes/no) and where (NFR-037).
6. **Key storage:** stored in the password manager and the Render settings (yes/no).
7. **Pages read:** each official page with its title, URL and read-on date.
8. **Date:** the date the pages were read and the key created.

## Blockers

None for the templates. The outcome is blocked on the member actions above.

## Proposed decisions

None.

## Open issues

- **OD-14 (API style)** is not decided in this card. The card cites it in step 3, but the decision register and §8 give it to the IMP-301 spike (Nidhi and Manya, before Sprint 3), which records it in `docs/decisions/gemini-setup.md`. Section 3 points there.
