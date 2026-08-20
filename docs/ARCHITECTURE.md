# Architecture

Private AI Lab ist eine kleine, lokale AI-Plattform. Der Fokus liegt nicht auf
einer grossen UI, sondern auf den Bausteinen, die bei AI-Plattformrollen wichtig
sind: API, RAG, Datenhaltung, Deployment, Auth und Observability.

## Komponenten

| Komponente | Aufgabe |
| --- | --- |
| FastAPI | HTTP API, Auth, Upload, Chat, Healthchecks |
| PDF Loader | extrahiert Text aus PDFs |
| Chunker | teilt Dokumenttext in ueberlappende Abschnitte |
| Embedding Provider | erzeugt Vektoren fuer Chunks und Suchfragen |
| Postgres + pgvector | speichert Dokumente, Chunks und Vektoren |
| Retriever | sucht passende Chunks per Cosine Distance |
| LLM Client | ruft eine OpenAI-kompatible Chat API auf |
| Prometheus | sammelt Request-Metriken |
| Grafana | visualisiert Request Rate und Latenz |

## RAG Flow

1. Ein PDF wird ueber `/v1/documents/upload` hochgeladen.
2. Die App extrahiert Text mit `pypdf`.
3. Der Chunker erzeugt ueberlappende Textabschnitte.
4. Der Embedding Provider erzeugt pro Chunk einen Vektor.
5. Dokumentmetadaten und Chunks werden in Postgres gespeichert.
6. Eine Frage an `/v1/chat` wird ebenfalls eingebettet.
7. pgvector liefert die aehnlichsten Chunks.
8. Der LLM Client baut daraus einen Kontextprompt und ruft die Chat API auf.
9. Die Antwort enthaelt Quellen aus den gefundenen Chunks.

## Embedding-Modi

`EMBEDDING_PROVIDER=hash` ist der Default. Das ist kein semantisches
Produktions-Embedding, aber sehr nuetzlich fuer lokale Tests, CI und Demos ohne
externen API-Key.

`EMBEDDING_PROVIDER=openai` nutzt einen OpenAI-kompatiblen `/embeddings`-Endpunkt.
Die Dimension muss zur pgvector-Spalte passen. Standard ist `384`.

## Betriebsmodell

Docker Compose ist fuer den lokalen Gesamtstack gedacht. k3d zeigt, wie die
gleiche App in Kubernetes betrieben werden koennte. Die k3d-Manifeste sind
bewusst klein gehalten, damit sie im Portfolio lesbar bleiben.

Security- und Datenschutzgrenzen sind separat im [Threat Model](THREAT_MODEL.md) dokumentiert.
Die synthetische [Offline-RAG-Evaluation](evidence/rag-evaluation.md) prueft die Retrieval-Verkabelung
reproduzierbar, ohne echte Dokumente oder externe Modellaufrufe.
