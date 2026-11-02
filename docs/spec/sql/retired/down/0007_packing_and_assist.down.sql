-- Downgrade 0007 (destroys packing lists and the assist-call log; local and staging only).
drop table if exists public.ai_assist_calls, public.checklist_items cascade;
