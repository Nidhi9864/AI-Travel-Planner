# IMP-114 · run-interviews part

- Run id: RUN-015
- Owner: Junaid (Junaid-Kureshi), card lead
- Status: template ready, outcome pending (HUMAN card: Junaid holds the five interviews and records the anonymised notes)
- Base commit: daeb8e0
- Branch: feat/IMP-114-interviews (one pull request for the card's two parts, as the run prompt asks)
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-151 (AC1)
- Card steps prepared: the template for step 2. No interview, interviewee, date, role, consent, note or review result was entered, and every result field reads "TO BE FILLED BY JUNAID".

## Changed files

- `docs/acceptance/interviews-round1.md` (modified; this part writes the session-log half):
  - five rows (interviews 1 to 5) with the date, stakeholder role, consent given, recording allowed, interviewer and anonymised notes;
  - the rules for notes and for the case where consent is not given;
  - the line confirming recordings were deleted;
  - the supervisor review line (the card's test: "Review by Junaid and the supervisor").
- `docs/progress/parts/IMP-114-run-interviews.md` (this record).

No code, migration, contract or FR ID changed.

## Commands and results

The checks ran once for the card, on the final text of both files including this session log.

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| FR ID check (scratch script): every `FR-NNN` in both files against the FR rows of §2 | `FR ID check: PASS (42 cited, 0 unknown)` |
| Personal-data check (scratch script): e-mail and phone patterns, and the capitalised names that occur in both files | `personal-data check: PASS (0 e-mail or phone matches)`. The only names are the team members Krrish and Junaid, as part owners |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  5.07s (environment 67%, setup 11%, tests 9%, import 6%, transform 6%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed` |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| `docs/acceptance/interviews-round1.md` lists five anonymised interviews (US-151 AC1) | not verified | Pending Junaid: the five session-log rows are empty |

## Outcome needed from Junaid

1. **Five interviews,** held with the guide (`docs/acceptance/interview-guide.md`) and its consent note read aloud. For each interview record:
   - the date;
   - the stakeholder role from guide section 3;
   - consent given (yes/no) and recording allowed (yes/no);
   - the interviewer (a team member);
   - anonymised notes, with no names, contact details or other identifying details.
2. **Recordings,** if any were made: deleted after the notes were written, and the line in the session log filled in.
3. **Supervisor review:** the date, the outcome and any changes requested.

## Blockers

None for the template. The outcome needs five interviewees and the supervisor's review.

## Proposed decisions

None.

## Open issues

- **Card test reviewer.** The card's test is "Review by Junaid and the supervisor". The run prompt names Kirtan as the pull-request reviewer; the supervisor's review is recorded in the session log once it happens.
- **Single pull request.** The card says "one branch and pull request per part"; the run prompt asks for one branch and one draft pull request for both parts, with each commit authored by its part's owner.
