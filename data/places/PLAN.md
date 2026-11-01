# Seed-data plan: the two demo destinations (IMP-115)

- Card: IMP-115 · Seed-data plan and choice of the two demo destinations (US-152)
- Plan owner: Malhar · Reviewer: Junaid
- Status: **template; outcome pending** (TO BE FILLED BY MALHAR)
- Used by: IMP-206 (curate and load destination 1, Jeel with Malhar), IMP-603 (curate and load destination 2, Junaid with Manya and Kirtan), IMP-205 (quality gate and minimum count)
- File format: [README.md](README.md) (specification §5.6)

Every field marked **TO BE FILLED BY MALHAR** is a team decision. Nothing in this template is a choice of destination, source, licence, count or fact.

## 1. The two destinations

Choose both by **data availability**: whether public pages exist, under a licence that allows this use, for enough places, opening hours and prices to reach the minimum usable count of section 2.

| | Destination 1 | Destination 2 |
| --- | --- | --- |
| Name | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Slug (folder `data/places/<slug>/`) | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Country code, IANA time zone, currency | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Reason, judged by data availability | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |

Evidence for the reason, one row per destination. Count only what the listed sources actually show; do not estimate.

| Data availability evidence | Destination 1 | Destination 2 |
| --- | --- | --- |
| Places with a public source, roughly counted | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Of those, places with opening hours on a public page | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Of those, places with prices on a public page | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Food places (the meal slots of every day need them) | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Spread over the categories (sight, museum, nature, food, shopping, entertainment, religious, activity) | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Licences allow entering the facts in this repository | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Other candidates considered and why not chosen | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |

## 2. Minimum usable-place count

A usable place passes the quality gate (IMP-205): it has a known source with licence and retrieved date, a verification status, coordinates inside the bounding box, an allowed category and a duration of 15 to 480 minutes. Hours and prices may be `unavailable`.

| | Destination 1 | Destination 2 |
| --- | --- | --- |
| Figure given by the card and the specification | 100 (IMP-115, IMP-206; §5.6 "curated about 100", AS-06) | No card figure; §5.6 says "curated about 100" |
| Team decision: confirmed, or a lower figure | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |
| Reason, if lower than 100 | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |

## 3. One-city fallback if destination 2 slips

| Item | Decision |
| --- | --- |
| When destination 2 counts as slipped (date or condition) | TO BE FILLED BY MALHAR |
| What the demo and the gates use instead | TO BE FILLED BY MALHAR |
| What happens to destination 2 data already entered | TO BE FILLED BY MALHAR |
| Who decides that the fallback applies | TO BE FILLED BY MALHAR |

## 4. Sources per destination

One row per source, which becomes one row of that destination's `sources.csv`.

**Fields provided:** list the `places.csv` and `opening_hours.csv` columns the source gives, for example `name`, `lat`/`lon`, hours or prices.

**How facts are recorded:** describe who enters the facts, how the curator reads them from the page, which label (`curated` or `estimate`) and which `verification_status` they get, and where the checked-on date goes.

`source_type` is one of `curated_manual`, `osm_import`, `official_site`, `estimate` or `other`.

### Destination 1: TO BE FILLED BY MALHAR

| Source name | URL | Licence | `source_type` | Fields it provides | How facts are recorded |
| --- | --- | --- | --- | --- | --- |
| TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |

### Destination 2: TO BE FILLED BY MALHAR

| Source name | URL | Licence | `source_type` | Fields it provides | How facts are recorded |
| --- | --- | --- | --- | --- | --- |
| TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR | TO BE FILLED BY MALHAR |

Add rows as needed. A fact whose source is not in this table is not entered.

## 5. Unavailable, never guessed (PR-02)

This rule is stated as the specification and the task register give it:

- "Facts that cannot be sourced stay unavailable" (IMP-115 step 2, PR-02).
- "Enter hours and price ranges only from official or public pages named in sources.csv; mark everything else unavailable; never fill a fact from memory or from an AI assistant" (IMP-206 step 2).
- "Curated data under `data/places/<slug>/` is entered by people from the named public pages, never from memory or from a model" (§5.6).
- Unavailable means "Unknown; never shown as zero and never treated as closed" (§9.2). "Unknown hours are never treated as open or closed" (DR-09).

In the files: an unsourced price leaves `price_min`, `price_max` and `price_currency` empty with `price_label` `unavailable`. Unsourced hours mean no rows in `opening_hours.csv`, which the seed stores as `hours_label` `unavailable`. Unknown suitability is left empty, never `false`. See the curator checklist in [README.md](README.md).

## 6. Review by Junaid

| Item | Result |
| --- | --- |
| Review date | TO BE FILLED BY MALHAR |
| Outcome (approved, or changes requested with the list) | TO BE FILLED BY MALHAR |
| Changes made after the review | TO BE FILLED BY MALHAR |
| Decision record | [docs/decisions/destinations.md](../../docs/decisions/destinations.md) |
