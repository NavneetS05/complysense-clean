# Use: Helper module to build a live operational database snapshot for grounding AI queries.

from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def build_institution_operational_context(session: AsyncSession, institution_id: str) -> str:
    """
    Queries live PostgreSQL database tables (registered policies, pending assessments,
    compliance gaps, remediation tasks, evidence queue) and builds a formatted
    operational snapshot to ground AI queries.
    """
    sections: list[str] = []

    # 1. Registered Policies
    try:
        policies_res = await session.execute(
            text(
                """
                select policy_name, version_number, policy_status, related_control_id, created_at
                from generated_policies
                where institution_id = :inst_id
                order by created_at desc
                limit 15
                """
            ),
            {"inst_id": institution_id},
        )
        p_rows = policies_res.mappings().all()
        if p_rows:
            p_lines = [
                f"- '{r['policy_name']}' (Version: v{r['version_number']}, Status: {r['policy_status'].upper()}, Control: {r['related_control_id'] or 'General'})"
                for r in p_rows
            ]
            sections.append("REGISTERED INSTITUTION POLICIES:\n" + "\n".join(p_lines))
        else:
            sections.append("REGISTERED INSTITUTION POLICIES: No custom policies registered yet.")
    except Exception:
        pass

    # 2. Active & Pending Assessments
    try:
        assess_res = await session.execute(
            text(
                """
                select title, framework_name, status, target_completion_date
                from assessments
                where institution_id = :inst_id
                order by created_at desc
                limit 10
                """
            ),
            {"inst_id": institution_id},
        )
        a_rows = assess_res.mappings().all()
        if a_rows:
            a_lines = [
                f"- '{r['title']}' (Framework: {r['framework_name']}, Status: {r['status'].upper()}, Due: {r['target_completion_date'] or 'N/A'})"
                for r in a_rows
            ]
            sections.append("PENDING & ACTIVE ASSESSMENTS:\n" + "\n".join(a_lines))
        else:
            sections.append("PENDING & ACTIVE ASSESSMENTS: No active assessments currently pending.")
    except Exception:
        pass

    # 3. Active Compliance Gaps
    try:
        gaps_res = await session.execute(
            text(
                """
                select control_id, framework_name, severity, title, remediation_status
                from compliance_gaps
                where institution_id = :inst_id and remediation_status in ('open', 'in_progress')
                order by case severity when 'critical' then 0 when 'high' then 1 when 'medium' then 2 else 3 end
                limit 15
                """
            ),
            {"inst_id": institution_id},
        )
        g_rows = gaps_res.mappings().all()
        if g_rows:
            g_lines = [
                f"- [{r['severity'].upper()}] Control {r['control_id']} ({r['framework_name']}): {r['title']} (Status: {r['remediation_status']})"
                for r in g_rows
            ]
            sections.append("OPEN COMPLIANCE GAPS:\n" + "\n".join(g_lines))
        else:
            sections.append("OPEN COMPLIANCE GAPS: None currently open.")
    except Exception:
        pass

    # 4. Remediation Tasks
    try:
        tasks_res = await session.execute(
            text(
                """
                select title, priority, status, due_date
                from remediation_tasks
                where institution_id = :inst_id and status != 'completed'
                order by created_at desc
                limit 10
                """
            ),
            {"inst_id": institution_id},
        )
        t_rows = tasks_res.mappings().all()
        if t_rows:
            t_lines = [
                f"- Task: '{r['title']}' (Priority: {r['priority'].upper()}, Status: {r['status']}, Due: {r['due_date'] or 'N/A'})"
                for r in t_rows
            ]
            sections.append("PENDING REMEDIATION TASKS:\n" + "\n".join(t_lines))
    except Exception:
        pass

    return "\n\n".join(sections)
