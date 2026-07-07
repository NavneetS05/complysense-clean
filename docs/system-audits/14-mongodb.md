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
- Reads/updates/deletes: not found in inspected route layer.

Current status: Partially Implemented.

### `control_library`

Purpose:

- Store control library data.

Evidence:

- `backend/app/storage/control_library.py`.

Current status: Partially Implemented.

## Current Usage

Partially Implemented:

- MongoDB health check is wired into `/health/ready`.
- Storage abstractions exist.
- Clear frontend-to-route-to-MongoDB workflows are limited in inspected code.

## Missing Implementation

- No collection indexes were defined in the inspected code.
- No complete CRUD API for documents collection was found.
- Evidence upload writes local file metadata to PostgreSQL but does not visibly write extracted text to MongoDB in `backend/app/routers/evidence.py`.

