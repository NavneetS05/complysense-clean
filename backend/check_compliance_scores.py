import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("select i.institution_id, i.institution_name, cr.compliance_percentage, cr.framework_name, cr.created_at from institutions i left join compliance_results cr on cr.institution_id = i.institution_id order by i.institution_name"))
        rows = res.mappings().all()
        print("COMPLIANCE RESULTS IN DB:")
        for r in rows:
            print(f"Inst: {r['institution_name']} | %: {r['compliance_percentage']} | Framework: {r['framework_name']} | Created: {r['created_at']}")

        # Also check control_assignments count per status per institution
        res_ctrl = await session.execute(text("select i.institution_name, ca.status, count(*) as cnt from institutions i left join control_assignments ca on ca.institution_id = i.institution_id group by i.institution_name, ca.status"))
        rows_ctrl = res_ctrl.mappings().all()
        print("\nCONTROL ASSIGNMENTS BY STATUS:")
        for r in rows_ctrl:
            print(f"Inst: {r['institution_name']} | Status: {r['status']} | Count: {r['cnt']}")

if __name__ == '__main__':
    asyncio.run(main())
