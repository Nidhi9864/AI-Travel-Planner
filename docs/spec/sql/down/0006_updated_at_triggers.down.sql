-- Downgrade 0006: remove the updated_at triggers (privilege revokes are left in place; they are harmless).
do $$ declare r record; begin
  for r in select event_object_table as t, trigger_name as n from information_schema.triggers
           where trigger_schema = 'public' and trigger_name like 'trg_%_updated_at' loop
    execute format('drop trigger if exists %I on public.%I', r.n, r.t);
  end loop;
end $$;
