# Capybara Validator Blueprint (Wombat Docker)

This directory is the capybara validator application reference.
It can run:

1. Locally with Python
2. In Docker with mounted data directories

## Purpose

The validator reads capybara payload files from a fresh directory, validates required schema and business rules, records accepted files in PostgreSQL tables, and moves files to success or failure directories.

## Components

### 1) Application Entrypoint

File: capybara_app.py

- Builds PostgreSQL connectivity from environment variables.
- Configures SQLAlchemy with connect timeout, statement timeout, and pool pre-ping.
- Routes execution by stuntbox mode.
- Current mode: validator.

### 2) Validator Engine

File: validator.py

- Uses an abstract validator interface and a concrete `CapybaraValidator` implementation.
- Iterates files in the configured fresh directory.
- Validates payload shape and capybara-specific business rules.
- Enforces idempotency by checking load-log state.
- On success: updates load-log/daily-score/frequency tables and moves file to success.
- On failure: moves file to failure.

### 3) Runtime Configuration

Supported environment variables:

1. DB_CONN
2. PG_CONNECT_TIMEOUT (default 5)
3. PG_STATEMENT_TIMEOUT_MS (default 5000)
4. FRESH_DIR (default /var/wombat/fresh/capybara)
5. SUCCESS_DIR (default /var/wombat/capybara/success)
6. FAILURE_DIR (default /var/wombat/failure)
7. stuntbox (default validator)

## Testing

Run tests from this directory:

```bash
source venv/bin/activate
python -m pytest -q
```

## Docker

Build:

```bash
docker build -f src/wombat_docker/Dockerfile -t capybara:latest src/
```

Run:

```bash
docker run \
  -e stuntbox=validator \
  -e DB_CONN="postgresql+psycopg2://capybara_client:batabat@172.17.0.1:5432/capybara" \
  -v /var/wombat:/mnt/wombat \
  --name capybara \
  capybara:latest
```
