[Sprint_Work_Distribution.md](https://github.com/user-attachments/files/33431053/Sprint_Work_Distribution.md)
# AI Travel Planner: Backend Sprint Work Distribution

**Project:** AI Travel Planner (IT314 Software Engineering — Group 12)  
**Scope:** Backend Engineering, System Architecture & Production Deployment  
**Target Architecture:** FastAPI, PostgreSQL 15, SQLAlchemy 2.0, Alembic, Gemini LLM (google-genai), Google Places & Routes APIs, ReportLab, Docker, Nginx, GitHub Actions CI/CD  

---

## 1. Engineering Team Roles & Phased Project Model

This document establishes the official governance, task ownership, and sprint distribution for the **Backend & Infrastructure Engineering Team**.

To ensure clear specialization, seamless collaboration, and high accountability, the backend project lifecycle is organized into two distinct operational phases:

1. **Phase 1: Backend Feature Engineering (Sprints 1 to 4)**  
   The entire backend feature set—API routing, database models, session pooling, Alembic migrations, business domain rules, AI pipelines, external API adapters, optimization algorithms, financial calculations, PDF document generation, and unit/integration test suites—is built **exclusively by three backend engineers**: **Het**, **Manal**, and **Jeel**.  
   Workload in Phase 1 is divided **strictly equally (33.3% per engineer)**. During this phase, **Kirtan writes zero backend feature code**, focusing instead on pre-deployment architecture, containerization strategies, and cloud infrastructure planning.

2. **Phase 2: Production Deployment & Infrastructure Operations (Sprint 5)**  
   When the backend features are complete, **Kirtan executes 100% of the deployment, containerization, cloud hosting, CI/CD automation, production database provisioning, SSL/TLS reverse proxy hardening, secret auditing, and release operations**.  
   Het, Manal, and Jeel do not write deployment infrastructure; they perform only functional smoke-test verification of their respective completed features on the deployed live server.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   PHASE 1: BACKEND FEATURE BUILD (SPRINTS 1–4)                   │
│                                                                                  │
│   Het (33.3%)                 Manal (33.3%)                 Jeel (33.3%)         │
│   ├── Core Architecture       ├── Security & Auth           ├── Trip Domain & CRUD
│   ├── AI Pipeline (Gemini)    ├── DB Engine & Pooling       ├── Places Verification
│   ├── Output Validation       ├── Financial Engine          ├── Route Optimizer
│   └── Transport Service       └── ReportLab PDF Export      └── Alembic Migrations
│                                                                                  │
│   [Kirtan: Pre-deployment research & cloud environment specification — 0% code]  │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Backend Feature Freeze & Handoff
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│              PHASE 2: PRODUCTION DEPLOYMENT & DEVOPS (SPRINT 5)                  │
│                                                                                  │
│                           Kirtan (100% Deployment Lead)                          │
│   ├── Production Multi-Stage Docker Containerization                             │
│   ├── Cloud Infrastructure & Managed PostgreSQL Provisioning                     │
│   ├── Automated GitHub Actions CI/CD Deployment Pipeline                         │
│   ├── Production Environment Secrets Configuration & Security Audit              │
│   ├── Automated Production Database Migration & Data Seeding                     │
│   ├── Nginx Reverse Proxy with SSL/TLS (HTTPS) & Production CORS                 │
│   ├── Production Rate Limiting, Health Probes & Log Monitoring                   │
│   └── Automated Live Smoke Testing & Disaster Recovery / Rollback Runbook        │
│                                                                                  │
│   [Het, Manal, Jeel: Functional verification & endpoint sign-off on live cloud]  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Team Member Responsibility Profile

| Member | Designated Role | Primary Responsibilities | Phase Allocation |
| :--- | :--- | :--- | :---: |
| **Het** | **AI Pipeline & Core Architecture Engineer** | Core FastAPI framework, configuration, unified error envelopes, Gemini LLMClient, prompt engineering, generation workflow, strict output validator, multi-modal transport service, and schedule feasibility validator. | **Phase 1 Lead (33.3% Feature Build)** |
| **Manal** | **Security, Authentication & Financial Domain Engineer** | Argon2 hashing, JWT token lifecycle, security guards (`deps.py`), database engine/session pooling, itinerary models/persistence, cost calculation engine, budget alerts, and ReportLab PDF document compilation. | **Phase 1 Lead (33.3% Feature Build)** |
| **Jeel** | **Trip Domain, Places Verification & Geo-Spatial Optimization Engineer** | Trip domain models/CRUD, Alembic migration framework, Google Places API verification & fallback engine, 2-opt heuristic route optimizer, atomic itinerary customization pipeline, and test harness setup. | **Phase 1 Lead (33.3% Feature Build)** |
| **Kirtan** | **Production Deployment, Cloud Infrastructure & DevOps Engineer** | Multi-stage Docker containerization, cloud hosting setup, CI/CD automated deployment pipelines, production database provisioning & migration execution, SSL/TLS reverse proxy, production rate limiting, secret leak audits, and live smoke testing. | **Phase 2 Lead (100% Deployment Work)** |

---

## 2. Module Ownership & Codebase Responsibility Map

Every module within `ai-travel-planner/backend/` and related root deployment infrastructure has an assigned primary owner:

```text
ai-travel-planner/
├── Dockerfile, Dockerfile.prod                      ← Kirtan (Production multi-stage containerization)
├── docker-compose.yml, docker-compose.prod.yml      ← Kirtan (Container orchestration, networks, volumes)
├── .github/workflows/deploy.yml                     ← Kirtan (Automated CI/CD deployment pipeline)
├── nginx/nginx.conf                                 ← Kirtan (Reverse proxy, SSL termination, security headers)
├── scripts/
│   ├── deploy.sh                                    ← Kirtan (Cloud deployment execution script)
│   ├── dev-backend.sh                               ← Het (Local development helper script)
│   └── seed_reference_data.py                       ← Jeel (Reference data seeding script)
├── backend/
│   ├── app/
│   │   ├── main.py                                  ← Het (Application lifecycle, CORS, middleware)
│   │   ├── core/
│   │   │   ├── config.py, exceptions.py, logging.py ← Het (Configuration, exceptions, redacted logging)
│   │   │   ├── security.py                          ← Manal (Argon2 hashing, JWT token issuer/verifier)
│   │   │   └── rate_limit.py                        ← Manal (Slowapi rate limiter configuration)
│   │   ├── api/
│   │   │   ├── deps.py                              ← Manal (Authentication & DB session dependencies)
│   │   │   └── v1/
│   │   │       ├── router.py                        ← Het (Router aggregation & prefix registration)
│   │   │       └── endpoints/
│   │   │           ├── health.py                    ← Het (Liveness and readiness health probes)
│   │   │           ├── auth.py                      ← Manal (Registration, login, user profile)
│   │   │           ├── trips.py                     ← Jeel (Trip CRUD & preference management)
│   │   │           ├── itineraries.py               ← Het & Manal (Generation & persistence endpoints)
│   │   │           ├── export.py                    ← Manal (PDF document streaming endpoint)
│   │   │           └── admin.py                     ← Jeel (System metrics & user administration)
│   │   ├── db/
│   │   │   ├── base.py, session.py                  ← Manal (Database engine, connection pool, Base)
│   │   ├── models/
│   │   │   ├── user.py                              ← Manal (User entity & credentials)
│   │   │   ├── trip.py                              ← Jeel (Trip & TripPreferences with CHECK constraints)
│   │   │   └── itinerary.py                         ← Manal (Itinerary, Day, Item, CostItem, RouteLeg)
│   │   ├── schemas/
│   │   │   ├── auth.py                              ← Manal (Login, Register, Token payload schemas)
│   │   │   ├── trip.py                              ← Jeel (TripCreate, TripUpdate, validation schemas)
│   │   │   └── itinerary.py                         ← Jeel (Itinerary generation & mutation schemas)
│   │   ├── repositories/
│   │   │   ├── user_repository.py                   ← Manal (User queries & credential verification)
│   │   │   ├── trip_repository.py                   ← Jeel (Trip queries scoped by authenticated user)
│   │   │   └── itinerary_repository.py              ← Manal (Itinerary persistence & eager joins)
│   │   ├── domain/
│   │   │   ├── rules.py                             ← Het (System domain rules DR-01 to DR-09)
│   │   │   ├── schedule_validator.py                ← Het (Temporal overlap, duration, opening-hours check)
│   │   │   ├── cost_calculator.py                   ← Manal (Spending aggregation, daily splits, alerts)
│   │   │   └── route_optimizer.py                   ← Jeel (2-opt heuristic TSP route solver)
│   │   ├── integrations/
│   │   │   ├── base.py, provider_registry.py        ← Jeel (Base HTTP provider & dynamic registry)
│   │   │   ├── places.py                            ← Jeel (Google Places POI search & hours adapter)
│   │   │   ├── routes.py                            ← Manal (Google Routes distance/time matrix adapter)
│   │   │   ├── amadeus.py, ground_transport.py      ← Het (Amadeus flight/hotel & transit adapters)
│   │   ├── services/
│   │   │   ├── auth.py                              ← Manal (Authentication service & claims)
│   │   │   ├── trip.py                              ← Jeel (Trip lifecycle business service)
│   │   │   ├── itinerary_service.py                 ← Het & Manal (Generation & persistence orchestration)
│   │   │   ├── verification.py                      ← Jeel (Place verification & fallback selection)
│   │   │   ├── routing.py                           ← Manal (Transit matrix & route caching operations)
│   │   │   ├── transport.py                         ← Het (Multi-modal transport comparison service)
│   │   │   ├── budget.py                            ← Manal (Budget status, overrun & threshold alerts)
│   │   │   ├── validation.py                        ← Het (Schedule feasibility & constraint service)
│   │   │   └── export.py                            ← Manal (ReportLab PDF compilation service)
│   │   └── ai/
│   │       ├── base.py                              ← Het (Abstract LLMClient interface)
│   │       ├── gemini_client.py                     ← Het (Google GenAI Gemini client with retries)
│   │       ├── prompts.py                           ← Het (System instructions & grounded facts builder)
│   │       ├── generation.py                        ← Het (AI generation workflow orchestrator)
│   │       ├── alternatives.py                      ← Het (AI activity replacement candidate generator)
│   │       └── output_validator.py                  ← Het (Strict JSON parsing & structural validator)
│   ├── alembic/ & alembic.ini                       ← Jeel & Manal (Migrations & linear revision chain)
│   └── tests/
│       ├── conftest.py, fixtures/                   ← Jeel (Pytest test database harness & recorded fixtures)
│       ├── unit/                                    ← Authored by respective feature owner (Het, Manal, Jeel)
│       └── integration/                             ← Authored by respective feature owner (Het, Manal, Jeel)
└── docs/deployment/
    └── runbook.md                                   ← Kirtan (Deployment runbook & rollback procedures)
```

---

## 3. Engineering Protocols & Ground Rules

1. **Strict 3-Developer Feature Build Protocol:** Sprints 1 to 4 are built exclusively by Het, Manal, and Jeel. Every backend feature PR must originate from one of these three engineers and be reviewed and approved by at least one of the other two feature engineers before merging into `main`.
2. **Dedicated Deployment Lead Protocol:** Kirtan owns 100% of Sprint 5. All container configurations, CI/CD workflows, cloud infrastructure, reverse proxy settings, production database provisioning, secret scanning, and automated smoke testing are executed by Kirtan.
3. **Test-Driven Delivery:** Every backend feature PR must include comprehensive unit and integration tests. Minimum line coverage target is 85% for domain services.
4. **Isolated Test Execution:** Unit and integration tests must run 100% offline using recorded mock JSON fixtures located in `tests/fixtures/`. Tests must never make live external HTTP calls during CI runs.
5. **Database Migration Linearity:** All schema changes must be committed as distinct Alembic migration scripts. Branching migration heads are strictly rejected; migrations must be rebased and verified against PostgreSQL 15 before merge.
6. **Data Privacy & Defense-in-Depth:** Free-text inputs must be sanitized and length-limited (NFR-07). All database access must be filtered by `user_id`. Queries targeting private resources belonging to another user must return HTTP 404 rather than 403 to prevent resource discovery (NFR-06). Passwords must never appear in application logs or exception payloads.

---

## 4. Sprint 1: Project Foundation, Database Architecture, Authentication & Trip Management

*Establishes the core backend application, PostgreSQL database session pooling, database migrations, cryptographic authentication, and the complete Trip CRUD domain. Built entirely by Het, Manal, and Jeel.*

- **Target Requirements:** FR-01, FR-02, FR-03, FR-04; US-01, US-02, US-03, US-04; NFR-05, NFR-06, NFR-07, NFR-08, NFR-09, NFR-12.
- **Participating Engineers:** Het (33.3%), Manal (33.3%), Jeel (33.3%).  
  *(Kirtan: 0% feature code; researches target cloud platform requirements and multi-stage container optimization).*

### Equal Work Distribution (Het, Manal, Jeel)

#### Het (Core Application Architecture, Runtime & Health — 33.3%)
1. **Application Shell & Lifecycle:** Implement `app/main.py` with FastAPI initialization, lifespan management, OpenAPI metadata, and CORS middleware configured for development origins.
2. **Environment Configuration:** Build `app/core/config.py` using `pydantic-settings` to load and validate backend environment variables (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, API provider keys).
3. **Exception Architecture:** Create `app/core/exceptions.py` defining domain exceptions (`EntityNotFoundException`, `UnauthorizedException`, `ValidationException`) and global HTTP exception handlers producing unified RFC-7807 error envelopes.
4. **Credential-Safe Logging:** Implement `app/core/logging.py` featuring structured JSON formatting and regex redaction for passwords, API keys, and JWT bearer tokens (NFR-09).
5. **Health Endpoints & Local Runtime:** Write `app/api/v1/endpoints/health.py` (`GET /health` liveness and readiness probes) and `scripts/dev-backend.sh` for developer local startup.

#### Manal (Security, Authentication & DB Session Layer — 33.3%)
1. **User Database Model:** Implement `app/models/user.py` with SQLAlchemy 2.0 mapped columns: `id`, `email` (unique index), `hashed_password`, `role` (user/admin), `is_active`, `created_at`, and `updated_at`.
2. **Cryptographic Engine:** Implement `app/core/security.py` featuring password hashing using Argon2id (`argon2-cffi`) and JWT access token creation and decoding (`python-jose`).
3. **Database Engine & Connection Pool:** Implement `app/db/session.py` and `app/db/base.py` configuring SQLAlchemy connection pooling (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`).
4. **Authentication Schemas & Service:** Create `app/schemas/auth.py` (`UserRegister`, `UserLogin`, `TokenResponse`, `UserResponse`) and `app/services/auth.py` with registration and credential verification logic.
5. **Auth Endpoints & Dependencies:** Implement `app/api/v1/endpoints/auth.py` (`POST /auth/register`, `POST /auth/login`, `GET /auth/me`), `app/api/deps.py` with the reusable `get_current_user` FastAPI dependency, and `tests/integration/test_auth.py`.

#### Jeel (Trip Domain, Migrations & Test Harness — 33.3%)
1. **Trip Database Models:** Implement `app/models/trip.py` with `Trip` and `TripPreferences` tables, foreign keys to `users.id`, and database-level `CheckConstraint` enforcing `traveler_count > 0`, `budget_amount > 0`, and `end_date >= start_date`.
2. **Alembic Migration System Baseline:** Initialize `alembic.ini` and `alembic/env.py` configured for SQLAlchemy 2.0; generate the baseline migration script creating `users`, `trips`, and `trip_preferences` tables.
3. **Pydantic Validation Schemas:** Build `app/schemas/trip.py` (`TripCreate`, `TripUpdate`, `TripResponse`) enforcing strict field validations: positive traveler counts, valid ISO dates, currency codes, non-empty interest arrays, and travel style enums.
4. **Trip Repository & Service:** Implement `app/repositories/trip_repository.py` and `app/services/trip.py` ensuring every database query automatically scopes by `user_id` to strictly isolate private trips between users.
5. **Trip CRUD Endpoints & Pytest Harness:** Implement `app/api/v1/endpoints/trips.py` (`POST /trips`, `GET /trips`, `GET /trips/{id}`, `PATCH /trips/{id}`, `DELETE /trips/{id}`), `tests/conftest.py` with isolated transaction rollbacks, and `tests/integration/test_trips.py`.

### Sprint 1 Deliverable & Verification Check
- **Deliverable:** Fully functional core backend engine running locally, allowing users to register, log in with JWT, and execute isolated Trip CRUD operations with validated database constraints.
- **Verification:** All tests in `test_auth.py` and `test_trips.py` pass; database migrations run cleanly from scratch.

---

## 5. Sprint 2: AI Itinerary Generation, Structured Output Validation & Location Verification Engine

*Implements the core AI generation loop using Gemini via the official google-genai SDK, structured JSON output validation, real-world Google Places verification, fallback substitution, and itinerary database persistence. Built entirely by Het, Manal, and Jeel.*

- **Target Requirements:** FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-16; US-05, US-08, US-11, US-13, US-18, US-19, US-20, US-23; NFR-03, NFR-10, NFR-11, NFR-12, NFR-13, NFR-14.
- **Participating Engineers:** Het (33.3%), Manal (33.3%), Jeel (33.3%).  
  *(Kirtan: 0% feature code; designs cloud secrets hierarchy and automated CI/CD workflow blueprints).*

### Equal Work Distribution (Het, Manal, Jeel)

#### Het (AI Pipeline, Generation Loop & Output Validation — 33.3%)
1. **Abstract LLM Client Interface:** Implement `app/ai/base.py` defining the `LLMClient` protocol, generation parameter structures, and unified exception classes (`LLMTimeoutException`, `LLMQuotaException`, `LLMMalformedException`).
2. **Gemini SDK Implementation:** Build `app/ai/gemini_client.py` wrapping the `google-genai` SDK with API key resolution from server environments, configurable model parameters, and request timeouts.
3. **System & User Prompt Engineering:** Author `app/ai/prompts.py` constructing structured generation prompts that enforce day-wise schemas, incorporate trip constraints, sanitize user free text, and inject ground truth facts.
4. **Generation Workflow Orchestrator:** Implement `app/ai/generation.py` coordinating the AI request lifecycle and executing bounded retries (up to 3 attempts) feeding validation errors back to the model.
5. **Strict JSON Output Validator:** Implement `app/ai/output_validator.py` parsing raw model output, validating JSON types, checking day-count alignment with trip duration (DR-05), detecting temporal overlaps, and authoring `tests/unit/test_output_validator.py`.

#### Manal (Itinerary Persistence, Models & Initial Cost Aggregator — 33.3%)
1. **Itinerary Data Models:** Implement `app/models/itinerary.py` defining `Itinerary`, `ItineraryDay`, `ItineraryItem`, and `CostItem` entities with foreign keys, cascade deletes, and data provenance enums.
2. **Itinerary Repository Layer:** Build `app/repositories/itinerary_repository.py` with optimized queries utilizing `selectinload` for eager-loading days, activities, and cost records in a single query.
3. **Atomic Persistence Transaction:** Implement transactional database persistence in `app/services/itinerary_service.py` ensuring the complete itinerary structure (days, items, initial cost items) is written atomically or rolled back completely on failure.
4. **Preliminary Financial Calculator:** Implement the initial version of `app/domain/cost_calculator.py` aggregating estimated costs across categories and flagging provisional status if costs are unverified (DR-07).
5. **Database Migration & Itinerary Endpoints:** Create Alembic revision for itinerary tables and implement `app/api/v1/endpoints/itineraries.py` (`GET /trips/{trip_id}/itineraries`, `GET /itineraries/{id}`, `DELETE /itineraries/{id}`) enforcing strict user ownership.

#### Jeel (Place Verification, Fallbacks, Provider Registry & Schemas — 33.3%)
1. **Provider Registry Architecture:** Implement `app/integrations/base.py` and `app/integrations/provider_registry.py` with an extensible adapter registration pattern and shared HTTP client with timeout management.
2. **Google Places Adapter:** Author `app/integrations/places.py` interfacing with the Google Places API (Find Place from Text, Place Details) to retrieve real-world coordinates, place IDs, address data, and operating hours.
3. **Verification Service & Fallback Engine:** Implement `app/services/verification.py` checking every AI-suggested POI against Google Places and querying alternative nearby places matching the user's selected interests when a primary suggestion is unverified (FR-08, AF-06).
4. **Itinerary Pydantic Schemas & Provenance:** Author `app/schemas/itinerary.py` defining strict input/output structures and tagging places with explicit data provenance labels (`Verified`, `Cached`, `Estimated`, `Unverified`, `Unavailable`) complying with DR-08 and NFR-14.
5. **Recorded Mock Fixtures & Integration Suite:** Author offline mock datasets in `tests/fixtures/gemini_responses.json` and `tests/fixtures/places_responses.json`, and implement `tests/integration/test_itineraries.py` validating end-to-end generation and fallback handling.

### Sprint 2 Deliverable & Verification Check
- **Deliverable:** Working AI generation pipeline producing validated, structured, multi-day itineraries with real-world location verification and fallback substitution, stored securely in PostgreSQL.
- **Verification:** Unit tests in `test_output_validator.py` and integration tests in `test_itineraries.py` pass; simulated provider failure gracefully returns user-friendly error envelope with retry option.

---

## 6. Sprint 3: Interactive Maps, Route Calculation, 2-opt Heuristic Optimization & Transport Services

*Connects itinerary activities with real-world geographic routing via the Google Routes API, implements an intelligent 2-opt Travelling Salesperson route optimization algorithm, caches routes, and provides multi-modal transport comparison. Built entirely by Het, Manal, and Jeel.*

- **Target Requirements:** FR-11, FR-12, FR-13, FR-14, FR-15; US-06, US-10, US-14, US-21, US-22; NFR-04, NFR-14.
- **Participating Engineers:** Het (33.3%), Manal (33.3%), Jeel (33.3%).  
  *(Kirtan: 0% feature code; evaluates managed cloud PostgreSQL configurations and SSL certificate automated renewal options).*

### Equal Work Distribution (Het, Manal, Jeel)

#### Het (Transport Integrations, Multi-Modal Comparison & Haversine — 33.3%)
1. **Amadeus Integration Adapter:** Implement `app/integrations/amadeus.py` connecting to Amadeus for Developers API with client credential OAuth2 token rotation, supporting flight offers search and hotel list lookups.
2. **Ground Transit Reference Adapter:** Implement `app/integrations/ground_transport.py` providing structured timetable and fare estimates for intercity rail and bus connections.
3. **Multi-Modal Transport Service:** Implement `app/services/transport.py` calculating and comparing transportation choices (flights, trains, buses, local transit, and distance-based cab estimates) sorted by cost and travel time.
4. **Transport & Accommodation Endpoints:** Build endpoints in `app/api/v1/endpoints/itineraries.py` (`GET /itineraries/{id}/transport`, `GET /itineraries/{id}/accommodation`) returning options tagged with data provenance and provider booking links.
5. **Haversine Distance Fallback & Tests:** Implement Haversine straight-line distance math as a graceful fallback when routing APIs are unreachable (AF-10) and write `tests/unit/test_transport.py`.

#### Manal (Google Routes API, Routing Service & Route Cache Layer — 33.3%)
1. **Google Routes API Adapter:** Implement `app/integrations/routes.py` invoking the Google Routes API (Compute Route Matrix and Route Geometry) supporting driving, walking, and transit travel modes.
2. **Routing Domain Service:** Implement `app/services/routing.py` taking consecutive itinerary stops, computing point-to-point distances (meters) and durations (seconds), and formatting human-readable metrics.
3. **Route Data Entities & Cache Table:** Define `RouteLeg` models and `route_cache` table in `app/models/itinerary.py` storing origin/destination coordinates, polyline geometry, mode, distance, duration, and TTL expiration.
4. **Route Cache Repository & Endpoints:** Implement caching repository layer and `GET /itineraries/{id}/routes` delivering daily route polylines, segment distances, and estimated travel times.
5. **Database Migration & Routing Tests:** Create Alembic revision for `route_legs` and `route_cache`, and author `tests/integration/test_routing.py` testing route queries and cache hits.

#### Jeel (2-Opt Route Optimization Algorithm & Geo-Spatial Performance — 33.3%)
1. **2-Opt Route Optimization Algorithm:** Implement `app/domain/route_optimizer.py` utilizing nearest-neighbor heuristic initialization improved by 2-opt local search to eliminate route backtracking.
2. **Anchor-Based Clustering:** Build clustering logic in `app/domain/route_optimizer.py` anchoring daily activity sequences to accommodation locations or primary morning arrival points.
3. **Optimization Service Endpoint:** Build `POST /itineraries/{id}/optimize` in `app/services/itinerary_service.py` to reorder itinerary items in the database and return before-and-after travel time metrics.
4. **Unverified Place Handling in Routing:** Implement logic in `route_optimizer.py` excluding unverified or missing-coordinate places from routing calculations while preserving their scheduled slots (AF-10).
5. **Mock Fixtures & Performance Benchmark Suite:** Author `tests/fixtures/routes_responses.json` and `tests/unit/test_route_optimizer.py` demonstrating that route recalculation for a 7-day trip finishes under the 5-second SLA (NFR-04).

### Sprint 3 Deliverable & Verification Check
- **Deliverable:** Complete geo-spatial routing engine with 2-opt route optimization, distance/time computation, route caching, and multi-modal transport comparison endpoints.
- **Verification:** All tests in `test_route_optimizer.py` and `test_routing.py` pass; route calculation benchmarks consistently execute under 5 seconds.

---

## 7. Sprint 4: Financial/Budget Engine, Schedule Feasibility Validation, Customization & PDF Export

*Delivers the financial calculation engine with budget thresholds and alerts, schedule validation for conflict detection, an atomic customization pipeline, AI-powered alternative activity replacement, and ReportLab PDF export. Built entirely by Het, Manal, and Jeel.*

- **Target Requirements:** FR-16, FR-17, FR-18, FR-19, FR-20, FR-21; US-07, US-09, US-12, US-13; NFR-04, NFR-17, NFR-18.
- **Participating Engineers:** Het (33.3%), Manal (33.3%), Jeel (33.3%).  
  *(Kirtan: 0% feature code; finalizes production Dockerfile multi-stage builds and writes cloud provisioning scripts).*

### Equal Work Distribution (Het, Manal, Jeel)

#### Het (Schedule Feasibility, Opening Hours & AI Alternatives — 33.3%)
1. **Schedule Feasibility Validator:** Implement `app/domain/schedule_validator.py` enforcing temporal rules: positive activity durations, zero temporal overlaps between scheduled items (DR-04), and transit feasibility between stops (DR-06).
2. **Opening Hours Validation:** Enhance `schedule_validator.py` with opening-hours checking against verified POI operating hours (DR-01); explicitly ensure missing hours are never assumed open (NFR-14).
3. **AI Activity Alternatives Generator:** Implement `app/ai/alternatives.py` generating substitute activity recommendations based on remaining time windows, budget headroom, and user interests (US-09).
4. **Validation Service & Endpoint:** Implement `app/services/validation.py` and `POST /itineraries/{id}/validate` returning structured conflict diagnostics (`ScheduleConflictError`) with actionable resolution suggestions.
5. **Concurrency Guards & Schedule Tests:** Implement concurrency locking guards during validation and author `tests/unit/test_schedule_validator.py` covering boundary conditions, temporal overlaps, and transit violations.

#### Manal (Financial Engine, Budget Tracking & PDF Document Generation — 33.3%)
1. **Financial Calculation Engine:** Complete `app/domain/cost_calculator.py` supporting category aggregation, planned daily budget division, multi-currency verification, and provisional flags for unpriced items.
2. **Budget Status & Alert Service:** Implement `app/services/budget.py` and `GET /itineraries/{id}/budget` returning spending totals, 80% threshold warnings, 100% budget overrun alerts, and lower-cost alternatives (DR-03, AF-09).
3. **ReportLab PDF Document Engine:** Implement `app/services/export.py` compiling the latest saved itinerary into a clean, formatted PDF document containing day-by-day schedules, route notes, and cost breakdowns.
4. **PDF Streaming Endpoint:** Implement `app/api/v1/endpoints/export.py` (`GET /itineraries/{id}/export/pdf`) streaming the generated PDF binary with proper MIME headers (`application/pdf`) and filename disposition.
5. **Budget & Export Test Suites:** Author `tests/unit/test_cost_calculator.py` (budget boundaries, 80% threshold, currency handling) and `tests/integration/test_export.py` (PDF structure validation, failure isolation where PDF error leaves data intact AF-11).

#### Jeel (Customization Pipeline, Atomic Transactions & Database Auditing — 33.3%)
1. **Item Manipulation Endpoints:** Implement item-level CRUD in `app/api/v1/endpoints/itineraries.py`: `POST /itineraries/{id}/items` (add), `DELETE /itineraries/{id}/items/{item_id}` (remove), and `PUT /itineraries/{id}/days/{day_id}/order` (reorder).
2. **Alternative Replacement Endpoint:** Implement `POST /itineraries/{id}/items/{item_id}/replace` swapping an existing itinerary item with a verified alternative while preserving day continuity.
3. **Atomic Modification Pipeline:** Build the mutation pipeline in `app/services/itinerary_service.py` that executes re-validation, route recalculation, cost re-aggregation, and budget checks within a single database transaction.
4. **State Preservation on Conflict:** Implement rollback mechanics in the modification pipeline ensuring that any edit triggering a schedule or route conflict rejects cleanly and preserves the last valid itinerary state (FR-20, AF-08, NFR-17).
5. **Database Migration & Recalculation Benchmark:** Create Alembic revision for activity sorting indices and modification audit fields, and author `tests/integration/test_customization.py` verifying recalculation under 5 seconds (NFR-04).

### Sprint 4 Deliverable & Verification Check
- **Deliverable:** Fully customizable itinerary engine with budget tracking, threshold alerts, schedule feasibility validation, atomic mutation rollback on error, and ReportLab PDF export.
- **Verification:** All tests in `test_cost_calculator.py`, `test_schedule_validator.py`, `test_customization.py`, and `test_export.py` pass cleanly.

---

## 8. Sprint 5: Production Deployment, Cloud Infrastructure & Release Operations

*Delivers the complete production release of the AI Travel Planner backend. Following the completion of the backend codebase by Het, Manal, and Jeel in Sprints 1–4, **Kirtan executes all deployment, containerization, cloud hosting, CI/CD, database provisioning, SSL/TLS reverse proxy hardening, secret auditing, and release operations in Sprint 5**.*

- **Target Requirements:** All functional requirements (FR-01 through FR-21); NFR-01, NFR-02, NFR-03, NFR-04, NFR-05, NFR-06, NFR-07, NFR-08, NFR-09, NFR-10, NFR-11, NFR-15, NFR-16, NFR-17, NFR-18.
- **Sole Deployment Lead:** **Kirtan (100% of Deployment Workload)**.  
  *(Het, Manal, Jeel: 0% deployment coding; perform post-deployment smoke test verification and feature sign-off on the live cloud server).*

### Kirtan's Complete Deployment & Infrastructure Tasks

#### 1. Production Docker Multi-Stage Containerization
- **Multi-Stage Build Architecture:** Author production-ready `Dockerfile.prod` utilizing a two-stage build:
  - *Build Stage:* Installs build compilers, wheels, and C-dependencies.
  - *Runtime Stage:* Uses lean `python:3.11-slim`, copies pre-compiled wheels, creates an unprivileged non-root user (`appuser`, UID 10001), sets bytecode compilation (`PYTHONDONTWRITEBYTECODE=1`), and configures Uvicorn workers with production timeouts.
- **Production Compose Specification:** Author `docker-compose.prod.yml` orchestrating the FastAPI backend container, PostgreSQL 15 container with persistent volume mounts, internal isolated Docker bridge network, and Nginx reverse proxy.

#### 2. Cloud Hosting & Infrastructure Provisioning
- **Cloud Platform Provisioning:** Deploy and provision the containerized backend to the selected production cloud environment (e.g., Render, Railway, AWS ECS/EC2, or GCP Cloud Run / Compute Engine).
- **Production Database Setup:** Provision managed PostgreSQL 15 database instance with connection pooling limits, automated daily snapshots, encrypted storage volumes, and firewall restrictions ensuring only backend containers can communicate with the database.

#### 3. Automated CI/CD Deployment Pipeline
- **GitHub Actions Deployment Workflow:** Author `.github/workflows/deploy.yml` automating the end-to-end release pipeline triggered on merge to `main`:
  1. *Lint & Security Check:* Runs `flake8`, `black --check`, and security scanners.
  2. *Automated Test Suite:* Executes 100% of offline pytest test suites across auth, trips, itineraries, routes, budget, and export.
  3. *Container Build & Scan:* Builds production Docker image and runs vulnerability scanning (`trivy` / GitHub code scanning).
  4. *Automated Cloud Push:* Deploys the verified image to the cloud host with zero-downtime rolling restart.

#### 4. Production Secret Management & Security Audit
- **Cloud Secret Store Configuration:** Configure production secrets within the cloud host's secure key-vault / environment manager (`DATABASE_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, `GOOGLE_MAPS_API_KEY`, `AMADEUS_API_KEY`).
- **Automated Secret Leak Scan:** Execute automated scanning tools (`git-secrets`, `trufflehog`) across Git commit history, configuration files, and build logs to verify zero exposed credentials (NFR-09).
- **Log Redaction Verification:** Confirm that structured production logging cleanly masks sensitive parameters, credentials, and JWT tokens in production log streams.

#### 5. Production Database Migration Execution & Reference Seeding
- **Automated Migration Hook:** Implement pre-deployment database migration execution (`alembic upgrade head`) ensuring that new schema revisions apply automatically before Uvicorn traffic begins serving.
- **Production Reference Data Seeding:** Execute automated production seed script (`scripts/seed_reference_data.py`) populating baseline travel categories, sample destinations, and reference transit fare standards.

#### 6. Nginx Reverse Proxy, SSL/TLS (HTTPS) & Production CORS Hardening
- **Nginx Configuration:** Author `nginx/nginx.conf` acting as the reverse proxy for the Uvicorn application server.
- **SSL/TLS Termination:** Configure SSL/TLS certificates (Let's Encrypt / Cloud SSL) enforcing strict HTTPS encryption across all API routes (NFR-08) with automatic HTTP-to-HTTPS 301 redirection.
- **Security Headers:** Enforce modern security headers: `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Content-Security-Policy`.
- **CORS Origin Whitelisting:** Restrict production CORS headers strictly to the production frontend domain, denying all unauthorized third-party cross-origin requests.
- **Production Rate Limiting:** Configure production rate limiting using `slowapi` backed by Redis or shared memory to safeguard public authentication and generation endpoints from brute-force or DoS traffic.

#### 7. Health Probes, Centralized Logging & System Monitoring
- **Health Check Integration:** Connect cloud container liveness and readiness monitors to `GET /health` ensuring failed containers are automatically recycled.
- **Centralized Log Streaming:** Configure structured JSON log aggregation and real-time error tracking (e.g. Sentry or CloudWatch/Stackdriver) to capture unhandled exceptions without leaking stack traces to clients (NFR-11).
- **Uptime & Performance Alerting:** Set up uptime monitoring alerts to notify the team in case of service degradation or API quota exhaustion.

#### 8. Automated Smoke Testing, Verification & Rollback Runbook
- **Post-Deployment Smoke Test Suite:** Execute automated live smoke tests validating that the deployed cloud instance correctly processes:
  - `GET /health` returns HTTP 200 with DB status `healthy`.
  - User registration and JWT login return valid tokens.
  - Trip creation persists and retrieves correctly from the production PostgreSQL instance.
  - AI generation endpoint triggers and completes within SLA.
  - PDF export streams a valid binary file.
- **Deployment Runbook & Rollback Strategy:** Document `docs/deployment/runbook.md` specifying step-by-step procedures for zero-downtime deployment, blue/green cutover, database backup restoration, and emergency rollback to previous stable Docker tags.

### Feature Sign-Off Verification (Het, Manal, Jeel)
Upon Kirtan's completion of the deployment pipeline, the three feature developers perform final operational verification of their respective modules on the live cloud URL:
- **Het:** Verifies live Gemini API generation, prompt grounding, and transport comparison queries.
- **Manal:** Verifies live user authentication flow, password hashing integrity, budget calculation, and PDF binary download.
- **Jeel:** Verifies live Google Places location lookups, Google Routes distance matrices, 2-opt route reordering, and trip customization.

### Sprint 5 Deliverable & Verification Check
- **Deliverable:** Fully deployed, containerized, SSL-secured, and monitored backend system running in the production cloud environment with automated CI/CD and passing smoke tests.
- **Verification:** 100% automated smoke test suite passing against the live production URL; zero exposed secrets; database migrations applied cleanly; SSL/TLS A+ rating on security checks.

---

## 9. Administrator Extensions (Post-Sprint 5 Roadmap)

The administrative functions support operational governance and platform maintenance. Built upon the foundation established in Sprints 1–5:

| Feature Story | Engineering Lead | Implementation Scope | Verification Criteria |
| :--- | :--- | :--- | :--- |
| **US-15: User Account Management** | **Manal** | `GET /admin/users`, `PATCH /admin/users/{id}/status` to deactivate accounts or audit registered users. | Enforce `require_admin` dependency; reject non-admin access with 404/403. |
| **US-16: Flagged Itineraries & Feedback** | **Jeel** | `POST /itineraries/{id}/feedback`, `GET /admin/feedback` to collect ratings and flag low-quality AI results. | Store feedback in `itinerary_feedback` table; filterable by rating and date. |
| **US-17: Reference Data Maintenance** | **Het** | `POST /admin/reference-data` to update seed destinations, transport cost baselines, and interest categories. | Ensure data validation schemas prevent corrupt reference insertions. |
| **Admin Infrastructure & Deployment** | **Kirtan** | Configure admin route rate limits, separate admin audit logs, and deploy admin dashboard routing. | Ensure admin endpoints cannot be reached from unauthorized IPs/domains. |

---

## 10. Workload Distribution Matrix & Audit

To verify that the work is divided cleanly according to the defined model—**3 developers building the backend first (Sprints 1–4), followed by Kirtan doing all deployment work (Sprint 5)**—the table below audits workload allocation across every phase and sprint.

| Project Metric | Het | Manal | Jeel | Kirtan | Phase / Team Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Assigned Role** | **AI Pipeline & Core Architecture** | **Security & Financial Domain** | **Trip Domain & Geo-Spatial** | **Production Deployment & DevOps** | **Full Team Allocation** |
| **Sprint 1 (Backend Build)** | App shell, config, exceptions, logging, health | User model, Argon2, JWT auth, DB session pool | Trip models, CHECK rules, Trip CRUD, Alembic base | *Pre-deployment research & cloud planning (0%)* | **100% (33.3% / 33.3% / 33.3%)** |
| **Sprint 2 (Backend Build)** | LLMClient, Gemini SDK, prompts, AI loop, validator | Itinerary models, eager joins, atomic persist | Places adapter, Verification, Fallbacks, Schemas | *Container strategy & CI/CD blueprint (0%)* | **100% (33.3% / 33.3% / 33.3%)** |
| **Sprint 3 (Backend Build)** | Amadeus adapter, Ground transit, Transport API | Routes API adapter, Routing service, Route cache | 2-opt TSP route optimizer, Optimization API | *Production DB config & SSL planning (0%)* | **100% (33.3% / 33.3% / 33.3%)** |
| **Sprint 4 (Backend Build)** | Schedule validator, Opening hours, Alternatives | Cost calculator, Budget service, PDF export | Customization endpoints, atomic pipeline, audits | *Docker multi-stage build manifests (0%)* | **100% (33.3% / 33.3% / 33.3%)** |
| **Sprint 5 (Deployment & Ops)** | *Live AI endpoint sign-off (0% code)* | *Live Auth & PDF sign-off (0% code)* | *Live Places/Routes sign-off (0% code)* | **Multi-stage Docker, Cloud hosting, CI/CD, DB prod, SSL/CORS, Secrets audit, Smoke tests (100%)** | **100% (Kirtan 100%)** |
| **Phase 1: Feature Build (Sprints 1–4)** | **33.3%** | **33.3%** | **33.3%** | **0.0%** | **100.0% Equal 3-Way Split** |
| **Phase 2: Deployment (Sprint 5)** | **0.0%** | **0.0%** | **0.0%** | **100.0%** | **100.0% Sole Deployment Lead** |
| **Overall Project Effort** | **25.0%** | **25.0%** | **25.0%** | **25.0%** | **100.0% Balanced Across Project** |
| **Primary Code Ownership** | `app/ai/`, `core/config.py`, `services/transport*`, `services/validation*` | `models/user*`, `core/security.py`, `db/`, `services/budget*`, `services/export*` | `models/trip*`, `domain/route*`, `integrations/places*`, `services/verification*` | `Dockerfile*`, `docker-compose*`, `.github/workflows/deploy.yml`, `nginx/`, `docs/deployment/` | **100% Backend & Deployment Stack** |
| **Test Ownership** | AI prompt/validator tests, Transport tests, Schedule tests | Auth tests, DB session tests, Cost tests, Export tests | Trip tests, Places tests, 2-opt optimizer tests, Customization | Automated CI/CD test runner, Secret scan suite, Live smoke test suite | **100% Offline & Live Test Coverage** |
