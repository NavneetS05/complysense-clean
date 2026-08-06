# Use: Orchestrates the full re-indexing pipeline (Markdown → Chunk → Embed → FAISS + BM25).
# Updated: removed app.* imports; uses decoupled db/mongo clients; structured logging.

import json
import time
from pathlib import Path
from typing import Any, Dict

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger
from ai_service.rag.indexing.markdown_loader import MarkdownLoader
from ai_service.rag.indexing.atomic_chunker import AtomicChunker
from ai_service.rag.indexing.embeddings import EmbeddingsGenerator
from ai_service.rag.indexing.faiss_store import FAISSIndexStore
from ai_service.rag.indexing.bm25_store import BM25IndexStore

logger = StructuredLogger("ai_service.rag.indexing.index_builder")


class IndexBuilder:
    """
    Orchestrates the full re-indexing pipeline:
    1. Load latest regulatory Markdown files (local / Supabase fallback).
    2. Parse nodes and chunk text (AtomicChunker).
    3. Include user-uploaded documents from MongoDB (best-effort, failures are non-fatal).
    4. Generate dense embeddings (BAAI/bge-m3 via EmbeddingsGenerator singleton).
    5. Build and persist FAISS index.
    6. Build and persist BM25 index.
    7. Write an audit_log row to PostgreSQL (best-effort, failures are non-fatal).
    """

    def __init__(self) -> None:
        self.settings = get_ai_settings()

        # Knowledge base directory — sits under ai_service/knowledge_base/
        self.kb_dir = Path(__file__).resolve().parents[2] / "knowledge_base"

        # Resolve vectorstore path (always relative to ai_service root for clarity)
        vs_setting = self.settings.vectorstore_path
        if Path(vs_setting).is_absolute():
            self.vs_path = Path(vs_setting)
        else:
            self.vs_path = Path(__file__).resolve().parents[2] / "vectorstore"

        # Shared instances — embeddings model loaded once here
        self.embeddings = EmbeddingsGenerator(model_name=self.settings.embeddings_model)
        self.faiss_store = FAISSIndexStore(str(self.vs_path))
        self.bm25_store = BM25IndexStore(str(self.vs_path))

    def is_built(self) -> bool:
        """Returns True if both index files exist on disk."""
        return self.faiss_store.is_built()

    async def run_reindex_pipeline(
        self,
        triggered_by: str = "startup",
        user_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Asynchronous re-indexing pipeline entry point.
        Non-fatal failures (MongoDB, audit log) are logged and skipped so the
        primary indexing always completes if the knowledge base is reachable.
        """
        start_time = time.time()
        logger.info("index_builder.pipeline_start", triggered_by=triggered_by)

        # ── Step 1: Load framework Markdown files ─────────────────────────────
        loader = MarkdownLoader(use_supabase=True)
        fw_docs = loader.load_documents()
        frameworks_indexed = list({d["framework"] for d in fw_docs})
        logger.info("index_builder.frameworks_loaded", count=len(fw_docs))

        all_chunks = []
        chunker = AtomicChunker(
            target_tokens=500,
            overlap_tokens=100,
            max_tokens=600,
        )

        # ── Step 2: Chunk framework docs via structured nodes ─────────────────
        for doc in fw_docs:
            nodes = doc.get("nodes")
            doc_meta = doc.get("metadata", {})
            if nodes:
                # Prefer structured path (frontmatter + heading nodes)
                if "framework" not in doc_meta:
                    doc_meta = dict(doc_meta)
                    doc_meta["framework"] = doc.get("framework", doc["document_name"])
                chunks = chunker.split_document_nodes(
                    document_name=doc["document_name"],
                    nodes=nodes,
                    doc_metadata=doc_meta,
                )
            else:
                # Fallback: treat content as flat text
                chunks = chunker.split_document(
                    doc.get("content", ""),
                    metadata={
                        "source_file": doc.get("file_name", doc.get("document_name", "unknown.md")),
                        "framework": doc.get("framework", "Unknown Framework"),
                    },
                )
            all_chunks.extend(chunks)

        # ── Step 3: Include user-uploaded documents from MongoDB (best-effort) ─
        await self._ingest_mongo_documents(chunker, all_chunks)

        if not all_chunks:
            logger.warning("index_builder.no_chunks", detail="No chunks produced — skipping build.")
            return {
                "status": "skipped",
                "reason": "no_chunks",
                "frameworks_indexed": frameworks_indexed,
                "chunk_count": 0,
                "duration_seconds": round(time.time() - start_time, 2),
            }

        # ── Step 4: Generate dense embeddings ─────────────────────────────────
        logger.info("index_builder.generating_embeddings", chunk_count=len(all_chunks))
        texts = [c.get("text", "") for c in all_chunks]
        embeddings = self.embeddings.embed_documents(texts)

        # ── Step 5: Build FAISS + BM25 ────────────────────────────────────────
        self.faiss_store.build_and_save(all_chunks, embeddings)
        self.bm25_store.build_and_save(all_chunks)

        duration = round(time.time() - start_time, 2)
        logger.info(
            "index_builder.pipeline_done",
            chunk_count=len(all_chunks),
            duration_seconds=duration,
        )

        # ── Step 6: Audit log to PostgreSQL (best-effort, non-fatal) ──────────
        await self._write_audit_log(
            triggered_by=triggered_by,
            user_id=user_id,
            frameworks_indexed=frameworks_indexed,
            chunk_count=len(all_chunks),
            duration=duration,
        )

        return {
            "status": "success",
            "frameworks_indexed": frameworks_indexed,
            "chunk_count": len(all_chunks),
            "duration_seconds": duration,
        }

    # ── Private Helpers ────────────────────────────────────────────────────────

    async def _ingest_mongo_documents(
        self,
        chunker: AtomicChunker,
        all_chunks: list,
    ) -> None:
        """
        Reads user-uploaded evidence documents from MongoDB and appends their chunks.
        Non-fatal: any exception is caught and logged.
        """
        try:
            from ai_service.utils.mongodb import get_mongo_database

            db = get_mongo_database()
            if db is None:
                logger.warning(
                    "index_builder.mongo_unavailable",
                    detail="Skipping user-document indexing.",
                )
                return

            collection_name = self.settings.mongodb_documents_collection
            cursor = db[collection_name].find(
                {},
                projection={
                    "combined_markdown": 1,
                    "extracted_text": 1,
                    "metadata": 1,
                    "institution_id": 1,
                    "uploaded_by_role": 1,
                },
            )
            count = 0
            async for doc in cursor:
                content = doc.get("combined_markdown") or doc.get("extracted_text")
                if not content:
                    continue

                doc_meta = doc.get("metadata", {})
                filename = doc_meta.get("filename", "user_document")

                metadata = {
                    "source": "user_upload",
                    "framework": "User Document",
                    "source_file": filename,
                    "document_name": filename,
                    "institution_id": str(doc.get("institution_id", "")),
                    "uploaded_by_role": doc.get("uploaded_by_role") or doc_meta.get("uploaded_by_role") or "unknown",
                }

                doc_chunks = chunker.split_document(content, metadata)
                all_chunks.extend(doc_chunks)
                count += 1

            logger.info("index_builder.mongo_docs_ingested", count=count)
        except Exception as exc:
            logger.warning(
                "index_builder.mongo_ingest_failed",
                error=str(exc),
                detail="Continuing without user-uploaded documents.",
            )

    async def _write_audit_log(
        self,
        triggered_by: str,
        user_id: str | None,
        frameworks_indexed: list,
        chunk_count: int,
        duration: float,
    ) -> None:
        """
        Writes a rag_reindexed row to audit_logs in PostgreSQL.
        Non-fatal: any exception is caught and logged.
        """
        try:
            from ai_service.utils.database import get_async_session_factory
            from sqlalchemy import text

            factory = get_async_session_factory()
            if factory is None:
                logger.warning(
                    "index_builder.audit_log_skipped",
                    detail="DATABASE_URL not configured.",
                )
                return

            action_details = json.dumps(
                {
                    "triggered_by": triggered_by,
                    "frameworks_indexed": frameworks_indexed,
                    "chunk_count": chunk_count,
                    "duration_seconds": duration,
                    "embedding_model": self.settings.embeddings_model,
                }
            )

            query = text(
                """
                INSERT INTO audit_logs (
                    institution_id, user_id, active_role_id, assumed_role_session_id,
                    action_type, entity_type, entity_id, action_details, ip_address, created_at
                ) VALUES (
                    NULL, :user_id, NULL, NULL,
                    'rag_reindexed', 'knowledge_base', NULL, :action_details, NULL, now()
                )
                """
            )
            async with factory() as session:
                await session.execute(
                    query,
                    {"user_id": user_id, "action_details": action_details},
                )
                await session.commit()

            logger.info("index_builder.audit_log_written")
        except Exception as exc:
            logger.warning(
                "index_builder.audit_log_failed",
                error=str(exc),
            )
