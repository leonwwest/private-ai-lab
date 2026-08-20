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
- Non-root Container, Kubernetes `restricted` Pod Security und read-only Root-Dateisysteme
- Default-deny NetworkPolicy mit expliziten Servicepfaden
- vollstaendig offline ausfuehrbare Hash-Embeddings und RAG-Evaluation

## Vor echter Nutzung ergaenzen

- echte Secret-Verwaltung statt Klartext-Env
- TLS/Ingress-Absicherung
- rollenbasierte Auth statt einem API-Key
- Malware-/Content-Scanning fuer Uploads
- Audit-Log fuer Dokumentzugriffe
- Retention-Konzept fuer Dokumente und Logs

Das ausfuehrliche [Threat Model](THREAT_MODEL.md) dokumentiert Assets, Trust Boundaries,
implementierte Controls und verbleibende Risiken.

## Vor oeffentlicher Freigabe

```bash
gitleaks git --no-banner --redact=100 .
make verify
git status --short
```

Zusaetzlich README und `.env.example` pruefen, damit keine privaten Pfade,
internen URLs oder echten Kundendaten enthalten sind.
