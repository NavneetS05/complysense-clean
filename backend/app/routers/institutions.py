# Use: Router for managing tenants (institutions).

from fastapi import APIRouter

router = APIRouter(prefix="/institutions", tags=["institutions"])
