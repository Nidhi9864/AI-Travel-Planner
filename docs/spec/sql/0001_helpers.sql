-- Migration 0001_helpers (MVP). Helper functions for updated_at triggers.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0001_helpers.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts;
-- money as numeric with a currency code (API serialises it as a two-decimal string, IMD-05).

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Creates (or re-creates) the updated_at trigger on every public table that has an updated_at column.
create or replace function public.add_updated_at_triggers()
returns void
language plpgsql
as $$
declare r record;
begin
  for r in
    select c.table_name
    from information_schema.columns c
    join information_schema.tables t
      on t.table_schema = c.table_schema and t.table_name = c.table_name and t.table_type = 'BASE TABLE'
    where c.table_schema = 'public' and c.column_name = 'updated_at'
  loop
    execute format(
      'create or replace trigger trg_%1$s_updated_at before update on public.%1$I
         for each row execute function public.set_updated_at()', r.table_name);
  end loop;
end;
$$;
