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

- **Timeouts and error checks:** every HTTP call has a 10-second timeout and fails loudly on 4xx/5xx errors.
- **Idempotent saves:** rows are upserted on a primary key, so running the script twice never creates duplicates.
- **Safe SQL:** all queries use `?` placeholders to prevent SQL injection.
- **Config outside code:** settings live in `.env` (not committed). `.env.example` shows what is needed.
- **Separation of concerns:** fetch, database and entry point are separate modules, so each is tested alone.

## Next steps

- Validate API responses with Pydantic
- Add retries with exponential backoff and logging
