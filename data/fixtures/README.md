# Test fixtures (SAMPLE)

Synthetic test fixtures labelled SAMPLE, such as the sampleton destination. Nothing here describes a
real place, business, address or price, and nothing here is personal data. Automated tests use only
these fixtures (IMD-09); curated destinations live in `data/places/<slug>/`.

## sampleton/

Loaded by `make seed` (`python -m app.places.seed data/fixtures/sampleton`, specification §5.6). The
seed refuses it unless `APP_ENV` is `local` or `test`, because `destination.json` has `is_sample: true`.

| File | Contents |
| --- | --- |
| `destination.json` | `sampleton`, "Sampleton (sample)": invented centre and bounding box out at sea (no town), `Europe/London`, `GBP`, `is_sample: true` |
| `sources.csv` | One data source, "SAMPLE fixture (synthetic)": `source_type` `other`, licence "synthetic test data", notes `synthetic` |
| `places.csv` | 30 places, `external_ref` `sample-001` to `sample-030`; every name starts with "Sample" or "Fixture" and ends with "(sample)"; `verification_status` `estimated`; prices labelled `estimate`, or `unavailable` with no price |
| `opening_hours.csv` | Weekly hours (1 = Monday, local time) for 27 places; the other 3 have `hours_label` `unavailable` and no rows |

Counts that tests rely on (IMP-107 step 2):

| Property | Places |
| --- | --- |
| Per category | sight 4, museum 4, nature 4, food 6, shopping 3, entertainment 3, religious 3, activity 3 (no `stay`) |
| Hours past midnight (`closes_next_day`, 18:00 to 02:00) | 3: `sample-015`, `sample-023`, `sample-024` |
| Closed on Monday (`is_closed`) | 3: `sample-005`, `sample-007`, `sample-016` |
| No hours rows, `hours_label` `unavailable` | 3: `sample-003`, `sample-009`, `sample-026` |
| `step_free` true | 2: `sample-001`, `sample-005` |
| `price_label` `unavailable` (no price) | 2: `sample-007`, `sample-017` |

Change these files only together with the tests that count them (`apps/api/tests/api/test_seed.py`).
