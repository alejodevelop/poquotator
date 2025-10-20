from fastapi import FastAPI
from .email_ingestor import pull_new_emails, parse_emails
from .schemas import ExtractedEmail
from typing import List


app = FastAPI(title="POQuotator API")


@app.get("/health")
def health():
return {"status": "ok"}


@app.get("/ingest", response_model=List[ExtractedEmail])
async def ingest(limit: int = 10):
items = await pull_new_emails(limit=limit)
extracted = await parse_emails(items)
return extracted