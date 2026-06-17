# Use: Router for querying and retrieving the central audit trail logs.

from fastapi import APIRouter

router = APIRouter(prefix="/audit", tags=["audit"])
