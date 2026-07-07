# Role Audit - Vendor Reviewer

## Overview

Purpose: manage vendor registry, vendor details, contract/risk review, and expiry tracking.

Frontend route file: `frontend/src/routes/VendorRoutes.tsx`.

Sidebar entries: Vendor Register, Expiry Tracker.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard/Register | `/vendor/dashboard` | `Dashboard.tsx` | Connected to `GET /vendors` |
| New Vendor | `/vendor/vendors/new` | `NewVendor.tsx` | Connected to `POST /vendors` |
| Vendor Detail | `/vendor/vendors/:id` | `VendorDetail.tsx` | Connected to `GET/PATCH /vendors/{vendor_id}` |
| Expiry Tracker | `/vendor/expiry` | `ExpiryTracker.tsx` | Uses vendor expiry data |

## Permissions

Backend permissions:

- `MANAGE_VENDORS`
- `VIEW_VENDORS` exists in enum, but inspected `vendors.py` uses `MANAGE_VENDORS` even for read endpoints.

## Database Usage

PostgreSQL:

- Reads/writes `vendors`.
- Reads `vendor_risk_assessments`.

MongoDB:

- No direct vendor route usage found.

## AI Integration

Implemented:

- Main proxy: `POST /api/v1/ai/vendor/analyze-contract`.
- AI service: `backend/ai_service/routers/vendor.py`.
- Agent: `VendorAgent`.

Partially Implemented:

- Contract analysis AI exists, but persistence of AI assessment results into `vendor_risk_assessments` was not found in the inspected main vendor router.

## Missing Features and Improvements

- Read-only vendor access should use `VIEW_VENDORS` where appropriate.
- Vendor risk assessment creation/update API is missing from the main vendor router.
- Expiry reminders/notifications are not implemented because notifications backend is empty.

