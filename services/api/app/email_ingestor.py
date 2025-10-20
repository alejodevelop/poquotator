import httpx
from .config import settings
from .nlp.extract import extract_structured


async def pull_new_emails(limit: int = 10):
# MailHog REST API
url = f"{settings.mailhog_api}?limit={limit}"
async with httpx.AsyncClient(timeout=10) as client:
r = await client.get(url)
r.raise_for_status()
data = r.json()
return data.get("items", [])


async def parse_emails(items):
return [extract_structured(it) for it in items]