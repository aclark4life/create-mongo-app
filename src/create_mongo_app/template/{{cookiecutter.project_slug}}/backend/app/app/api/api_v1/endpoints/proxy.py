from typing import Any
from pydantic import AnyHttpUrl
from fastapi import APIRouter, Depends, HTTPException, Request, Response
import httpx

from app import models
from app.api import deps
from app.core.config import settings


router = APIRouter()

"""
A proxy for the frontend client when hitting cors issues with axios requests. Adjust as required.

Security notes:
- Requests are only forwarded to hosts explicitly listed in ``settings.PROXY_ALLOWED_HOSTS``
  (deny-by-default) to prevent Server-Side Request Forgery (e.g. reaching cloud metadata
  endpoints or internal-only services).
- The caller's ``Authorization`` header is NOT forwarded, so the app bearer token is never
  leaked to an upstream host.
- Upstream/connection errors are returned as a generic message so internal network details
  are not disclosed to the client.
"""


def _validate_target(path: AnyHttpUrl) -> None:
    """Reject any target host not on the allowlist."""
    if not settings.PROXY_ALLOWED_HOSTS or path.host not in settings.PROXY_ALLOWED_HOSTS:
        raise HTTPException(status_code=403, detail="Proxy target is not permitted.")


@router.post("/{path:path}")
async def proxy_post_request(
    *,
    path: AnyHttpUrl,
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    _validate_target(path)
    try:
        data = await request.json()
        headers = {"Content-Type": request.headers.get("Content-Type", "application/json")}
        async with httpx.AsyncClient() as client:
            proxy = await client.post(f"{path}", headers=headers, json=data)
        return Response(content=proxy.content, status_code=proxy.status_code)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream request failed.")


@router.get("/{path:path}")
async def proxy_get_request(
    *,
    path: AnyHttpUrl,
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    _validate_target(path)
    try:
        headers = {
            "Content-Type": request.headers.get("Content-Type", "application/x-www-form-urlencoded"),
        }
        async with httpx.AsyncClient() as client:
            proxy = await client.get(f"{path}", headers=headers)
        return Response(content=proxy.content, status_code=proxy.status_code)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream request failed.")
