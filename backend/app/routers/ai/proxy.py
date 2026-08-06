# Use: Proxy layer to forward requests to the decoupled AI microservice with error mapping and robust JSON extraction.

import httpx
import json
import re
from fastapi import HTTPException
from app.config import get_settings
import logging

log = logging.getLogger("app.routers.ai.proxy")


def _extract_json_from_text(text: str):
    """Attempt to extract a JSON object/array from freeform assistant text.

    Strategies:
    - Direct json.loads()
    - Extract fenced ```json``` or ``` blocks
    - Find the first '{' or '[' and try to parse a balanced slice heuristically
    Returns the parsed object on success or None on failure.
    """
    if not text:
        return None

    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fenced code block
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass

    # Find first JSON-ish start
    starts = [i for i in (text.find('{'), text.find('[')) if i >= 0]
    if not starts:
        return None
    first = min(starts)
    candidate = text[first:]

    # Heuristic: try progressively trimming to the last brace
    last_curly = candidate.rfind('}')
    last_square = candidate.rfind(']')
    last = max(last_curly, last_square)
    if last > 0:
        candidate2 = candidate[: last + 1]
        try:
            return json.loads(candidate2)
        except Exception:
            pass

    # As a last resort, try to find JSON-like substrings via regex and parse
    json_like = re.findall(r"(\{[\s\S]{10,}\}|\[[\s\S]{10,}\])", text)
    for piece in json_like:
        try:
            return json.loads(piece)
        except Exception:
            continue

    return None


async def forward_to_ai_service(path: str, payload: dict, auth_header: str | None) -> dict:
    settings = get_settings()
    url = f"{settings.ai_service_url.rstrip('/')}" + path

    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in (401, 403):
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Unauthorized"))
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Too many requests. Please wait 30 seconds.")
            elif response.status_code == 503:
                raise HTTPException(status_code=503, detail="AI service is starting up. Try again in a moment.")
            elif response.status_code >= 500:
                raise HTTPException(status_code=502, detail="Something went wrong. Please try again.")

            response.raise_for_status()
            resp_json = response.json()

            # If the AI service returned a textual assistant response, attempt to extract JSON
            ai_text = None
            if isinstance(resp_json, dict):
                # Common keys: 'response', 'answer', 'text'
                for k in ("response", "answer", "text", "result"):
                    if k in resp_json and isinstance(resp_json[k], str):
                        ai_text = resp_json[k]
                        break

            if ai_text:
                parsed = _extract_json_from_text(ai_text)
                if parsed is not None:
                    # attach parsed JSON under a stable key while keeping original text
                    resp_json["response_json"] = parsed

            return resp_json

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Response took too long. Try with a shorter input.")
        except httpx.RequestError as exc:
            log.error(f"Failed to connect to AI service at {url}: {exc}")
            raise HTTPException(status_code=503, detail="AI service is currently unavailable. Please try again later.")
