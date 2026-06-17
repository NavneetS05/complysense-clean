# Use: Router for managing compliance calendar events and deadlines.

from fastapi import APIRouter

router = APIRouter(prefix="/calendar", tags=["calendar"])
