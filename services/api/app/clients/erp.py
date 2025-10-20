# services/api/app/clients/erp.py
from typing import List, Dict, Any
import requests
import os

ERP_BASE_URL = os.getenv("ERP_BASE_URL", "http://erp:9000")
TIMEOUT = 5

def check_inventory(items: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    items: [{"sku": "Widget A", "qty": 3}, ...]
    returns: {"availability": {"Widget A": True, "Widget-B": False}}
    """
    url = f"{ERP_BASE_URL}/inventory/check"
    r = requests.post(url, json=items, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data.get("availability", {})

def create_quote(customer_id: str, items: List[Dict[str, Any]]) -> str:
    """
    returns: quote_id (e.g., "Q-12345")
    """
    url = f"{ERP_BASE_URL}/quotes"
    payload = {"customer_id": customer_id, "items": items}
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data.get("quote_id", "")
