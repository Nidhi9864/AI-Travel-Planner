-- Applied by tests/fixtures/db.py ONLY when schema auth does not exist (plain PostgreSQL in CI). Never on Supabase.
-- LOCAL TEST DOUBLE ONLY. NEVER RUN THIS ON SUPABASE: these objects already exist there.
begin;
do $$ begin
  if exists (select 1 from pg_namespace where nspname = 'auth') then
    raise exception 'Schema auth already exists. This looks like a Supabase database.';
  end if;
end $$;
create schema auth;
create table auth.users (id uuid primary key default gen_random_uuid(), email text);
do $$ begin
  if not exists (select 1 from pg_roles where rolname='anon') then create role anon nologin; end if;
  if not exists (select 1 from pg_roles where rolname='authenticated') then
    create role authenticated nologin; end if;
end $$;
create or replace function auth.uid() returns uuid language sql stable
as $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
grant usage on schema auth to authenticated, anon;
grant execute on function auth.uid() to authenticated, anon;
commit;
