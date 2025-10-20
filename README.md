# POQuotator — Email → Quote POC


## Prereqs
- Docker + Docker Compose
- (Optional) `jq` for pretty JSON and `swaks` to send test emails


## Setup
1. Copy `.env.example` → `.env` and adjust if needed.
2. `make up`
3. Open:
- API docs: http://localhost:8000/docs
- Mail UI: http://localhost:8025
- ERP Mock: http://localhost:9000/docs


## Test Flow
1. Send a test email to MailHog (via UI or SMTP on `localhost:1025`).
- Subject: `Quote request`
- Body: `Please quote: 3x Widget A, 5 Widget-B`.
2. Call the API: `curl http://localhost:8000/ingest | jq`.
3. You should see structured extraction of products.


## Next Steps (milestones)
- [✅] Add validation + Pydantic models for extraction results.
- [✅] Implement availability check.
- [ ] If complete data → call `POST /quotes` in ERP mock.
- [ ] If missing data → post-process to forward email (via SMTP) with partial info.
- [ ] Add Postgres for logs + metrics.
- [ ] Swap regex extractor with LLM pipeline (OpenAI, LangChain) + JSON schema enforcement.
- [ ] Add CI (GitHub Actions) + container scan.