-- Downgrade 0005: drop policies, disable RLS, drop the ownership function and schema.
do $$ declare r record; begin
  for r in select policyname, tablename from pg_policies where schemaname = 'public' loop
    execute format('drop policy if exists %I on public.%I', r.policyname, r.tablename);
  end loop;
  for r in select tablename from pg_tables where schemaname = 'public' and tablename <> 'alembic_version' loop
    execute format('alter table public.%I disable row level security', r.tablename);
  end loop;
end $$;
drop function if exists app_private.owns_trip(uuid);
-- app_private is kept if Alembic's version table lives there; otherwise it can be dropped by hand.
