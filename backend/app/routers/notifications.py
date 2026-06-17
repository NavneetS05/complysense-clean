# Use: Router retrieving user alerts and notifications.

from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])
