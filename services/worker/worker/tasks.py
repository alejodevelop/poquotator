from celery import Celery
from .config import BROKER_URL
import httpx


app = Celery("poquotator", broker=BROKER_URL, backend=BROKER_URL)


@app.task
def check_availability(products: list):
# Placeholder: call ERP mock to check stock
# Returns a dict with availability per product
return {p["name"]: True for p in products}


@app.task
def create_quote(payload: dict):
# Placeholder: integrate with ERP mock
with httpx.Client(base_url="http://erp-mock:9000", timeout=10) as client:
r = client.post("/quotes", json=payload, headers={"x-api-key":"dev-erp-key"})
r.raise_for_status()
return r.json()