from pathlib import Path


PROJECT_NAME = "Michael Opportunity Intelligence"
TIMEZONE = "America/Sao_Paulo"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

JOBS_FILE = DATA_DIR / "jobs" / "jobs.jsonl"
COMPANIES_FILE = DATA_DIR / "companies" / "companies.jsonl"
SKILLS_DAILY_FILE = DATA_DIR / "market" / "skills_daily.jsonl"
MARKET_DAILY_FILE = DATA_DIR / "market" / "market_daily.jsonl"
JOBS_SEEN_FILE = DATA_DIR / "state" / "jobs_seen.json"
LAST_RUNS_FILE = DATA_DIR / "state" / "last_runs.json"
CURRENT_JOBS_FILE = DATA_DIR / "state" / "current_jobs.json"

SOURCES_DIR = DATA_DIR / "sources"
SOURCE_REGISTRY_FILE = SOURCES_DIR / "discovery_registry.json"
TAVILY_BUDGET_FILE = DATA_DIR / "state" / "tavily_discovery_budget.json"
SOURCE_DUPLICATES_FILE = DATA_DIR / "state" / "source_duplicates.json"

MARKET_SCHEMA_VERSION = 2
CLASSIFIER_VERSION = "area-v3"
MIN_TREND_SNAPSHOTS = 3
TREND_WINDOW_DAYS = 7

EXPORTS_DIR = DATA_DIR / "exports"
JOBS_CURRENT_CSV = EXPORTS_DIR / "jobs_current.csv"
JOBS_HISTORY_CSV = EXPORTS_DIR / "jobs_history.csv"
SKILLS_DAILY_CSV = EXPORTS_DIR / "skills_daily.csv"
AREAS_DAILY_CSV = EXPORTS_DIR / "areas_daily.csv"
COMPANIES_DAILY_CSV = EXPORTS_DIR / "companies_daily.csv"
MARKET_DAILY_CSV = EXPORTS_DIR / "market_daily.csv"

PARQUET_DIR = DATA_DIR / "parquet"
JOBS_CURRENT_PARQUET = PARQUET_DIR / "jobs_current.parquet"
JOBS_HISTORY_PARQUET = PARQUET_DIR / "jobs_history.parquet"
SKILLS_DAILY_PARQUET = PARQUET_DIR / "skills_daily.parquet"
AREAS_DAILY_PARQUET = PARQUET_DIR / "areas_daily.parquet"
COMPANIES_DAILY_PARQUET = PARQUET_DIR / "companies_daily.parquet"
MARKET_DAILY_PARQUET = PARQUET_DIR / "market_daily.parquet"
