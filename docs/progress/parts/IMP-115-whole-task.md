# IMP-115 · whole-task part

- Run id: RUN-013
- Owner: Malhar (Malhar1112-v)
- Status: templates ready, outcome pending (HUMAN card: the decisions are Malhar's, the review is Junaid's)
- Base commit: daeb8e0 (the preflight fetch showed d05ca5d; IMP-111 merged before the branch was created from `main`)
- Branch: feat/IMP-115-whole-task
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: US-152; PR-02
- Card steps prepared: step 3 written in full; templates for steps 1, 2 and 4. No destination, source, place, price, opening hour, licence or count was chosen, and every result field reads "TO BE FILLED BY MALHAR".

## Changed files

- `data/places/README.md` (step 3). It replaces the one-line purpose note that IMP-101 placed there ("Curated destinations, one folder per slug with its quality_report.md."), and that sentence stays as the opening line. The guide covers:
  - the curated-destination file format of §5.6, the same format as `data/fixtures/sampleton/` (IMP-107);
  - the four files, with every key or column, whether it is required, its allowed values and the database column it is stored in;
  - the provenance and verification fields;
  - how `price_label` and `hours_label` express `curated`, `estimate` and `unavailable` (§9.2, §7.8);
  - the curator checklist: every fact sourced; unavailable, never guessed (PR-02); no personal data; checked-on dates; licences respected; format checks; stable `external_ref`; load check.
- `data/places/PLAN.md` (template for steps 1, 2 and 4), with six sections:
  1. the two destinations and the reason, with a data-availability evidence table;
  2. the minimum usable-place count: the card's 100 for destination 1 with a confirm-or-lower field and reason, and a field for destination 2, for which the card gives no figure;
  3. the one-city fallback;
  4. a sources table per destination (name, URL, licence, `source_type`, fields provided, how facts are recorded);
  5. the PR-02 rule, quoted;
  6. Junaid's review (date, outcome, changes).
- `docs/decisions/destinations.md` (template for step 4): the decision record. Its fields for the date, decider, reviewer, review outcome, both destinations, the reason, both minimum counts and the fallback are all empty; a consequences list links IMP-206, IMP-603 and IMP-205.
- `docs/progress/parts/IMP-115-whole-task.md` (this record).

No code, migration, contract or fixture changed.

## Column check (format contract)

A scratch script, kept outside the repository, parsed the column tables of `data/places/README.md` and compared them with three things:

- the `create table` blocks of `apps/api/migrations/sql/0002_reference_data.sql` and `0003_accounts_trips.sql`;
- `SOURCE_COLUMNS`, `PLACE_COLUMNS` and `HOURS_COLUMNS` and the `destination.json` keys read in `apps/api/app/places/seed.py`;
- the sampleton CSV headers.

| Check | Result |
| --- | --- |
| Every "stored in" column exists in its table: `destinations` 13, `data_sources` 7, `places` 22, `place_opening_hours` 6 | OK |
| README file columns equal the seed's: `sources.csv` 7, `places.csv` 22, `opening_hours.csv` 6 | OK |
| The sampleton header of each CSV equals the seed's column tuple | OK |
| README `destination.json` keys equal the keys the seed reads (9), including the `center` and `bbox` sub-keys (6) | OK |
| README allowed values include every CHECK value of `source_type`, `category`, `price_label`, `hours_label` and `verification_status` | OK |
| `0003_accounts_trips.sql` creates none of the four reference tables (it only references `destinations` and `places` by foreign key) | OK |
| Summary line | `column check: PASS (0 failures)` |
| Mutation: the same script on a scratch copy with `booking_url` renamed in the README | `column check: FAIL (1 failures)` |

**Result:** no mismatch between §5.6, migrations 0002 and 0003, and `seed.py`. The four reference tables are all defined in 0002; 0003 holds no columns of them.

## Commands and results

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `d05ca5d` (then `daeb8e0` after IMP-111 merged; the branch base) |
| `python check_columns.py <repo>` (scratch, above) | `column check: PASS (0 failures)` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make check` | `   Duration  3.93s (environment 63%, tests 16%, setup 12%, import 7%, transform 2%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, imports `Contracts: 3 kept, 0 broken.`) |
| `make db-down` | ` Network group12_default Removed ` |

Prettier (`make lint`) checks `apps/web` only, so the new Markdown files are not linted by any make target.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| `data/places/PLAN.md` names two destinations, sources per destination and the minimum usable-place count (US-152 AC1) | not verified | Pending Malhar: the template's sections 1, 2 and 4 are empty |
| Each source lists its licence and how facts are recorded (US-152 AC2) | not verified | Pending Malhar: the section 4 tables have the licence and "How facts are recorded" columns, but no rows |
| The "unavailable, never guessed" rule is stated (US-152 AC3) | verified (stated in the template) | PLAN.md section 5 and the README checklist state it, quoted from IMP-115 step 2, IMP-206 step 2, §5.6, §9.2 and DR-09. The card's acceptance test ("Review by Junaid") still applies to the whole plan |

## Outcome needed from Malhar

1. **The two destinations:** each with its name, slug, country code, time zone, currency, and the reason judged by data availability. Fill the evidence table in PLAN.md section 1, including the candidates considered.
2. **The minimum usable-place count:**
   - destination 1: confirm 100, or record a lower figure with the reason;
   - destination 2: set a figure, since the card gives none and §5.6 says "curated about 100".
3. **The one-city fallback if destination 2 slips:** the trigger, what the demo and gates use instead, what happens to data already entered, and who decides.
4. **Per source and per destination:** the source name, URL, licence, `source_type`, the fields it provides, and how facts are recorded (who enters them, which label and verification status, where the checked-on date goes).
5. **Junaid's review:** the date, the outcome and any changes. Then fill `docs/decisions/destinations.md` (decision date, decided by, reviewer, both destinations, reason, minimums, fallback) and set both statuses from pending.

## Blockers

None for the templates. The card's outcome is blocked on the member decisions above.

## Proposed decisions

None.

## Open issues

- **PR-02 has no definition text in the repository.** Neither `docs/spec/IMPLEMENTATION_SPEC.md` nor `TASK_REGISTER.md` defines PR-02 (or PR-01 and PR-03); they only cite them, so the principles appear to live in the blueprint. PLAN.md section 5 therefore quotes the rule from the places where the specification states it (IMP-115 step 2, IMP-206 step 2, §5.6, §9.2, DR-09) and does not invent a PR-02 sentence.
- **Minimum count key:** IMP-205 adds the minimum usable-place count to `destination.json` (its step 3: "usable count vs the minimum in destination.json"). §5.6 does not list that key yet, so the README names no key and leaves it to that card.
- **Rules not yet enforced:** the IMP-205 quality gate (bounding box, tag vocabulary, retrieved date required, usable count) does not exist yet. The README marks these rules as arriving with IMP-205; the current seed enforces only the file format and the database CHECKs.
- **Source name:** the SAMPLE source in the fixture is "SAMPLE fixture (synthetic)", while §5.6 says "SAMPLE fixture data" (PD-IMP-107-1, already reported). It does not affect curated data.
