# MongoDB Audit

## Configuration

Implemented:

- `backend/app/mongodb.py` creates `AsyncIOMotorClient`.
- Settings in `backend/app/config.py`:
  - `mongodb_uri`
  - `mongodb_database`
  - `mongodb_documents_collection`
  - `mongodb_control_library_collection`
- Health check: `check_mongodb`.

## Collections

### `documents`

Purpose:

- Store document metadata and extracted text.

Evidence:

- `backend/app/storage/documents.py::DocumentStore`.

Operations:

- Insert: `DocumentStore.save_metadata`.
- Reads/updates/deletes: `DocumentStore.get`, `DocumentStore.update_metadata`, and `DocumentStore.delete`.

Current status: Implemented for helper CRUD and evidence metadata/extracted-text writes.

### `control_library`

Purpose:

- Store control library data.

Evidence:

- `backend/app/storage/control_library.py`.

Current status: Partially Implemented.

Operations:

- Insert/save: `ControlLibraryStore.save_control`.
- Read: `ControlLibraryStore.find_by_control_id` and `ControlLibraryStore.get`.
- Update/delete: `ControlLibraryStore.update_control` and `ControlLibraryStore.delete`.

## Current Usage

Partially Implemented:

- MongoDB health check is wired into `/health/ready`.
- Storage abstractions exist.
- Evidence upload writes MongoDB document metadata and extracted text previews.
- `ControlLibraryStore` is exported but no active route or service caller was found in the inspected code.

## Missing Implementation

- No collection indexes were defined in the inspected code.
- RAG ingestion from uploaded evidence remains separate from the evidence upload path.
