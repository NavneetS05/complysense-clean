# Use: Router for uploading and reviewing evidence files.

from fastapi import APIRouter

router = APIRouter(prefix="/evidence", tags=["evidence"])
