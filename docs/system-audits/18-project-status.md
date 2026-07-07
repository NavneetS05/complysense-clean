# Current Project Status

These percentages are engineering estimates from inspected implementation depth, not test-derived metrics.

| Area | Estimated status |
|---|---:|
| Overall | 62% |
| Frontend | 68% |
| Backend API | 70% |
| Authentication | 72% |
| RBAC | 78% |
| AI service | 58% |
| PostgreSQL | 75% |
| MongoDB | 35% |
| RAG | 60% |
| Knowledge base management | 40% |

## Major Completed Modules

- Main FastAPI app composition and route registration.
- React route tree and role-based dashboards.
- JWT plus server-side session validation.
- RBAC permission loading and route guards.
- Controls, tasks, incidents, vendors, policies, assessments, gaps, and audit report records.
- AI service skeleton with RAG orchestration.
- PostgreSQL schema for major GRC entities.

## Major Incomplete Modules

- Notifications backend.
- Email verification.
- Auth token cookie hardening.
- Role assumption start workflow.
- Vendor risk assessment persistence from AI outputs.
- Evidence scanning/extraction/indexing.
- MongoDB CRUD usage beyond helper abstractions.
- Production document/report generation.
- Automated tests.

## High-Priority Remaining Work

1. Fix login lockout duration and response shape.
2. Move refresh token out of `localStorage` or introduce secure cookie flow.
3. Align AI permissions between main proxy and AI service.
4. Harden evidence upload: size, MIME/extension allowlist, scanning hook, streaming write.
5. Implement notifications API or remove dead UI badges until backed.
6. Add tests for auth, RBAC, tenant scoping, and critical workflows.
7. Resolve frontend lint errors.
8. Complete role assumption start/stop lifecycle.

## Technical Debt

- Duplicate route exports in `frontend/src/routes/index.tsx` and `AppRouter.tsx`.
- AI microservice imports main app auth/RBAC modules, coupling service boundaries.
- Some backend routers write SQL directly instead of using repositories.
- Some comments/docs contain mojibake and outdated OpenAI references.
- Report generation is currently record generation plus synthetic file paths/simple HTML.

## Architecture Concerns

- Direct AI service exposure should be avoided or tightly controlled; browser traffic should prefer the main API proxy.
- MongoDB is configured but underused; clarify whether it is required for MVP.
- RAG vectorstore lifecycle needs deployment/runbook clarity.
- Audit logging is important but inconsistent across non-auth CRUD operations.

## Recommended Implementation Order

1. Security/auth fixes.
2. RBAC/AI permission alignment.
3. Evidence upload hardening.
4. Notifications and role assumption lifecycle.
5. RAG knowledge/evidence ingestion completion.
6. Report generation pipeline.
7. Test suite and CI.
8. Documentation cleanup.

