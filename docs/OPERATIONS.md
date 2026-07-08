# Operations

## Local Checks

```bash
make venv
make lint
make test
```

## Compose Runbook

```bash
cp .env.example .env
docker compose up --build
```

Danach pruefen:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/metrics
```

## Modell vorbereiten

Wenn Ollama im Compose-Stack laeuft:

```bash
docker exec -it private-ai-lab-ollama ollama pull llama3.2:3b
```

## Typische Fehler

| Symptom | Ursache | Loesung |
| --- | --- | --- |
| `/readyz` liefert 503 | Postgres nicht bereit | `docker compose ps`, Logs pruefen |
| Chat liefert 502 | LLM API nicht erreichbar | Ollama starten, Modell pullen |
| Upload liefert 400 | PDF ohne extrahierbaren Text | anderes PDF oder OCR davor nutzen |
| Dimension mismatch | Embedding-Modell passt nicht zur DB | `EMBEDDING_DIMENSIONS` und Modell angleichen |

## Monitoring

Die App exportiert:

- `private_ai_lab_http_requests_total`
- `private_ai_lab_http_request_duration_seconds`

Prometheus scraped die API unter `/metrics`. Grafana wird mit einem einfachen
Dashboard provisioniert.
