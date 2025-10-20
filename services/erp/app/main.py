from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="ERP Mock", version="0.1.0")

# --- Models (muy simples para POC) ---
class ItemRequest(BaseModel):
    sku: str
    qty: int

class QuoteRequest(BaseModel):
    customer_id: str
    items: List[ItemRequest]

class QuoteResponse(BaseModel):
    quote_id: str
    status: str = "CREATED"

# --- Endpoints de prueba ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/inventory/check")
def check_inventory(items: List[ItemRequest]) -> Dict[str, Dict[str, bool]]:
    availability = {i.sku: (i.sku.endswith("A")) for i in items}
    return {"availability": availability}

@app.post("/quotes", response_model=QuoteResponse)
def create_quote(payload: QuoteRequest):
    # Genera un ID de cotización simulado
    qid = f"Q-{abs(hash(payload.customer_id)) % 100000:05d}"
    return QuoteResponse(quote_id=qid)
