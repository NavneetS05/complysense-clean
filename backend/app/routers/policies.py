# Use: Router for policy draft management and comparison.

from fastapi import APIRouter

router = APIRouter(prefix="/policies", tags=["policies"])
