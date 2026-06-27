# MongoDB Atlas setup for ComplySense

This project uses MongoDB Atlas for two things:

- `control_library`: the master reference catalog of compliance controls used by the app.
- `documents`: metadata and extracted text for uploaded evidence/documents.

The backend expects these names through the environment variables in [.env](../.env).

## 1. Create the Atlas cluster

1. Open https://cloud.mongodb.com.
2. Create an account or sign in.
3. Create a new project and name it `complysense`.
4. Create a cluster:
   - Cluster type: `M0 Free` (good for local development)
   - Provider: `AWS`
   - Region: `ap-south-1` or the closest region to you
5. Wait for the cluster to finish provisioning.

## 2. Create a database user

In Atlas, go to Security → Database Access → Add New Database User.

Use these values:

- Username: `complysense_app`
- Password: a strong password you save somewhere safe
- Role: `readWriteAnyDatabase`

## 3. Allow network access

Go to Security → Network Access → Add IP Address.

For local development, add your current public IP address.

If you want the app to be reachable from hosted services later, add `0.0.0.0/0` as well.

## 4. Get the connection string

In Atlas, open your cluster and click Connect → Connect your application.

Copy the Python connection string. It will look like this:

```text
mongodb+srv://complysense_app:<password>@cluster0.xxxxx.mongodb.net/
```

Add the database name and options so it matches the app config:

```text
mongodb+srv://complysense_app:yourpassword@cluster0.xxxxx.mongodb.net/complysense?retryWrites=true&w=majority
```

## 5. Update the app environment variables

In [.env](../.env), set these values:

```env
MONGODB_URI=mongodb+srv://complysense_app:yourpassword@cluster0.xxxxx.mongodb.net/complysense?retryWrites=true&w=majority
MONGODB_DATABASE=complysense
MONGODB_DOCUMENTS_COLLECTION=documents
MONGODB_CONTROL_LIBRARY_COLLECTION=control_library
```

These names match the backend config in [backend/app/config.py](../backend/app/config.py).

## 6. Create the database and collections

In Atlas, open Browse Collections and create the database named `complysense`.

Then create these collections:

- `control_library`
- `documents`

## 7. What goes into each collection

### `control_library`

This collection stores the master control metadata used by the compliance workflow.

The app looks up controls by `control_id`, as implemented in [backend/app/storage/control_library.py](../backend/app/storage/control_library.py).

Example document:

```json
{
  "_id": "DPDP-001",
  "control_id": "DPDP-001",
  "framework": "DPDP Act 2023",
  "title": "Data protection policy",
  "description": "The institution must maintain a documented data protection policy.",
  "evidence_required": ["Approved policy document", "Review records"],
  "review_cycle_days": 365,
  "tags": ["dpdp", "governance"]
}
```

The seed data in [seed.py](../seed.py) uses 105 canonical control IDs across several frameworks, so your `control_library` collection should contain matching documents for those IDs.

### `documents`

This collection stores document metadata and extracted content for evidence uploads.

The app inserts rows into it through [backend/app/storage/documents.py](../backend/app/storage/documents.py).

Example document:

```json
{
  "institution_id": "11111111-2222-3333-4444-555555555555",
  "source_type": "evidence",
  "source_id": "assignment-id-or-document-id",
  "metadata": {
    "filename": "evidence.pdf",
    "content_type": "application/pdf"
  },
  "extracted_text": "Some extracted text from the uploaded file",
  "created_at": "2026-06-27T00:00:00Z",
  "updated_at": "2026-06-27T00:00:00Z"
}
```

## 8. Optional indexes

For better performance, add these indexes:

```javascript
// Atlas UI or mongosh
use complysense

db.control_library.createIndex({ control_id: 1 }, { unique: true })
db.control_library.createIndex({ framework: 1 })
db.documents.createIndex({ institution_id: 1 })
db.documents.createIndex({ source_type: 1 })
db.documents.createIndex({ created_at: -1 })
```

## 9. Quick verification

After setting the variables and starting the backend, verify that MongoDB is reachable:

- The app should start without a MongoDB connection error.
- The health endpoint should report MongoDB as healthy.
- A simple test query should return data from `control_library` if you inserted sample records.

## 10. Beginner note

If you are just starting out, the most important part is to make sure the `control_library` documents exist with the same `control_id` values used by the seeded PostgreSQL assignments. Without that, the compliance workflows will not have the control details they expect.
