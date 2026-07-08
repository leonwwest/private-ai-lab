# Samples

Lege hier eigene Test-PDFs ab, die keine privaten oder kundenspezifischen Daten
enthalten.

Beispiel:

```bash
curl -X POST http://localhost:8000/v1/documents/upload \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@samples/example.pdf"
```

PDFs sind in `.gitignore` nicht pauschal ausgeschlossen, damit spaeter ein
harmloses Demo-PDF bewusst committed werden kann.
