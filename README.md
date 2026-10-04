# Option Pricing Platform

A self-contained data engineering platform that extracts options chain data from multiple
market data providers, loads it into Postgres through a staged ETL pipeline orchestrated by
Airflow, and serves it through a Streamlit dashboard for options pricing (Black-Scholes,
Binomial Tree, Monte Carlo) and analysis.

This was built as a solo project to demonstrate practical data engineering skills: multi-source
ingestion, schema design, orchestration, and containerized, reproducible deployment.

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
| Pricing models | Black-Scholes, Binomial Tree (Monte Carlo in progress) — `numpy`, `scipy` |
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
│   ├── black.py
│   └── binomial.py
├── app/
│   ├── app.py
│   └── callbacks.py
├── airflow_dags/
│   ├── alpaca_markets_dag.py
│   ├── market_data_dag.py
│   └── massive_dag.py
├── airflow/
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── dags/            
├── tests/
│   ├── test_black_scholes.py
│   ├── test_binomial_tree.py
│   ├── test_occ_symbol_parsing.py
│   └── test_transform_dedup.py
├── Dockerfile             # builds the ETL image DockerOperator runs
├── docker-compose.yml     # the project's own Postgres
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
docker compose up -d
```

### 3. Run the dashboard

```bash
streamlit run app/app.py
```

### 4. (Optional) Run the orchestrated pipelines with Airflow

```bash
cd airflow
docker compose up airflow-init   # first time only
docker compose up -d
```

Airflow UI: [http://localhost:8080](http://localhost:8080) (default login `airflow` / `airflow`).
DAGs are paused by default — unpause `alpaca_markets_dag`, `market_data_dag`, and `massive_dag`
from the UI to let them run on schedule, or trigger manually.

The ETL image needs to be built once (and rebuilt after any code change) before Airflow can run it:

```bash
docker build -t option-pricing-etl:latest .
```

## Running tests

```bash
pytest -v
```

## What I'd do differently / lessons learned

<!-- TODO: fill this in — a few honest sentences go a long way. Ideas based on this project: -->
- Underestimated how much import-path resolution differs across entry points (plain script,
  `pytest`, `streamlit run`, Airflow's `DockerOperator`) — settled on an editable install
  (`pip install -e .`) as the one fix that works everywhere, rather than patching `sys.path` per
  entry point.
- Hit the same `ON CONFLICT ... DO UPDATE` cardinality violation twice, from two different
  sources, before writing a dedup step into the transform stage as a standing rule rather than a
  one-off fix.
- Learned Docker and Airflow from scratch specifically to make this project's ETL layer
  reproducible and independently orchestrated — the environment isolation problem (Airflow's own
  Python environment vs. the project's dependencies) was the most instructive part.

## Roadmap

- [ ] Implied volatility surface visualization
- [ ] Historical backtesting page comparing model fair value to realized market price
- [ ] Seeded sample database + Docker Compose so the project runs out-of-the-box for reviewers
