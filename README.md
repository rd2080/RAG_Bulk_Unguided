# Bulking Coach (RAG chatbot)

A small retrieval-augmented chatbot that answers bulking questions (muscle gain, calorie surplus, progressive overload). Answers come from approved public sources and always show their links. When a question is about cutting, the bot answers honestly and then frames it for someone trying to gain muscle.

- Backend: FastAPI (`app/`)
- Vector store: Postgres with pgvector (Neon in production)
- Embeddings: `nomic-embed-text` via Ollama
- Chat model: `qwen3:8b` via Ollama
- Chat page: `static/index.html`

## Run it

1. Install and start [Ollama](https://ollama.com), then pull the two models:

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

2. Copy the env template and put your Neon connection string in it:

```bash
cp .env.example .env
```

Set `DATABASE_URL` in `.env` to your Neon string. Never commit `.env`.

3. Start the app:

```bash
docker compose up --build
```

4. Load the approved sources into the database (run once, and again when you change `sources.txt`):

```bash
docker compose exec app python -m app.ingest sources.txt
```

5. Open http://localhost:8000 and ask a question.

## Status

Checked on the `main` branch:

- Unit tests: 6 pass (`pytest`).
- Ingest against Neon (pgvector): 18 chunks stored from the three approved sources.
- Chat: "How do I build muscle on a bulk?" returns an answer with source links.
- Chat: "How do I cut fat fast?" returns an answer framed toward bulking, with a note on when cutting does not fit.
- Chat: a steroid question gets a refusal that suggests a doctor.
- Docker: the app container starts and reaches Ollama on the host.

## Neon setup

1. Create a Neon project and copy its connection string.
2. Put it in `.env` as `DATABASE_URL`. Keep `?sslmode=require` at the end.
3. The ingest script creates the `vector` extension and the `chunks` table. You don't need to do it by hand. Run ingest before asking questions.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

## Sources

`sources.txt` lists the approved public pages. The ingest script checks `robots.txt` for each site and skips any page it disallows. Wikipedia and Harvard Nutrition Source block automated clients, so they are not used.

## Known limits

- The source set is small (three pages from MedlinePlus and CDC) and only lightly covers bulking. Add more approved pages to `sources.txt`.
- The 8B model sometimes adds numbers that are not in the retrieved text, even with the rule against it. Check figures against the cited sources.
- Steroid and PED questions get a fixed refusal that points to a doctor.
