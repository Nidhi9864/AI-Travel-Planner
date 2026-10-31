-- Migration 0004_ai_and_plan (MVP). Generation records and the current plan: ai_generations, itinerary_days, itinerary_items, itinerary_warnings, itinerary_versions, route_cache.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0004_ai_and_plan.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

create table public.ai_generations (
  id                    uuid primary key default gen_random_uuid(),
  trip_id               uuid not null references public.trips(id) on delete cascade,
  user_id               uuid not null references public.profiles(id) on delete cascade,
  provider              text not null check (provider in ('GEMINI','MOCK','FINETUNED_MODEL')),
  model_id              text not null,
  model_version         text,
  adapter_version       text,                         -- version of the adapter code that made the call (NFR-042)
  prompt_template_id    text not null,
  prompt_version        text not null,
  input_schema_version  text not null default 'gr-1',
  output_schema_version text not null default 'io-1',
  mapping_version       text not null,
  generation_settings   jsonb not null default '{}'::jsonb,   -- parameter names and values only, never prompt text (NFR-042)
  scope                 text not null check (scope in ('full','day','edit')),
  scope_day_number      smallint check (scope_day_number between 1 and 14),   -- set only for scope 'day' (API-30)
  status                text not null default 'queued'
                        check (status in ('queued','running','validating','repairing','completed','failed')),
  outcome               text check (outcome in ('model','model_repaired','fallback_rule_based','failed')),
  failure_reason        text check (failure_reason in ('provider_timeout','provider_rate_limited',
                          'provider_quota_exhausted','provider_unavailable','invalid_output',
                          'unresolved_validation','config_error','internal')),
  repair_attempts       smallint not null default 0 check (repair_attempts between 0 and 1),
  deterministic_repairs smallint not null default 0 check (deterministic_repairs >= 0),
  validation_summary    jsonb not null default '{}'::jsonb,
  latency_ms            integer check (latency_ms >= 0),
  input_tokens          integer check (input_tokens >= 0),
  output_tokens         integer check (output_tokens >= 0),
  thinking_tokens       integer check (thinking_tokens >= 0),
  cost_estimate_usd     numeric(10,6) check (cost_estimate_usd >= 0),
  cost_basis            text,
  request_hash          text not null,                -- SHA-256 of the canonical request; never the content
  created_at            timestamptz not null default now(),
  completed_at          timestamptz,
  retention_until       timestamptz not null default (now() + interval '90 days'),  -- default is proposed
  check ((scope = 'day') = (scope_day_number is not null)),
  check (
    (status = 'completed' and outcome in ('model','model_repaired','fallback_rule_based') and failure_reason is null and completed_at is not null)
    or (status = 'failed' and outcome = 'failed' and failure_reason is not null and completed_at is not null)
    or (status in ('queued','running','validating','repairing') and outcome is null and completed_at is null)
  )
);
create index ix_aigen_trip     on public.ai_generations (trip_id, created_at desc);
create index ix_aigen_user_day on public.ai_generations (user_id, created_at);
create index ix_aigen_retention on public.ai_generations (retention_until);
create index ix_aigen_active   on public.ai_generations (created_at)
  where status in ('queued','running','validating','repairing');

create table public.itinerary_days (
  id                   uuid primary key default gen_random_uuid(),
  trip_id              uuid not null references public.trips(id) on delete cascade,
  day_number           smallint not null check (day_number between 1 and 14),
  plan_date            date not null,
  theme                text check (char_length(theme) <= 80),
  source_generation_id uuid references public.ai_generations(id) on delete set null,
  created_at           timestamptz not null default now(),
  updated_at           timestamptz not null default now(),
  unique (trip_id, day_number),
  unique (id, trip_id)                                -- target of the composite foreign key below
);

create table public.itinerary_items (
  id                    uuid primary key default gen_random_uuid(),
  trip_id               uuid not null references public.trips(id) on delete cascade,
  day_id                uuid not null,
  position              smallint not null check (position >= 1),
  place_id              uuid not null references public.places(id) on delete restrict,
  slot_type             text not null default 'activity' check (slot_type in ('activity','meal','rest')),
  start_time            time not null,
  duration_min          integer not null check (duration_min between 15 and 480),    -- DR-04 limits (proposed)
  origin                text not null check (origin in ('model','fallback_rule_based','user')),
  note                  text check (char_length(note) <= 200),
  note_origin           text not null default 'none' check (note_origin in ('ai','user','none')),
  is_locked             boolean not null default false,
  cost_min              numeric(10,2) check (cost_min >= 0),     -- group total, computed by the backend
  cost_max              numeric(10,2) check (cost_max >= 0),
  cost_currency         char(3) check (cost_currency ~ '^[A-Z]{3}$'),
  cost_label            text check (cost_label in ('estimate','curated','unavailable')),
  travel_from_prev_min  integer check (travel_from_prev_min >= 0),
  travel_from_prev_m    integer check (travel_from_prev_m >= 0),
  travel_mode           text check (travel_mode in ('walking','local_transport','car')),
  travel_source         text check (travel_source in ('routing_api','fallback_estimate')),
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),
  foreign key (day_id, trip_id) references public.itinerary_days (id, trip_id) on delete cascade,
  unique (day_id, position) deferrable initially deferred,
  check (cost_max is null or cost_min is null or cost_max >= cost_min),
  check ((cost_min is null and cost_max is null) or (cost_currency is not null and cost_label is not null)),
  check ((travel_from_prev_min is null) = (travel_source is null)
         and (travel_from_prev_min is null) = (travel_mode is null)),
  check ((note is null) = (note_origin = 'none'))
);
create index ix_items_trip  on public.itinerary_items (trip_id);
create index ix_items_place on public.itinerary_items (place_id);

create table public.itinerary_warnings (
  id             uuid primary key default gen_random_uuid(),
  trip_id        uuid not null references public.trips(id) on delete cascade,
  plan_revision  integer not null,
  code           text not null check (code in ('OVERLAP','TRANSFER_TOO_SHORT','CLOSED_ON_DAY','OUTSIDE_HOURS',
                   'HOURS_UNVERIFIED','DAY_TOO_LONG','BUDGET_EXCEEDED','BUDGET_NEAR','MUST_VISIT_MISSING',
                   'UNKNOWN_PLACE','OUTSIDE_TRIP_DATES','COST_INCOMPLETE','ESTIMATE_USED')),
  severity       text not null check (severity in ('error','warning','info')),
  message        text not null check (char_length(message) <= 500),
  day_number     smallint check (day_number between 1 and 14),
  item_id        uuid references public.itinerary_items(id) on delete cascade,
  place_id       uuid references public.places(id) on delete cascade,   -- set only for MUST_VISIT_MISSING (IMD-42)
  suggested_fix  text check (char_length(suggested_fix) <= 500),
  created_at     timestamptz not null default now(),
  check ((code = 'MUST_VISIT_MISSING') = (place_id is not null)),
  check (code <> 'MUST_VISIT_MISSING' or item_id is null)
);
create index ix_warnings_trip on public.itinerary_warnings (trip_id, plan_revision);
create index ix_warnings_item on public.itinerary_warnings (item_id) where item_id is not null;

create table public.itinerary_versions (
  id                 uuid primary key default gen_random_uuid(),
  trip_id            uuid not null references public.trips(id) on delete cascade,
  version_no         integer not null check (version_no >= 1),
  reason             text not null check (reason in ('generation','regeneration','edit','restore','fallback','manual')),
  name               text check (char_length(name) between 1 and 80),   -- set for a named version (API-37)
  plan_revision      integer not null,
  snapshot           jsonb not null,
  validation_summary jsonb not null default '{}'::jsonb,
  generation_id      uuid references public.ai_generations(id) on delete set null,
  created_by         uuid references public.profiles(id) on delete set null,
  created_at         timestamptz not null default now(),
  unique (trip_id, version_no),
  check (reason <> 'manual' or name is not null)
);
create unique index ux_versions_name on public.itinerary_versions (trip_id, name) where name is not null;
create index ix_versions_generation on public.itinerary_versions (generation_id) where generation_id is not null;

create table public.route_cache (
  from_place_id  uuid not null references public.places(id) on delete cascade,
  to_place_id    uuid not null references public.places(id) on delete cascade,
  mode           text not null check (mode in ('walking','local_transport','car')),
  travel_minutes integer not null check (travel_minutes >= 0),
  distance_m     integer not null check (distance_m >= 0),
  travel_source  text not null check (travel_source in ('routing_api','fallback_estimate')),
  provider_name  text,
  computed_at    timestamptz not null default now(),
  expires_at     timestamptz not null,
  primary key (from_place_id, to_place_id, mode),
  check (from_place_id <> to_place_id)
);
create index ix_route_cache_expiry on public.route_cache (expires_at);
create index ix_route_cache_to on public.route_cache (to_place_id);
