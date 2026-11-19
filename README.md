# day1-api-to-sqlite

A small Python data pipeline that pulls 100 posts from the public [JSONPlaceholder](https://jsonplaceholder.typicode.com) API and saves them into a local SQLite database.

## Tech stack

Python 3.12, httpx, SQLite, python-dotenv, pytest, ruff, uv

## How it works

```
.env -> main.py -> fetch.py -> JSONPlaceholder API
           |
           +-----> db.py -> data.db (SQLite)
```

- `fetch.py` gets posts from the API
- `db.py` creates the table and saves posts
- `main.py` loads settings and connects the two

## Run it

```bash
uv sync
cp .env.example .env
uv run python -m app.main
```

Expected output:

```
Saved 100 posts. Table now has 100 rows.
```

## Test and lint

```bash
uv run python -m pytest -v
uv run ruff check .
```

All 3 tests pass. The API is mocked, so tests run offline in under a second.

## Design choices

- **Validation at the boundary:** every post is checked with a Pydantic model. Bad records are skipped and logged, so one broken post never stops the job.
- **Retries with exponential backoff:** timeouts, 429 and 5xx errors are retried (1s, 2s), then the job fails cleanly. 4xx errors fail fast with no retry.
- **Structured logging:** timestamped logs with levels replace print statements.
- **Clean failure:** a custom `FetchError` is caught in `main.py`, logged as one clear error, and the process exits with code 1.
- **Idempotent saves:** rows are upserted on a primary key, so reruns never create duplicates.
- **Safe SQL:** all queries use `?` placeholders to prevent SQL injection.
- **Config outside code:** settings live in `.env` (not committed). `.env.example` shows what is needed.

## Tests

8 tests cover: saving, no duplicates on rerun, validation, retry on 503, retry on timeout, no retry on 404, and giving up after max attempts. The API and the clock are faked, so tests run offline in under a second.