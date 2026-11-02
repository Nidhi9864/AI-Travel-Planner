# IMP-311 · whole-task part

- Run id: RUN-027
- Owner: Malhar (Malhar1112-v)
- Status: PR_OPEN
- Base commit: 1baa1f0
- Branch: feat/IMP-311-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-166; FR-136, FR-138; NFR-034; TC-441, TC-442, TC-337; IMD-01, IMD-107, IMD-110, IMD-113, IMD-115 (Amendment A1 §5.2 to §5.4)
- Card steps built: 1 to 7

## Changed files

- **Step 1: the SQL.** These were copied with `cp` from `docs/spec/sql/` and not retyped. `diff` against each source reported **identical**:
  - `apps/api/migrations/sql/0007_rag_store.sql` (created);
  - `apps/api/migrations/sql/down/0007_rag_store.down.sql` (created).
- **Step 2: `apps/api/migrations/versions/0007_rag_store.py` (created).** It is revision `0007` with down revision `0006`. It runs the two files exactly as 0001 to 0006 do. `alembic heads` shows `0007 (head)`, the only head.
- **Step 3: ORM models.**
  - `apps/api/app/db/models/rag.py` (created) holds `RagDocument` and `RagChunk`. `embedding` is typed `pgvector.sqlalchemy.Vector(768)` (`EMBEDDING_DIMENSIONS`).
  - `apps/api/app/db/models/itinerary.py` (modified): `ItineraryItem.source_chunk_ids` is `ARRAY(UUID)` with server default `'{}'`.
  - `apps/api/app/db/models/generation.py` (modified): `AiGeneration` gains `retrieval_mode` and `embedding_model_id`. It also gains `retrieval_ms` (integer, nullable), as the run prompt's narrowing asks, because 0007 adds that column.
  - `apps/api/app/db/models/__init__.py` (modified) registers and exports the two models.
- **Step 3: `apps/api/pyproject.toml` (modified).** It adds `pgvector>=0.5,<0.6`, which installed 0.5.1 with no dependencies; numpy is optional and not installed. The reason is the `Vector(768)` column type of `rag_chunks.embedding` (IMD-115).
- **Step 3: `apps/api/tests/api/test_schema_drift.py` (modified).** The table set is now the 15 MVP tables plus `RAG_TABLES` (`rag_documents`, `rag_chunks`), both for the table check and for the parameterised column and key checks. No vector-specific mapping was needed: importing `pgvector.sqlalchemy` registers the `vector` type for reflection, and `VECTOR(768)` compares equal.
- **Step 4: images.** `docker-compose.yml` `db` and the `.github/workflows/ci.yml` `api` job service both changed from `postgres:16` to `pgvector/pgvector:pg16`. The compose header comment was updated to match. There is no other CI change.
- **Step 6: `apps/api/tests/api/test_rag_store.py` (created; TC-441, TC-442).** It holds 7 tests, using SAMPLE rows over the Sampleton fixture:
  - **Cosine query:** an exact `order by embedding <=> cast(:q as vector) limit 1` over a place document and a guide document with unit-vector chunks returns the nearest chunk. An unembedded chunk is skipped, and the ORM reads 768 dimensions back.
  - **CHECK rejections** (sqlstate 23514): a place document without `place_id` (and a guide document with one); an embedding without `embedding_model_id`; a 1,201-character chunk (1,200 is accepted); 4 `source_chunk_ids` (3 are accepted, and the default is `[]`).
  - **Browser roles:** `anon` and `authenticated` have none of the 7 table privileges on either table, and RLS is enabled.
- **`apps/api/tests/authz/test_rls.py` (modified, IMP-106 file, not on the card's Files list).** TC-345 writes one row into every table of the ORM metadata and fails when a table has no row. It now also writes one `rag_documents` row and one `rag_chunks` row, so it proves that browser roles read zero rows from the RAG tables too. Without this change `make test-authz` failed with `AssertionError: rag_chunks has no row to read`. The test is extended, not weakened.
- This record (created).

Unchanged: the tables of 0001 to 0006, the 0007 SQL text, every API schema, `contracts/`, environment variable names, and `app/rag/` (not created).

## Step 5: extension version

| Database | `select extversion from pg_extension where extname = 'vector'` |
| --- | --- |
| Supabase CLI local stack (`make stack-up`, CLI v2.122.0; `make db-migrate` ran `Running upgrade 0006 -> 0007`, `alembic_version` = `0007`, tables `rag_chunks,rag_documents`) | **0.8.2** |
| compose `db` (`pgvector/pgvector:pg16`) | 0.8.7 |

## Checks that the tests can fail

- I changed the rejected item in the citations test to 3 ids. The run printed `Failed: DID NOT RAISE IntegrityError` and `1 failed, 6 passed, 187 deselected, 1 warning in 1.56s`. The change was reverted.
- Before `test_rls.py` was extended, `make test-authz` failed on the RAG tables (above), which shows that the inventory sees them.

## Commands run

| Command | Result |
| --- | --- |
| `diff docs/spec/sql/0007_rag_store.sql apps/api/migrations/sql/0007_rag_store.sql` | identical (no output) |
| `diff docs/spec/sql/down/0007_rag_store.down.sql apps/api/migrations/sql/down/0007_rag_store.down.sql` | identical (no output) |
| `cd apps/api && .venv/bin/alembic heads` | `0007 (head)` |
| `make db-down`, `make db-up` | `Container group12-db-1 Healthy`; `docker compose ps`: `db pgvector/pgvector:pg16 Up … (healthy)` |
| `make db-up && make test-api ARGS='-k rag_store'` | `7 passed, 187 deselected, 1 warning in 1.66s` |
| `make test-api ARGS='-k drift'` | `35 passed, 152 deselected, 1 warning in 1.47s` |
| Round trip on the compose pgvector database: `alembic downgrade base`, then `alembic upgrade head` | `Running downgrade 0001 -> ` … `Running upgrade 0006 -> 0007`; `alembic current` = `0007 (head)` |
| `make stack-up`, `make db-migrate` (local Supabase), extension query | `Running upgrade 0006 -> 0007`; `extversion: 0.8.2` |
| `make lint` | `All checks passed!`, `124 files already formatted`, `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 76 source files`; `✓ Types generated successfully` |
| `make imports` | `Contracts: 4 kept, 0 broken.` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |
| `make test` | unit `374 passed, 1 warning in 8.46s`; contract `35 passed, 1 warning in 0.89s`; api `194 passed, 1 warning in 44.92s`; authz `9 passed in 1.82s`; web `Tests  54 passed (54)` |
| `make check` | exit 0, with the lines above |

## Not run

- `make e2e`: no journey changed.
- The CI round trip and the 0007 apply in the CI `api` job: see the pull request's checks.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Migration 0007 applies to a blank PostgreSQL 16 with pgvector and survives the CI round trip; the drift test is green (TC-441, NFR-034) | verified locally; CI pending | Local round trip on `pgvector/pgvector:pg16`; `make test-api ARGS='-k drift'` green |
| The 0007 checks reject the invalid rows of step 6, and an exact cosine query returns the nearest chunk (TC-442) | verified | `test_rag_store.py` (7 passed) |
| The compose `db` and the CI `api` job run `pgvector/pgvector:pg16`; the local Supabase stack migrates to head with the extension present | verified | `docker compose ps`; `ci.yml` diff; local stack at `0007` with `vector` 0.8.2 |
| TC-337 drift test | verified | 35 passed, including the two RAG tables |
| Browser roles have no privilege on the new tables | verified | `test_rag_store_browser_roles_have_no_privilege`; TC-345 extended in `test_rls.py` |

## Blockers

None.

## Proposed decisions

- **PD-IMP-311-1 (spec text for the test image):** §4.1 (the `docker-compose.yml` row), the §4.5 environment table and card IMP-105 still say `postgres:16` for the compose `db` and the CI service. IMP-311 and IMD-115 change the image to `pgvector/pgvector:pg16`. Proposed: update those rows.
- **PD-IMP-311-2 (card Files list):** `tests/authz/test_rls.py` (TC-345) has to write a row into every table of the ORM metadata. Any card that adds a table must therefore also touch it. Proposed: add it to the Files list of table-adding cards, starting with this one.

## Open issues

- `make stack-up` restored an existing local database ("Starting database from backup"). That database was at `0006` and migrated to `0007`. The stack was stopped again with `make stack-down`.
- The Supabase CLI reports a newer version (v3.0.0; v2.122.0 is installed). It was not updated in this run.
- `rag_chunks.embedding` is mapped as `list[float] | None`. Without numpy, pgvector 0.5.1 returns a sequence of floats when reading. IMP-313 and IMP-315 decide the vector type their code uses.
