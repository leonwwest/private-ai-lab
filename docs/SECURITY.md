# Security Notes

Dieses Projekt ist ein lokales Lab und kein fertig gehaertetes Produktivsystem.
Es zeigt aber bewusst Sicherheitsbausteine, die fuer eine private AI-Plattform
wichtig sind.

## Enthalten

- API-Key-Auth fuer geschuetzte Endpunkte
- keine echten Secrets im Repo
- `.env.example` nur mit Demo-Werten
- Healthchecks getrennt von geschuetzten RAG-Endpunkten
- strukturierte Logs ohne PDF-Inhalte
- Upload-Limit ueber `MAX_UPLOAD_MB`

## Vor echter Nutzung ergaenzen

- echte Secret-Verwaltung statt Klartext-Env
- TLS/Ingress-Absicherung
- rollenbasierte Auth statt einem API-Key
- Malware-/Content-Scanning fuer Uploads
- Audit-Log fuer Dokumentzugriffe
- Backup-Strategie fuer Postgres
- Retention-Konzept fuer Dokumente und Logs

## Vor oeffentlicher Freigabe

```bash
gitleaks detect --source . --redact --no-banner --exit-code 42
git status -sb
```

Zusaetzlich README und `.env.example` pruefen, damit keine privaten Pfade,
internen URLs oder echten Kundendaten enthalten sind.
