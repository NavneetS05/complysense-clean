# Use: Proxy layer to forward requests to the decoupled AI microservice with error mapping.

import httpx
from fastapi import HTTPException
from app.config import get_settings
# from app.utils.logger import logger  # If there is a logger in app, let's look for it. We'll use a generic print or imports if not. Let's see if we can import logging.
import logging

log = logging.getLogger("app.routers.ai.proxy")

async def forward_to_ai_service(path: str, payload: dict, auth_header: str | None) -> dict:
    settings = get_settings()
    url = f"{settings.ai_service_url.rstrip('/')}{path}"
    
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 401 or response.status_code == 403:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Unauthorized"))
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Too many requests. Please wait 30 seconds.")
            elif response.status_code == 503:
                raise HTTPException(status_code=503, detail="AI service is starting up. Try again in a moment.")
            elif response.status_code >= 500:
                raise HTTPException(status_code=502, detail="Something went wrong. Please try again.")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Response took too long. Try with a shorter input.")
        except httpx.RequestError as exc:
            log.error(f"Failed to connect to AI service at {url}: {exc}")
            raise HTTPException(status_code=503, detail="AI service is currently unavailable. Please try again later.")
