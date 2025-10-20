from typing import List, Dict, Any, Tuple
import requests
import os

ERP_BASE_URL = os.getenv("ERP_BASE_URL", "http://erp:9000")
TIMEOUT = 5

def check_inventory_and_pricing(items: List[Dict[str, Any]]) -> Tuple[Dict[str, bool], Dict[str, float], str]:
    """
    items: [{"sku": "...", "qty": 3}, ...]
    returns: (availability: dict[str,bool], pricing: dict[str,float], currency: str)
    """
    url = f"{ERP_BASE_URL}/inventory/check"
    r = requests.post(url, json=items, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    availability = data.get("availability", {})
    pricing = data.get("pricing", {})
    currency = data.get("currency", "USD")
    return availability, pricing, currency

def create_quote(customer_id: str, items: List[Dict[str, Any]]) -> str:
    url = f"{ERP_BASE_URL}/quotes"
    payload = {"customer_id": customer_id, "items": items}
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data.get("quote_id", "")
