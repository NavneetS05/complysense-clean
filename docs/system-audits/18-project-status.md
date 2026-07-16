# Current Project Status

These percentages are engineering estimates from inspected implementation depth, not test-derived metrics.

| Area | Estimated status |
|---|---:|
| Overall | 68% |
| Frontend | 72% |
| Backend API | 76% |
| Authentication | 84% |
| RBAC | 78% |
| AI service | 64% |
| PostgreSQL | 80% |
| MongoDB | 45% |
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
- Role assumption start workflow.
- Full evidence/RAG indexing pipeline.
- Production document/report generation.
- Automated tests.

## High-Priority Remaining Work

1. Implement notifications API or remove dead UI badges until backed.
2. Add tests for auth, RBAC, tenant scoping, and critical workflows.
3. Resolve frontend lint errors.
4. Complete role assumption start/stop lifecycle with active session integrity checks.
5. Complete evidence-to-RAG ingestion and Supabase KB operational flow.

## Technical Debt

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

1. Notifications and role assumption lifecycle.
2. RAG knowledge/evidence ingestion completion.
3. Report generation pipeline.
4. Test suite and CI.
5. Documentation cleanup.
