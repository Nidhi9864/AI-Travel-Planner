-- Migration 0009_weather_cache (EXT, IMP-710). Daily forecast cache from Open-Meteo for rain-aware day swapping (AX-17).
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0009_weather_cache.py.
-- Writer: MOD-B16. Reference data shared by all trips of a destination; read only through the API (CC BY 4.0 attribution shown).

create table public.weather_cache (
  destination_id          uuid not null references public.destinations(id) on delete cascade,
  forecast_date           date not null,
  precip_probability_max  smallint check (precip_probability_max between 0 and 100),
  precipitation_sum       numeric(6,1) check (precipitation_sum >= 0),
  weather_code            smallint check (weather_code between 0 and 99),
  temp_max                numeric(4,1),
  temp_min                numeric(4,1),
  fetched_at              timestamptz not null default now(),
  primary key (destination_id, forecast_date),
  check (temp_min is null or temp_max is null or temp_min <= temp_max)
);
create index ix_weather_fetched on public.weather_cache (fetched_at);

alter table public.weather_cache enable row level security;
-- No policy: browser roles have no access; the backend reads and writes it.
revoke all on table public.weather_cache from anon, authenticated;
