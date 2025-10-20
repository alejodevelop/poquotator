import os
import smtplib
from email.mime.text import MIMEText
from typing import List, Dict

SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
TRIAGE_EMAIL = os.getenv("TRIAGE_EMAIL", "triage@example.com")
SENDER = os.getenv("SENDER_EMAIL", "noreply@poquotator.local")

def send_triage_email(
    from_email: str,
    subject: str,
    items: List[Dict[str, str]],
    availability: Dict[str, bool],
    pricing: Dict[str, float],
    currency: str,
    missing: List[str],
    customer_id: str,
):
    # separar disponibles vs. no disponibles
    available = [it for it in items if availability.get(it["sku"], False)]
    unavailable = [it for it in items if not availability.get(it["sku"], False)]

    # totales
    def line_total(it):
        return float(pricing.get(it["sku"], 0.0)) * int(it["qty"])

    subtotal = sum(line_total(it) for it in available)
    # impuestos/fees simulados (opcional)
    tax = round(subtotal * 0.0, 2)  # en POC lo dejamos 0
    grand_total = round(subtotal + tax, 2)

    lines = []
    lines.append("[POC] Triage de cotización — resumen")
    lines.append("")
    lines.append(f"De: {from_email or 'desconocido'}")
    lines.append(f"Asunto original: {subject or '(sin asunto)'}")
    lines.append(f"Customer ID: {customer_id}")
    lines.append("")

    lines.append("== Disponibles ==")
    if available:
        for it in available:
            unit = pricing.get(it["sku"], 0.0)
            lines.append(f"- {it['qty']} x {it['sku']} @ {unit:.2f} {currency} = {line_total(it):.2f} {currency}")
    else:
        lines.append("- (ninguno)")

    lines.append("")
    lines.append("== NO disponibles ==")
    if unavailable:
        for it in unavailable:
            lines.append(f"- {it['qty']} x {it['sku']}")
    else:
        lines.append("- (ninguno)")

    lines.append("")
    lines.append(f"Subtotal: {subtotal:.2f} {currency}")
    lines.append(f"Impuestos: {tax:.2f} {currency}")
    lines.append(f"Total estimado: {grand_total:.2f} {currency}")

    lines.append("")
    lines.append("== Faltantes / Motivos ==")
    if missing:
        for m in missing:
            lines.append(f"- {m}")
    else:
        lines.append("- (ninguno)")

    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = "[POC] Triage — cotización incompleta (con precios)"
    msg["From"] = SENDER
    msg["To"] = TRIAGE_EMAIL

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)
