# Use: Router managing IT security incident command center, timelines, and reporting.

from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["incidents"])
