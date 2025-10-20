from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional


API_KEY = "dev-erp-key"


class Product(BaseModel):
name: str
quantity: float


class QuoteRequest(BaseModel):
customer_email: Optional[str] = None
customer_name: Optional[str] = None
company: Optional[str] = None
products: List[Product]


app = FastAPI(title="ERP Mock")


@app.post("/quotes")
async def create_quote(req: QuoteRequest, x_api_key: str = Header(default="")):
if x_api_key != API_KEY:
raise HTTPException(status_code=401, detail="invalid api key")
# Return a fake quote id and echo payload
return {"quote_id": "Q-" + req.customer_email[:3] if req.customer_email else "Q-000", "data": req.model_dump()}