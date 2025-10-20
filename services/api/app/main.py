from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os, re, requests

app = FastAPI(title="Poquotator API", version="0.1.0")

# --- Healthcheck ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Config ---
MAILHOG_API = os.getenv("MAILHOG_API", "http://mailhog:8025/api/v2/messages")

# --- Schemas ---
class Item(BaseModel):
    sku: str
    qty: int

class IngestResponse(BaseModel):
    from_email: str
    subject: str
    items: List[Item]

# --- Parser muy simple ---
def parse_items(text: str) -> List[Item]:
    # Matchea: "3x Widget A", "5 Widget-B", "2 X SKU123"
    pattern = re.compile(r"(?P<qty>\d+)\s*(?:x|X)?\s*(?P<sku>[A-Za-z0-9][\w\- ]+)")
    merged: Dict[str, int] = {}
    for m in pattern.finditer(text or ""):
        qty = int(m.group("qty"))
        sku = m.group("sku").strip()
        merged[sku] = merged.get(sku, 0) + qty
    return [Item(sku=k, qty=v) for k, v in merged.items()]

# --- Endpoint /ingest ---
@app.get("/ingest", response_model=IngestResponse)
def ingest_latest_email():
    try:
        r = requests.get(MAILHOG_API, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MailHog fetch failed: {e}")

    items = data.get("items") or []
    if not items:
        raise HTTPException(status_code=404, detail="No emails found in MailHog")

    msg = items[0]  # más reciente
    from_email = ""
    if msg.get("From"):
        from_email = f"{msg['From'].get('Mailbox','')}@{msg['From'].get('Domain','')}"
    subject = (msg.get("Content", {}).get("Headers", {}).get("Subject", []) or [""])[0]
    body = msg.get("Content", {}).get("Body", "") or ""

    parsed = parse_items(body)
    return IngestResponse(
        from_email=from_email or "unknown@example.com",
        subject=subject,
        items=parsed
    )
