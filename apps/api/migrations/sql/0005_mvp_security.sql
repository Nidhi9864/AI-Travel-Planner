-- Migration 0005_mvp_security (MVP). Row-level security, ownership function and revoked browser privileges.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0005_mvp_security.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

create schema if not exists app_private;

create or replace function app_private.owns_trip(p_trip_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.trips t
    where t.id = p_trip_id and t.user_id = (select auth.uid()) and t.deleted_at is null
  );
$$;
revoke all on function app_private.owns_trip(uuid) from public;
grant usage on schema app_private to authenticated;
grant execute on function app_private.owns_trip(uuid) to authenticated;

alter table public.destinations         enable row level security;
alter table public.data_sources         enable row level security;
alter table public.places               enable row level security;
alter table public.place_opening_hours  enable row level security;
alter table public.profiles             enable row level security;
alter table public.trips                enable row level security;
alter table public.trip_preferences     enable row level security;
alter table public.trip_places          enable row level security;
alter table public.budget_settings      enable row level security;
alter table public.ai_generations       enable row level security;
alter table public.itinerary_days       enable row level security;
alter table public.itinerary_items      enable row level security;
alter table public.itinerary_warnings   enable row level security;
alter table public.itinerary_versions   enable row level security;
alter table public.route_cache          enable row level security;

-- Reference data: readable by signed-in users, writable only by migrations and the seed script.
create policy destinations_read  on public.destinations        for select to authenticated using (is_active);
create policy data_sources_read  on public.data_sources        for select to authenticated using (true);
create policy places_read        on public.places              for select to authenticated using (is_active);
create policy hours_read         on public.place_opening_hours for select to authenticated using (true);

-- Own profile.
create policy profiles_select on public.profiles for select to authenticated using (id = (select auth.uid()));
create policy profiles_insert on public.profiles for insert to authenticated with check (id = (select auth.uid()));
create policy profiles_update on public.profiles for update to authenticated
  using (id = (select auth.uid())) with check (id = (select auth.uid()));

-- Own trips and their settings.
create policy trips_owner on public.trips for all to authenticated
  using (user_id = (select auth.uid()) and deleted_at is null)
  with check (user_id = (select auth.uid()));
create policy trip_prefs_owner  on public.trip_preferences for all to authenticated
  using (app_private.owns_trip(trip_id)) with check (app_private.owns_trip(trip_id));
create policy trip_places_owner on public.trip_places for all to authenticated
  using (app_private.owns_trip(trip_id)) with check (app_private.owns_trip(trip_id));
create policy budget_owner      on public.budget_settings for all to authenticated
  using (app_private.owns_trip(trip_id)) with check (app_private.owns_trip(trip_id));

-- Plan, findings, versions and generation records: owner may read; every write goes through the API
-- because the backend must recalculate and validate (PR-04).
create policy ai_gen_read   on public.ai_generations     for select to authenticated using (user_id = (select auth.uid()));
create policy days_read     on public.itinerary_days     for select to authenticated using (app_private.owns_trip(trip_id));
create policy items_read    on public.itinerary_items    for select to authenticated using (app_private.owns_trip(trip_id));
create policy warnings_read on public.itinerary_warnings for select to authenticated using (app_private.owns_trip(trip_id));
create policy versions_read on public.itinerary_versions for select to authenticated using (app_private.owns_trip(trip_id));
-- route_cache: RLS on, no policy = no access for browser roles.

-- Second lock: browser roles hold no table privileges in the MVP.
revoke all on table public.destinations, public.data_sources, public.places, public.place_opening_hours,
  public.profiles, public.trips, public.trip_preferences, public.trip_places, public.budget_settings,
  public.ai_generations, public.itinerary_days, public.itinerary_items, public.itinerary_warnings,
  public.itinerary_versions, public.route_cache from anon, authenticated;
-- If direct browser access is ever approved, grant per table, for example:
-- grant select on public.places to authenticated;
