from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="ERP Mock", version="0.2.0")

# --- Models ---
class ItemRequest(BaseModel):
    sku: str
    qty: int

class QuoteRequest(BaseModel):
    customer_id: str
    items: List[ItemRequest]

class QuoteResponse(BaseModel):
    quote_id: str
    status: str = "CREATED"

# --- Precio simulado ---
CATALOG = {
    "Widget A": 12.50,
    "Widget-B": 9.90,
    "ItemA": 7.25,
}
CURRENCY = "USD"

def price_for(sku: str) -> float:
    if sku in CATALOG:
        return CATALOG[sku]
    # fallback sencillo: base 10 + 0.5 * largo
    return round(10 + 0.5 * len(sku), 2)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/inventory/check")
def check_inventory(items: List[ItemRequest]) -> Dict:
    # Disponible si el SKU termina en 'A' (regla de POC)
    availability = {i.sku: (i.sku.strip().endswith("A")) for i in items}
    # Precios unitarios (por SKU)
    pricing = {i.sku: price_for(i.sku) for i in items}
    return {
        "availability": availability,    # dict[str,bool]
        "pricing": pricing,              # dict[str,float]
        "currency": CURRENCY
    }

@app.post("/quotes", response_model=QuoteResponse)
def create_quote(payload: QuoteRequest):
    qid = f"Q-{abs(hash(payload.customer_id)) % 100000:05d}"
    return QuoteResponse(quote_id=qid)
