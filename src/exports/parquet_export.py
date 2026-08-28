from pathlib import Path

import polars as pl

from config.settings import (
    JOBS_CURRENT_CSV,
    JOBS_HISTORY_CSV,
    SKILLS_DAILY_CSV,
    AREAS_DAILY_CSV,
    COMPANIES_DAILY_CSV,
    MARKET_DAILY_CSV,
    JOBS_CURRENT_PARQUET,
    JOBS_HISTORY_PARQUET,
    SKILLS_DAILY_PARQUET,
    AREAS_DAILY_PARQUET,
    COMPANIES_DAILY_PARQUET,
    MARKET_DAILY_PARQUET,
)


DATASETS = {
    "jobs_current": (JOBS_CURRENT_CSV, JOBS_CURRENT_PARQUET),
    "jobs_history": (JOBS_HISTORY_CSV, JOBS_HISTORY_PARQUET),
    "skills_daily": (SKILLS_DAILY_CSV, SKILLS_DAILY_PARQUET),
    "areas_daily": (AREAS_DAILY_CSV, AREAS_DAILY_PARQUET),
    "companies_daily": (COMPANIES_DAILY_CSV, COMPANIES_DAILY_PARQUET),
    "market_daily": (MARKET_DAILY_CSV, MARKET_DAILY_PARQUET),
}


def converter_csv_para_parquet(origem, destino):
    origem = Path(origem)
    destino = Path(destino)

    if not origem.exists():
        raise FileNotFoundError(f"CSV não encontrado: {origem}")

    destino.parent.mkdir(parents=True, exist_ok=True)

    dataframe = pl.read_csv(
        origem,
        infer_schema_length=10_000,
        try_parse_dates=True,
    )

    dataframe.write_parquet(
        destino,
        compression="zstd",
        statistics=True,
    )

    tamanho_csv = origem.stat().st_size
    tamanho_parquet = destino.stat().st_size

    economia = 0.0
    if tamanho_csv:
        economia = round(
            (1 - (tamanho_parquet / tamanho_csv)) * 100,
            1,
        )

    return {
        "rows": dataframe.height,
        "columns": dataframe.width,
        "csv_bytes": tamanho_csv,
        "parquet_bytes": tamanho_parquet,
        "economia_percentual": economia,
    }


def gerar_parquets():
    resultado = {}
    for nome, (csv_file, parquet_file) in DATASETS.items():
        resultado[nome] = converter_csv_para_parquet(
            csv_file,
            parquet_file,
        )
    return resultado
