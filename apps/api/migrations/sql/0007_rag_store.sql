-- Migration 0007_rag_store (MVP, Amendment A1). Vector store for the RAG pipeline, item citations and retrieval record.
-- Source of truth for the schema (IMD-01). Executed by apps/api/migrations/versions/0007_rag_store.py.
-- Conventions: uuid keys from gen_random_uuid(); timestamptz; enumerations as text + CHECK equal to the API contracts.
-- Writers: MOD-B18 (app/rag/repository.py) writes rag_documents and rag_chunks; MOD-B08 writes itinerary_items.source_chunk_ids;
-- MOD-B06 writes ai_generations.retrieval_mode, embedding_model_id and retrieval_ms.
-- Needs the pgvector extension: available on Amazon RDS for PostgreSQL 16, on the Supabase local stack and in the
-- pgvector/pgvector:pg16 test image (IMD-115). On RDS the migration role must be allowed to create extensions (the master user is).

create extension if not exists vector;

create table public.rag_documents (
  id              uuid primary key default gen_random_uuid(),
  destination_id  uuid not null references public.destinations(id) on delete cascade,
  kind            text not null check (kind in ('place','guide')),
  place_id        uuid references public.places(id) on delete cascade,     -- set exactly when kind = 'place'
  source_id       uuid not null references public.data_sources(id) on delete restrict,
  doc_key         text not null unique
                  check (char_length(doc_key) between 1 and 200),          -- 'place:<uuid>' or 'guide:<slug>/<file stem>'
  title           text not null check (char_length(title) between 1 and 200),
  url             text,
  retrieved_on    date,
  content_sha256  text not null check (content_sha256 ~ '^[0-9a-f]{64}$'),
  is_active       boolean not null default true,                           -- false = removed from the corpus; never deleted
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  check ((kind = 'place') = (place_id is not null))
);
create index ix_rag_documents_dest on public.rag_documents (destination_id, kind) where is_active;
create index ix_rag_documents_place on public.rag_documents (place_id) where place_id is not null;

create table public.rag_chunks (
  id                  uuid primary key default gen_random_uuid(),
  document_id         uuid not null references public.rag_documents(id) on delete cascade,
  chunk_index         smallint not null check (chunk_index >= 0),
  heading             text check (char_length(heading) <= 200),
  content             text not null check (char_length(content) between 1 and 1200),
  content_sha256      text not null check (content_sha256 ~ '^[0-9a-f]{64}$'),
  token_estimate      integer not null check (token_estimate > 0),
  embedding           vector(768),                                         -- null until embedded (IMD-106)
  embedding_model_id  text check (char_length(embedding_model_id) between 1 and 100),
  embedded_at         timestamptz,
  is_active           boolean not null default true,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  unique (document_id, chunk_index),
  check ((embedding is null) = (embedding_model_id is null)),
  check ((embedding is null) = (embedded_at is null))
);
create index ix_rag_chunks_document on public.rag_chunks (document_id);
create index ix_rag_chunks_model on public.rag_chunks (embedding_model_id) where is_active and embedding is not null;
-- No approximate-nearest-neighbour index: exact cosine search while the corpus stays under 5,000 active chunks (IMD-107).

alter table public.itinerary_items
  add column source_chunk_ids uuid[] not null default '{}'
  check (cardinality(source_chunk_ids) <= 3);

alter table public.ai_generations
  add column retrieval_mode text check (retrieval_mode in ('vector','lexical_fallback')),
  add column embedding_model_id text check (char_length(embedding_model_id) between 1 and 100),
  add column retrieval_ms integer check (retrieval_ms >= 0);

alter table public.rag_documents enable row level security;
alter table public.rag_chunks    enable row level security;
-- RLS on, no policy: browser roles have no access; the API connects as the owner (OD-18 resolved, IMD-100).
revoke all on table public.rag_documents, public.rag_chunks from anon, authenticated;

select public.add_updated_at_triggers();
