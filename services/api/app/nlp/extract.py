import re
from typing import Dict, Any


PRODUCT_PATTERN = re.compile(r"(?P<qty>\d+(?:[.,]\d+)?)\s*x?\s*(?P<name>[\w\-\s]+)", re.I)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def extract_structured(email: Dict[str, Any]) -> Dict[str, Any]:
body = (email.get("Content", {}).get("Body", "") or "")
subject = email.get("Content", {}).get("Headers", {}).get("Subject", [""])[0]
sender = email.get("Content", {}).get("Headers", {}).get("From", [""])[0]


products = []
for m in PRODUCT_PATTERN.finditer(body):
qty = float(m.group("qty").replace(",", "."))
name = m.group("name").strip()
products.append({"name": name, "quantity": qty})


sender_email = None
m = EMAIL_PATTERN.search(sender)
if m:
sender_email = m.group(0)


return {
"customer_email": sender_email,
"customer_name": sender.split("<")[0].strip().strip('"') or None,
"company": None,
"products": products,
"availability_needed": True,
"pricing_needed": False,
"raw_subject": subject,
}