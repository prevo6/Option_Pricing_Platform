# Option Pricing Platform

A self-contained data driven platform that extracts options chain data from multiple
market data providers, loads it into Postgres through a staged ETL pipeline orchestrated by
Airflow, and serves it through a Streamlit dashboard for options pricing (Black-Scholes,
Binomial Tree, Monte Carlo) and analysis.

Multi-source ingestion, schema design, orchestration, and containerized, reproducible deployment.

<!-- TODO: add 2-3 screenshots/GIFs here — dashboard heatmap, Airflow DAG graph succeeding -->

## Architecture

```
                 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                 │  Alpaca API  │   │ MarketData   │   │ Massive API  │
                 └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
                        │                  │                  │
                        ▼                  ▼                  ▼
                 ┌─────────────────────────────────────────────────┐
                 │         extract → transform → load (per source)  │
                 │         staged in Postgres, then upserted         │
                 └──────────────────────┬────────────────────────────┘
                                        ▼
                                 ┌─────────────┐
                                 │  Postgres   │◄──── orchestrated on a schedule by
                                 │ (Docker)    │       Airflow (DockerOperator, CeleryExecutor)
                                 └──────┬──────┘
                                        ▼
                                 ┌─────────────┐
                                 │  Streamlit  │
                                 │  Dashboard  │
                                 └─────────────┘
```

Each data source (Alpaca, MarketData.app, Massive) has its own independent
extract/transform/load pipeline. They share nothing but a common Postgres schema and a
`database/connection.py` helper — a bug or API change in one source cannot break another,
and each maps to its own Airflow DAG and schedule.

## Why these design decisions

- **Staging tables + `ON CONFLICT` upsert, not direct inserts** — every load first writes to a
  `stage_*` table, then merges into the real tables. This keeps partial/failed loads from
  corrupting existing data, and makes re-running a pipeline idempotent.
- **`underlying_assets` is a snapshot table (upserted), `options_quote_history` is append-only** —
  spot price only needs "latest known value," but quotes need full history for backtesting and
  IV-surface analysis later.
- **Airflow orchestration uses `DockerOperator`, not `PythonOperator`/`ExternalPythonOperator`** —
  keeps Airflow's own Python environment completely free of project dependencies (pandas, yfinance,
  etc.), so multiple unrelated Airflow-orchestrated projects never fight over conflicting package
  versions.
- **The dashboard never reads spot price from Postgres for pricing calculations** — it calls
  yfinance live (short-TTL cached) so Black-Scholes/Binomial/Monte Carlo always price against a
  fresh spot, while Postgres remains the system of record for historical analysis.

## Tech stack

| Layer | Tools |
|---|---|
| Extraction | `requests`, provider SDKs (Alpaca, MarketData.app, Massive), `yfinance` |
| Transformation | `pandas` |
| Storage | PostgreSQL (Docker) |
| Orchestration | Apache Airflow 3.x (Docker Compose, CeleryExecutor, `DockerOperator`) |
| Pricing models | Black-Scholes, Binomial Tree, Monte Carlo — `numpy`, `scipy` |
| Dashboard | Streamlit, Plotly/Matplotlib |
| Testing | `pytest` |

## Project structure

```
Option_Pricing_Platform/
├── etl_scripts/
│   ├── alpaca/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── load.py
│   │   └── alp_etl.py
│   ├── market_data/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── load.py
│   │   └── md_etl.py
│   └── massive/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── massive_etl.py
├── database/
│   └── connection.py
├── utils/
│   ├── yfinance_data.py
│   ├── queries.py
│   ├── visuals.py
│   └── stage_tables.py
├── pricing_engine/
│   ├── black.py           # Black-Scholes + greeks
│   ├── binomial.py        # Binomial tree (CRR) + visualization
│   └── monte.py           # Monte Carlo simulation
├── app/
│   ├── app.py
├── scripts/
│   └── seed_tracked_underlyings.py   # one-off: seed which tickers each pipeline tracks
├── airflow/
│   ├── Dockerfile                    # Airflow image + Docker provider
│   ├── docker-compose.yaml           # Airflow stack (CeleryExecutor, Redis, Postgres)
│   ├── .env.example
│   └── dags/
│       ├── alpaca_markets_dag.py
│       ├── market_data_dag.py
│       └── massive_dag.py
├── docker/
│   └── docker-compose.yml            # the project's own data Postgres
├── tests/
│   ├── test_black_prices.py
│   ├── test_greeks.py
│   ├── test_binomial.py
│   ├── test_monte.py
│   └── test_occ_symbol.py
├── Dockerfile                        # builds the ETL image DockerOperator runs
├── pyproject.toml
└── .env.example
```

## Getting started

### Prerequisites
- Docker Desktop
- Python 3.12+ and a virtual environment

### 1. Set up the project environment

```bash
git clone <repo-url>
cd Option_Pricing_Platform
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # fill in your own API keys / DB credentials
```

### 2. Start the data Postgres container

```bash
cd docker
docker compose up -d
cd ..
```

### 3. Run the dashboard

```bash
streamlit run app/app.py
```

### 4. (Optional) Run the orchestrated pipelines with Airflow

Create Airflow's environment file first:

```bash
cp airflow/.env.example airflow/.env
```

Fill in `AIRFLOW_UID` (run `id -u`) and `FERNET_KEY`, which you can generate with:

```bash
docker run --rm apache/airflow:3.3.1 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Build the ETL image (rebuild it after any code change), then start the stack:

```bash
docker build -t option-pricing-etl:latest .
cd airflow
docker compose up airflow-init   # first time only
docker compose up -d
```

Airflow UI: [http://localhost:8080](http://localhost:8080) (default login `airflow` / `airflow`).
DAGs are paused by default — unpause `alpaca_markets_dag`, `market_data_dag`, and `massive_dag`
from the UI to let them run on schedule, or trigger manually.

Each DAG task runs inside its own container and reaches the data Postgres through
`host.docker.internal`, which Docker Desktop provides on Mac and Windows.

## Running tests

From the project root:

```bash
pytest -v
```

## Roadmap

- [ ] Implied volatility surface visualization
- [ ] Historical backtesting page comparing model fair value to realized market price
- [ ] Seeded sample database + Docker Compose so the project runs out-of-the-box for reviewers