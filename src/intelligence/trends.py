from config.settings import (
    MARKET_DAILY_FILE,
    SKILLS_DAILY_FILE,
    MIN_TREND_SNAPSHOTS,
    TREND_WINDOW_DAYS,
)
from src.storage.json_store import ler_jsonl


def ordenar(registros):
    return sorted(registros, key=lambda r: r.get("date", ""))


def snapshots_comparaveis():
    mercado = ordenar(ler_jsonl(MARKET_DAILY_FILE))
    skills = ordenar(ler_jsonl(SKILLS_DAILY_FILE))

    mercado = [item for item in mercado if item.get("coverage_signature")]
    skills = [item for item in skills if item.get("coverage_signature")]

    if not mercado:
        return [], []

    assinatura_atual = mercado[-1]["coverage_signature"]
    versao_atual = mercado[-1].get("schema_version")

    mercado = [
        item
        for item in mercado
        if (
            item.get("coverage_signature") == assinatura_atual
            and item.get("schema_version") == versao_atual
        )
    ]

    skills = [
        item
        for item in skills
        if (
            item.get("coverage_signature") == assinatura_atual
            and item.get("schema_version") == versao_atual
        )
    ]

    return (
        mercado[-TREND_WINDOW_DAYS:],
        skills[-TREND_WINDOW_DAYS:],
    )


def calcular_variacao(anterior, atual):
    anterior = anterior or 0
    atual = atual or 0
    delta = atual - anterior
    percentual = (delta / anterior * 100) if anterior > 0 else None

    return {
        "antes": anterior,
        "agora": atual,
        "delta": delta,
        "percentual": round(percentual, 1) if percentual is not None else None,
    }


def ranking_variacao(inicio, fim, limite=10):
    nomes = set(inicio) | set(fim)
    ranking = []

    for nome in nomes:
        variacao = calcular_variacao(
            inicio.get(nome, 0),
            fim.get(nome, 0),
        )
        ranking.append({"nome": nome, **variacao})

    ranking.sort(
        key=lambda item: (item["delta"], item["agora"]),
        reverse=True,
    )
    return ranking[:limite]


def gerar_tendencias():
    mercado, skills = snapshots_comparaveis()
    quantidade = len(mercado)

    if quantidade < MIN_TREND_SNAPSHOTS:
        return {
            "ready": False,
            "snapshots": quantidade,
            "required": MIN_TREND_SNAPSHOTS,
            "remaining": max(0, MIN_TREND_SNAPSHOTS - quantidade),
        }

    primeiro = mercado[0]
    ultimo = mercado[-1]
    skills_por_data = {item["date"]: item for item in skills}
    primeira_skill = skills_por_data.get(primeiro["date"], {})
    ultima_skill = skills_por_data.get(ultimo["date"], {})

    return {
        "ready": True,
        "snapshots": quantidade,
        "period_start": primeiro["date"],
        "period_end": ultimo["date"],
        "jobs": calcular_variacao(
            primeiro.get("total_jobs", 0),
            ultimo.get("total_jobs", 0),
        ),
        "skills": ranking_variacao(
            primeira_skill.get("skills", {}),
            ultima_skill.get("skills", {}),
            15,
        ),
        "companies": ranking_variacao(
            primeiro.get("companies", {}),
            ultimo.get("companies", {}),
            10,
        ),
        "areas": ranking_variacao(
            primeiro.get("areas", {}),
            ultimo.get("areas", {}),
            10,
        ),
        "source_count": ultimo.get("source_count", 0),
        "coverage_signature": ultimo.get("coverage_signature"),
    }
