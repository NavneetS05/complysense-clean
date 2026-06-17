# Use: Router managing control assignments and their operational status.

from fastapi import APIRouter

router = APIRouter(prefix="/controls", tags=["controls"])
