-- Down migration 0007_rag_store. Used by the CI round trip on plain PostgreSQL; production migrations are forward only.
alter table public.ai_generations drop column if exists retrieval_ms;
alter table public.ai_generations drop column if exists embedding_model_id;
alter table public.ai_generations drop column if exists retrieval_mode;
alter table public.itinerary_items drop column if exists source_chunk_ids;
drop table if exists public.rag_chunks;
drop table if exists public.rag_documents;
-- The extension is left installed: other databases on the same server may use it, and Supabase manages its own copy.
