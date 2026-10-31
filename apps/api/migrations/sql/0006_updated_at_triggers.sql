-- Migration 0006_updated_at_triggers (MVP). Attach updated_at triggers; revoke helper functions and the Alembic version table from browser roles.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0006_updated_at_triggers.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

select public.add_updated_at_triggers();
-- Functions in the public schema may be callable by the browser roles through the Supabase API (Unverified; confirm at setup).
-- Only the migration owner needs to call these two; the triggers they create keep working.
revoke execute on function public.set_updated_at() from public, anon, authenticated;
revoke execute on function public.add_updated_at_triggers() from public, anon, authenticated;
-- Alembic keeps its version table in public; browser roles must not read or change it.
do $$ begin
  if to_regclass('public.alembic_version') is not null then
    revoke all on table public.alembic_version from anon, authenticated;
  end if;
end $$;
