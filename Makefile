.PHONY: up down logs reset rebuild


up:
docker compose up -d --build
docker compose ps


e2e:
# send a sample email into MailHog via SMTP using swaks (optional if installed)
# swaks --to test@example.com --from "Alejandro <alejo@test.com>" --server 127.0.0.1:1025 --header "Subject: Quote request" --body "Please quote: 3x Widget A, 5 Widget-B"
curl -s http://localhost:8000/ingest | jq


logs:
docker compose logs -f --tail=200


down:
docker compose down


reset:
docker compose down -v
docker system prune -f


rebuild:
docker compose build --no-cache