# Role Audit - Vendor Reviewer

## Overview

Purpose: manage vendor registry, vendor details, contract/risk review, and expiry tracking.

Frontend route file: `frontend/src/routes/VendorRoutes.tsx`.

Sidebar entries: Vendor Register, Expiry Tracker.

Current status: Implemented for registry and risk-assessment write paths; notifications remain out of scope.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard/Register | `/vendor/dashboard` | `Dashboard.tsx` | Connected to `GET /vendors` |
| New Vendor | `/vendor/vendors/new` | `NewVendor.tsx` | Connected to `POST /vendors` |
| Vendor Detail | `/vendor/vendors/:id` | `VendorDetail.tsx` | Connected to `GET/PATCH /vendors/{vendor_id}` |
| Expiry Tracker | `/vendor/expiry` | `ExpiryTracker.tsx` | Uses vendor expiry data |

## Permissions

Backend permissions:

- `VIEW_VENDORS` for vendor list/detail reads.
- `MANAGE_VENDORS` for vendor create/update, risk assessment writes, and AI contract analysis.

## Database Usage

PostgreSQL:

- Reads/writes `vendors`.
- Reads/writes `vendor_risk_assessments`.

MongoDB:

- The AI vendor proxy stores analyzed contract text in `vendor_contracts` as non-fatal supporting metadata.

## AI Integration

Implemented:

- Main proxy: `POST /api/v1/ai/vendor/analyze-contract`.
- AI service: `backend/ai_service/routers/vendor.py`.
- Agent: `VendorAgent`.
- The main proxy persists returned AI analysis into `vendor_risk_assessments` and writes `vendor_risk_assessment_created` to `audit_logs`.

## Missing Features and Improvements

- `backend/app/routers/vendors.py::upsert_vendor_risk_assessment` provides a create/update write path for manual risk assessments.
- Expiry reminders/notifications are not implemented because notifications backend is empty.
