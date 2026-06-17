# Use: Router managing user creation and lifecycle operations.

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])
