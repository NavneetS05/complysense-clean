# Use: Router managing vendor records, risk assessments, and contract reviews.

from __future__ import annotations
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext

router = APIRouter(prefix="/vendors", tags=["vendors"])


class VendorCreate(BaseModel):
    vendor_name: str
    product_name: str | None = None
    vendor_category: str | None = None
    processing_location: str | None = None
    dpa_available: bool = False
    model_training_allowed: bool = False
    contract_expiry_date: str | None = None
    contact_email: str | None = None


class VendorUpdate(BaseModel):
    vendor_name: str | None = None
    product_name: str | None = None
    vendor_category: str | None = None
    processing_location: str | None = None
    dpa_available: bool | None = None
    model_training_allowed: bool | None = None
    contract_expiry_date: str | None = None
    contact_email: str | None = None


@router.get("", summary="List all vendors for the institution")
async def list_vendors(
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_VENDORS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    query = """
        select v.vendor_id, v.vendor_name, v.product_name, v.vendor_category,
               v.processing_location, v.dpa_available, v.model_training_allowed,
               v.contract_expiry_date, v.contact_email, v.created_at,
               vra.risk_level, vra.dpdp_compliant
        from vendors v
        left join (
            select distinct on (vendor_id) vendor_id, risk_level, dpdp_compliant
            from vendor_risk_assessments
            order by vendor_id, created_at desc
        ) vra on vra.vendor_id = v.vendor_id
        where v.institution_id = :inst_id
        order by v.vendor_name asc
    """
    res = await session.execute(text(query), {"inst_id": user_ctx.institution_id})
    rows = res.mappings().all()
    return [
        {
            "vendor_id": str(r["vendor_id"]),
            "vendor_name": r["vendor_name"],
            "product_name": r["product_name"],
            "vendor_category": r["vendor_category"],
            "processing_location": r["processing_location"],
            "dpa_available": r["dpa_available"],
            "model_training_allowed": r["model_training_allowed"],
            "contract_expiry_date": r["contract_expiry_date"].isoformat() if r["contract_expiry_date"] else None,
            "contact_email": r["contact_email"],
            "risk_level": r["risk_level"],
            "dpdp_compliant": r["dpdp_compliant"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


@router.get("/{vendor_id}", summary="Get single vendor with risk assessment history")
async def get_vendor(
    vendor_id: str,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_VENDORS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    vendor_res = await session.execute(
        text("""
            select vendor_id, vendor_name, product_name, vendor_category,
                   processing_location, dpa_available, model_training_allowed,
                   contract_expiry_date, contact_email, created_at
            from vendors
            where vendor_id = :vendor_id and institution_id = :inst_id
        """),
        {"vendor_id": vendor_id, "inst_id": user_ctx.institution_id},
    )
    row = vendor_res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Vendor not found")

    assess_res = await session.execute(
        text("""
            select vendor_risk_id, risk_level, assessment_summary, recommendations, dpdp_compliant, created_at
            from vendor_risk_assessments
            where vendor_id = :vendor_id and institution_id = :inst_id
            order by created_at desc
            limit 5
        """),
        {"vendor_id": vendor_id, "inst_id": user_ctx.institution_id},
    )
    assessments = [
        {
            "vendor_risk_id": str(a["vendor_risk_id"]),
            "risk_level": a["risk_level"],
            "assessment_summary": a["assessment_summary"],
            "recommendations": a["recommendations"],
            "dpdp_compliant": a["dpdp_compliant"],
            "created_at": a["created_at"].isoformat() if a["created_at"] else None,
        }
        for a in assess_res.mappings().all()
    ]

    return {
        "vendor_id": str(row["vendor_id"]),
        "vendor_name": row["vendor_name"],
        "product_name": row["product_name"],
        "vendor_category": row["vendor_category"],
        "processing_location": row["processing_location"],
        "dpa_available": row["dpa_available"],
        "model_training_allowed": row["model_training_allowed"],
        "contract_expiry_date": row["contract_expiry_date"].isoformat() if row["contract_expiry_date"] else None,
        "contact_email": row["contact_email"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "risk_assessments": assessments,
    }


@router.post("", status_code=201, summary="Create a new vendor record")
async def create_vendor(
    payload: VendorCreate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_VENDORS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    query = """
        insert into vendors (
            institution_id, vendor_name, product_name, vendor_category,
            processing_location, dpa_available, model_training_allowed,
            contract_expiry_date, contact_email, created_by
        ) values (
            :inst_id, :vendor_name, :product_name, :vendor_category,
            :processing_location, :dpa_available, :model_training_allowed,
            :contract_expiry_date, :contact_email, :created_by
        ) returning vendor_id, vendor_name
    """
    res = await session.execute(
        text(query),
        {
            "inst_id": user_ctx.institution_id,
            "vendor_name": payload.vendor_name,
            "product_name": payload.product_name,
            "vendor_category": payload.vendor_category,
            "processing_location": payload.processing_location,
            "dpa_available": payload.dpa_available,
            "model_training_allowed": payload.model_training_allowed,
            "contract_expiry_date": payload.contract_expiry_date,
            "contact_email": payload.contact_email,
            "created_by": user_ctx.user_id,
        },
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create vendor")
    return {"vendor_id": str(row["vendor_id"]), "vendor_name": row["vendor_name"]}


@router.patch("/{vendor_id}", summary="Update vendor record")
async def update_vendor(
    vendor_id: str,
    payload: VendorUpdate,
    user_ctx: Annotated[UserContext, Depends(require_permission(PermissionKey.MANAGE_VENDORS))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clauses = ", ".join(f"{k} = :{k}" for k in fields)
    fields["vendor_id"] = vendor_id
    fields["inst_id"] = str(user_ctx.institution_id)
    res = await session.execute(
        text(f"update vendors set {set_clauses}, updated_at = now() where vendor_id = :vendor_id and institution_id = :inst_id returning vendor_id"),
        fields,
    )
    await session.commit()
    row = res.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"vendor_id": str(row["vendor_id"]), "updated": True}
