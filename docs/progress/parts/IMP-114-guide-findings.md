# IMP-114 · guide-findings part

- Run id: RUN-015
- Owner: Krrish (Assassin-byte)
- Status: template ready, outcome pending (HUMAN card: Krrish records the findings and opens the change requests after Junaid's interviews)
- Base commit: daeb8e0
- Branch: feat/IMP-114-interviews (one pull request for the card's two parts, as the run prompt asks)
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-151 (AC2); §2 register
- Card steps prepared:
  - step 1: the guide and consent note, written in full;
  - step 3: the template for the findings summary and the change-request procedure (step 4 allows drafting these).

  No finding, quote, count, conflict or issue was entered, and every result field reads "TO BE FILLED BY KRRISH".

## Changed files

- `docs/acceptance/interview-guide.md` (created):
  1. the purpose of round 1;
  2. a consent note to read aloud: voluntary, anonymised notes, no recording without permission;
  3. the stakeholder roles to cover, each with its specification source;
  4. 15 open, neutral questions grouped by FR area, each citing the FR IDs it probes:
     - accounts and trips;
     - places;
     - generation;
     - validation;
     - editing;
     - costs and routes;
     - output and accessibility;
  5. the out-of-scope reminder: booking, payments and live prices (§1.3, IMD-46) are recorded as out-of-scope wishes, not conflicts;
  6. the rules for anonymised notes.
- `docs/acceptance/interviews-round1.md` (created; this part writes the header and the findings half):
  - the findings summary table: finding, interview numbers, related FR IDs, conflict with §2 yes/no, and the issue link;
  - an out-of-scope wishes table;
  - the change-request procedure: one issue labelled `change-request` per conflict, citing FR IDs;
  - a change-request issue table.
- `docs/progress/parts/IMP-114-guide-findings.md` (this record).

No code, migration, contract or FR ID changed. No issue or label was created.

## Commands and results

The checks ran on the final text of both files, including Junaid's session log.

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| FR ID check (scratch script): every `FR-NNN` in both files against the FR rows of §2 (§2.1 to §2.6, 135 IDs) | `FR ID check: PASS (42 cited, 0 unknown)` |
| Personal-data check (scratch script): e-mail and phone patterns, and the capitalised names that occur in both files | `personal-data check: PASS (0 e-mail or phone matches)`. The only names are the team members Krrish and Junaid, as part owners |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  5.07s (environment 67%, setup 11%, tests 9%, import 6%, transform 6%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed` |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Every conflict found has a change-request issue citing FR IDs (US-151 AC2) | not verified | Pending Krrish after the interviews: the findings and change-request tables are empty |

## Outcome needed from Krrish

1. **Findings table:** after Junaid's five interviews, one row per finding, with the interview numbers, the related FR IDs (exactly as in §2.2) and conflict with §2 yes/no.
2. **Out-of-scope wishes:** recorded with the interview numbers and the §1.3 item.
3. **Change requests:**
   - one GitHub issue labelled `change-request` per conflict, citing the FR IDs, following the procedure in `interviews-round1.md`;
   - each issue link in both tables, with its opened-on date;
   - or "No conflicts found" with the date.

## Blockers

None for the templates. The outcome is blocked on the interviews (run-interviews part, Junaid).

## Proposed decisions

None.

## Open issues

- **The blueprint is not in the repository.** Step 1 cites "blueprint §4 and Appendix D", but no blueprint file exists here; the specification only cites it. The guide was built from the specification instead: §1.1, §1.2, §1.3, §1.6, §2.2 and the card. No blueprint content was invented.
- **No stakeholder section in the specification.** The roles in guide section 3 are taken from the people §1.1 and §2.2 describe, plus the supervisor named in the card's test. Junaid may adjust the mix.
- **US-151 has no story text in the repository.** Only its two acceptance criteria appear, on the card.
- **The `change-request` label does not exist** in `het-lathiya/Group12` (`gh label list` shows none). This run created no label; whoever opens the first change request creates it.
- **Single pull request.** The card says "one branch and pull request per part"; the run prompt asks for one branch and one draft pull request for both parts, with each commit authored by its part's owner.
