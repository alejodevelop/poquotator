from fastapi import FastAPI, HTTPException, Body
from typing import Optional
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.clients.erp import check_inventory_and_pricing, create_quote
from app.clients.mailer import send_triage_email
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

class ProcessResult(BaseModel):
    status: str
    from_email: str
    subject: str
    items: List[Item] = Field(default_factory=list)
    availability: Dict[str, bool] = Field(default_factory=dict)
    pricing: Dict[str, float] = Field(default_factory=dict)
    currency: str = "USD"
    missing: Optional[List[str]] = None
    quote_id: Optional[str] = None
    reason: Optional[str] = None

class ProcessInput(BaseModel):
    customer_id: str = "prospect-unknown"

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

@app.post("/process-latest", response_model=ProcessResult)
def process_latest_email(payload: ProcessInput):
    """
    Orquesta: lee último email, parsea items, verifica inventario y crea quote si aplica.
    """
    customer_id = payload.customer_id
    # 1) Reusar la lógica de MailHog que ya tienes en /ingest
    try:
        # reusa tu función existente o copia aquí el fetch a MAILHOG_API
        r = requests.get(MAILHOG_API, timeout=5)
        r.raise_for_status()
        data = r.json()
        items_list = data.get("items") or []
        if not items_list:
            raise HTTPException(status_code=404, detail="No emails found")
        msg = items_list[0]
        from_email = ""
        if msg.get("From"):
            from_email = f"{msg['From'].get('Mailbox','')}@{msg['From'].get('Domain','')}"
        subject = (msg.get("Content", {}).get("Headers", {}).get("Subject", []) or [""])[0]
        body = msg.get("Content", {}).get("Body", "") or ""
        parsed = parse_items(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MailHog fetch failed: {e}")

    # 2) Validaciones mínimas
    missing = []
    if not parsed:
        missing.append("items")
    if not customer_id:
        missing.append("customer_id")

    # 3) Disponibilidad (si hay items)
    availability: Dict[str, bool] = {}
    pricing: Dict[str, float] = {}
    currency: str = "USD"

    if parsed:
        items_payload = [{"sku": it.sku, "qty": it.qty} for it in parsed]
        try:
            availability, pricing, currency = check_inventory_and_pricing(items_payload)
        except Exception as e:
            return ProcessResult(
                status="error",
                from_email=from_email or "unknown@example.com",
                subject=subject or "",
                items=parsed,
                availability=availability,
                pricing=pricing,
                currency=currency,
                reason=f"ERP inventory error: {e}",
            )


        # agrega a missing los SKUs sin stock
        out_of_stock = [sku for sku, ok in availability.items() if not ok]
        if out_of_stock:
            missing.extend([f"stock:{sku}" for sku in out_of_stock])

    # 4) Si hay faltantes → incomplete + email a triage
    if missing:
        try:
            send_triage_email(
                from_email=from_email or "unknown@example.com",
                subject=subject or "",
                items=[{"sku": it.sku, "qty": it.qty} for it in parsed],
                availability=availability,
                pricing=pricing,
                currency=currency,
                missing=missing,
                customer_id=customer_id,
            )
        except Exception as e:
            return ProcessResult(
                status="incomplete",
                from_email=from_email or "unknown@example.com",
                subject=subject or "",
                items=parsed,
                availability=availability,
                pricing=pricing,
                currency=currency,
                missing=missing,
                reason=f"triage email failed: {e}",
            )

        return ProcessResult(
            status="incomplete",
            from_email=from_email or "unknown@example.com",
            subject=subject or "",
            items=parsed,
            availability=availability,
            pricing=pricing,
            currency=currency,
            missing=missing
        )

    # 5) Todo OK → crear quote
    try:
        quote_id = create_quote(customer_id, [{"sku": it.sku, "qty": it.qty} for it in parsed])
        return ProcessResult(
            status="created",
            from_email=from_email or "unknown@example.com",
            subject=subject or "",
            items=parsed,
            availability=availability,
            pricing=pricing,
            currency=currency,
            quote_id=quote_id
        )

    except Exception as e:
        return ProcessResult(
            status="error",
            from_email=from_email or "unknown@example.com",
            subject=subject or "",
            items=parsed,
            availability=availability,
            reason=f"ERP quote error: {e}",
        )