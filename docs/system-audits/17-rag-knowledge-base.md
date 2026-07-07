# RAG and Knowledge Base Audit

## Current Architecture

Implemented:

- Markdown knowledge base directory exists under `backend/ai_service/rag/knowledge_base`.
- Indexing modules:
  - `markdown_loader.py`
  - `atomic_chunker.py`
  - `metadata_builder.py` appears in `ai_service-pr` but not current `backend/ai_service` listing from initial scan
  - `embeddings.py`
  - `faiss_store.py`
  - `bm25_store.py`
  - `index_builder.py`
- Retrieval modules:
  - `hybrid_retriever.py`
  - `rrf.py`
  - `query_classifier.py`
  - `confidence.py`
  - `cross_reference.py`
  - `context_builder.py`
- Generation modules:
  - `prompt_builder.py`
  - `conversation.py`
  - `response_validator.py`

Current status: Partially Implemented.

## Supabase Storage Usage

Implemented:

- Supabase client and knowledge bucket config exist.
- Health check calls `supabase.storage.get_bucket`.

Partially Implemented:

- Complete route-level workflow for uploading Markdown knowledge files to Supabase and triggering reindex was not confirmed in inspected main app routers.

## Ingestion Pipeline

Implemented:

- AI service startup uses `IndexBuilder`.
- If indexes exist, retriever reloads.
- If missing or invalid, startup attempts rebuild.
- Reindex admin route exists in AI service admin router.

Risks:

- Startup rebuild can make service readiness slow.
- Local vectorstore path is ignored by `.gitignore`, so deployment must provide a build/rebuild process.

## Chunking and Metadata

Implemented:

- Atomic chunker and markdown loader exist.
- Retrieved chunks carry metadata under `meta` or legacy `metadata` according to `BaseAgent`.

Partially Implemented:

- Cross-reference injection exists, but coverage depends on metadata quality.

## Embeddings and Vector Search

Implemented:

- Embeddings model setting defaults to `BAAI/bge-m3`.
- FAISS store exists.
- BM25 store exists.
- Hybrid retrieval uses reciprocal rank fusion.

## Retrieval

Implemented:

- `HybridRetriever.retrieve(query_text, role, institution_id, limit=7)` is called by `BaseAgent`.
- Role and institution are passed into retrieval.

Needs review:

- Confirm whether role/institution filters are enforced inside retriever stores for all document types.

## Response Generation and Validation

Implemented:

- Prompt builder combines base system prompt, role context, retrieved context, history, and task query.
- LLM call uses Gemini.
- Response validator checks generated output.
- Citations are extracted from retrieved chunk framework metadata.

Partially Implemented:

- Citations are framework names, not precise document/page/chunk references.

## Missing Implementation

- No clear production admin UI for knowledge base management found.
- No full evidence document extraction/indexing path confirmed.
- No cache invalidation or distributed index strategy found.

