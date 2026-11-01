# Curated destinations

One folder per destination slug, `data/places/<slug>/`, holding the four data files below and the `quality_report.md` the seed writes beside them. Which destinations and sources are used is decided in [PLAN.md](PLAN.md) and recorded in [docs/decisions/destinations.md](../../docs/decisions/destinations.md).

The file format is the one of specification §5.6, the same format as the SAMPLE fixture in [data/fixtures/sampleton/](../fixtures/sampleton/) (IMP-107). The seed loads a folder with:

```sh
SEED_DIRS=data/places/<slug> make seed
```

(`python -m app.places.seed <dir> ...`). From IMP-205 the seed also applies the quality gate and writes `quality_report.md`.

## Files

| File | Contents | Upsert key |
| --- | --- | --- |
| `destination.json` | The destination: name, country, time zone, currency, centre and bounding box | `slug` |
| `sources.csv` | Every public page or dataset the facts come from, with its licence | `name` |
| `places.csv` | One row per place, citing one source by name | (`source_name`'s source, `external_ref`) |
| `opening_hours.csv` | Weekly opening hours per place, in local time | replaced as a set per place |
| `quality_report.md` | Written by the seed (IMP-205): rows read, loaded, rejected with reasons, flagged, usable count against the minimum | none; do not edit by hand |

General rules for the CSV files:

- **Encoding and header:** UTF-8 with a header row. The header must hold exactly the columns listed below. The seed rejects a file with a missing or an unknown column; column order does not matter, and the fixture uses the order below.
- **Empty cells:** an empty cell means "no value" (stored as NULL), never zero and never false.
- **Formats:**
  - dates are `YYYY-MM-DD`;
  - times are `HH:MM`, 24-hour, in the destination's local time;
  - booleans are `true` or `false`;
  - numbers use a point as the decimal separator and no thousands separator.
- **Quoting:** a cell containing a comma, a quote or a line break is quoted in standard CSV style (`"…"`, with an embedded quote doubled).

## destination.json

| Key | Required | Allowed values | Stored in `destinations` |
| --- | --- | --- | --- |
| `slug` | yes | Lower-case letters and digits in words joined by single hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`); use the folder name | `slug` (unique) |
| `name` | yes | 1 to 120 characters | `name` |
| `region` | no | Free text, or `null` | `region` |
| `country_code` | yes | Two capital letters (ISO 3166-1 alpha-2) | `country_code` |
| `timezone` | yes | An IANA time-zone name; the seed checks it with `zoneinfo` | `timezone` |
| `currency` | yes | Three capital letters (ISO 4217); the currency of the prices in `places.csv` | `currency` |
| `center` | yes | `{"lat": …, "lon": …}`: latitude −90 to 90, longitude −180 to 180, at most 6 decimals | `center_lat`, `center_lon` |
| `bbox` | yes | `{"min_lat": …, "max_lat": …, "min_lon": …, "max_lon": …}`, with min below max for both | `bbox_min_lat`, `bbox_max_lat`, `bbox_min_lon`, `bbox_max_lon` |
| `is_sample` | no (default `false`) | `false` for every curated destination. `true` marks SAMPLE fixtures only, and the seed refuses those outside `APP_ENV` `local` and `test` | `is_sample` |

`destinations.is_active` is not part of the file (the database default is `true`).

Every place must lie inside the bounding box: from IMP-205 the quality gate rejects a place outside it (FR-023). IMP-205 also adds the minimum usable-place count to `destination.json`, which the report compares against. That card sets the key name; §5.6 does not list it yet.

## sources.csv

| Column | Required | Allowed values | Stored in `data_sources` |
| --- | --- | --- | --- |
| `name` | yes | Unique name of the source; places cite it in `source_name` | `name` (unique) |
| `source_type` | yes | `curated_manual`, `osm_import`, `official_site`, `estimate`, `other` | `source_type` |
| `licence` | yes | The licence or terms of use as the source states them | `licence` |
| `attribution_text` | no in the database; yes when the licence asks for attribution | The attribution the licence requires, word for word | `attribution_text` |
| `url` | no in the database; yes for curated data | The public page or dataset the facts were taken from | `url` |
| `retrieved_on` | no in the database; yes for curated data (the IMP-205 gate rejects a source without a retrieved date) | `YYYY-MM-DD`: the date the facts were read from the source | `retrieved_on` |
| `notes` | no | How facts are recorded from this source, and any limit of its licence | `notes` |

## places.csv

| Column | Required | Allowed values | Stored in `places` |
| --- | --- | --- | --- |
| `external_ref` | yes | Stable identifier of the place within its source, unique in the file (for example the source's own ID). Never renumber: a reference missing from the file sets the existing place `is_active = false`, and places are never deleted | `external_ref` (unique with `source_id`) |
| `source_name` | yes | A `name` from `sources.csv` | `source_id` (resolved by the seed) |
| `name` | yes | 1 to 160 characters | `name` |
| `category` | yes | `sight`, `museum`, `nature`, `food`, `shopping`, `entertainment`, `religious`, `activity`, `stay` (`stay` is not offered in the MVP, IMP-205) | `category` |
| `tags` | no | `;`-separated tags from the tag vocabulary that IMP-205 creates (`app/places/vocabulary.py`); from then on the gate rejects an unknown tag | `tags` |
| `description` | no | At most 600 characters, written by the team in its own words; never copied text, and never sent to the model (§8.6) | `description` |
| `address` | no | Free text | `address` |
| `lat`, `lon` | yes | Decimal degrees, at most 6 decimals, inside the destination's `bbox` | `lat`, `lon` |
| `typical_duration_min` | yes | Whole minutes, 15 to 480 (DR-04) | `typical_duration_min` |
| `price_min`, `price_max` | no | Amount per person (BF-01), or per group when the place has the tag `price_per_group` (BF-02); the tags `child_half` and `child_free` set the children's share. At least 0, two decimals; `price_max` not below `price_min`; empty when no source gives a price | `price_min`, `price_max` |
| `price_currency` | when a price is given | Three capital letters; normally the destination's `currency` | `price_currency` |
| `price_label` | no (empty means `unavailable`) | `curated`, `estimate`, `unavailable` (see "Labels" below); `curated` or `estimate` only with a price, `unavailable` only without one | `price_label` |
| `hours_label` | no (empty means `unavailable`) | `curated`, `estimate`, `unavailable`; `curated` needs `hours_checked_on`; a place without rows in `opening_hours.csv` is stored as `unavailable` whatever this cell says | `hours_label` |
| `hours_checked_on` | when `hours_label` is `curated` | `YYYY-MM-DD`: the date a person checked the hours against the source | `hours_checked_on` |
| `verification_status` | yes | `unverified`, `curated_checked`, `imported_osm`, `estimated` | `verification_status` |
| `step_free`, `child_friendly`, `indoor` | no | `true`, `false`, or empty for unknown. Unknown is never written as `false` (FR-019) | `step_free`, `child_friendly`, `indoor` |
| `website_url` | no | The place's official page | `website_url` |
| `booking_url` | no | An external link only; the product books nothing (PR-10, IMD-46) | `booking_url` |

`places.is_active` and `destination_id` are set by the seed, not by the file.

## opening_hours.csv

| Column | Required | Allowed values | Stored in `place_opening_hours` |
| --- | --- | --- | --- |
| `external_ref` | yes | An `external_ref` from `places.csv` | `place_id` (resolved by the seed) |
| `weekday` | yes | `1` (Monday) to `7` (Sunday), ISO numbering | `weekday` |
| `is_closed` | yes | `true` for a day the source states as closed, else `false` | `is_closed` |
| `open_time`, `close_time` | when open | `HH:MM`, local time; both empty on a closed row | `open_time`, `close_time` |
| `closes_next_day` | no (empty means `false`) | `true` when `close_time` falls after midnight (DR-07); otherwise `close_time` must be later than `open_time` | `closes_next_day` |

Rules:

- **Several intervals:** a weekday may have more than one open row (for example a midday break), with different `open_time` values. A closed weekday has exactly one row with `is_closed` set to `true`.
- **Closed days:** write a closed day explicitly (DR-06); do not leave a weekday out to mean closed.
- **No source for the hours:** if no source gives a place's hours, give it no rows at all. It is then stored with `hours_label` `unavailable`, which is never treated as open or closed (DR-09).

## Labels: curated, estimate, unavailable

`price_label` and `hours_label` take one of three values; the interface shows them through SourceBadge (§7.8, §9.2), and no value is ever labelled live or verified (FR-076).

| Label | Use it when | What the traveller sees |
| --- | --- | --- |
| `curated` | A person entered the value from the public page named in `sources.csv`. For hours, `hours_checked_on` gives the date it was checked | "Curated, checked on <date>" |
| `estimate` | The value is calculated or assumed, not checked against a page (§9.2: "Calculated or assumed, not checked") | "Estimate" |
| `unavailable` | No source gives the value. The price cells stay empty and the place has no hour rows | "Unavailable", never a guessed value, never shown as zero, never treated as closed |

`verification_status` describes the row as a whole:

| Value | Meaning |
| --- | --- |
| `curated_checked` | Entered by the team from the named source and checked |
| `imported_osm` | Imported from OpenStreetMap data without a person checking each fact |
| `estimated` | Values are estimates (the SAMPLE fixture uses this) |
| `unverified` | Not yet checked |

Provenance is carried by the source (`source_name` gives `licence`, `url` and `retrieved_on`) and by the row (`verification_status`, `price_label`, `hours_label` and `hours_checked_on`). Every place needs all of them before it counts as usable (US-026 AC2).

## Curator checklist

Before a row is committed:

- [ ] **Every fact has a source.** The place's `source_name` is in `sources.csv`, and that source has a `url`, a `licence` and a `retrieved_on` date. Every price and every opening hour comes from a public page named in `sources.csv` (US-026 AC3).
- [ ] **Unavailable, never guessed (PR-02).** Anything that cannot be sourced stays unavailable: empty price cells with `price_label` `unavailable`, and no hour rows. No fact is filled from memory, from another website that is not listed, or from an AI assistant (IMP-206 step 2; §5.6).
- [ ] **No personal data.** Do not record names of private people, private phone numbers or e-mail addresses, reviews by named people, or photos of people. Business contact details belong on the place's own page, so use `website_url` rather than copying them.
- [ ] **Checked-on date recorded.** `retrieved_on` on the source is the date the facts were read, and `hours_checked_on` on each place with `curated` hours is the date they were checked.
- [ ] **Licence respected.** The source's licence allows this use. `attribution_text` holds the attribution the licence asks for, and nothing beyond what the licence allows is copied. `description` is always the team's own words.
- [ ] **Format checks pass.**
  - the category is from the list above;
  - the duration is 15 to 480;
  - the coordinates are inside the `bbox`;
  - `price_max` is not below `price_min`;
  - a price has a currency;
  - unknown suitability is left empty, not `false`.
- [ ] **Stable references.** `external_ref` values are not renumbered, and a place that closes is removed from the file (so it is deactivated), not overwritten with another place.
- [ ] **Load check.** The folder loads with `SEED_DIRS=data/places/<slug> make seed` on the local stack, and `quality_report.md` lists no unexpected rejects.
