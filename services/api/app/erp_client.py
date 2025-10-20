import httpx
from .config import settings


async def create_quote(payload: dict) -> dict:
async with httpx.AsyncClient(base_url=settings.erp_base_url, timeout=10) as client:
r = await client.post("/quotes", json=payload, headers={"x-api-key": settings.erp_api_key})
r.raise_for_status()
return r.json()