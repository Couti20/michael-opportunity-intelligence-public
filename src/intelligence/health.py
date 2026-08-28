from datetime import datetime
from zoneinfo import ZoneInfo

from config.settings import (
    TIMEZONE,
    CURRENT_JOBS_FILE,
    JOBS_FILE,
    MARKET_DAILY_FILE,
    SKILLS_DAILY_FILE,
    LAST_RUNS_FILE,
)
from src.storage.json_store import carregar_json, ler_jsonl


CAMPOS_OBRIGATORIOS = [
    "id",
    "company",
    "title",
    "url",
    "area",
    "seniority",
]


def idade_horas(data_iso):
    if not data_iso:
        return None
    try:
        data = datetime.fromisoformat(data_iso)
        agora = datetime.now(ZoneInfo(TIMEZONE))
        return max(0, (agora - data).total_seconds() / 3600)
    except (ValueError, TypeError):
        return None


def status_score(score):
    if score >= 90:
        return "excelente", "🟢"
    if score >= 75:
        return "boa", "🟢"
    if score >= 60:
        return "atenção", "🟡"
    return "crítica", "🔴"


def gerar_saude():
    alertas = []
    detalhes = {}

    last_runs = carregar_json(LAST_RUNS_FILE, {})
    coleta = last_runs.get("market_collection", {})
    ultima_coleta = coleta.get("last_run")
    horas = idade_horas(ultima_coleta)

    if horas is None:
        score_recencia = 0
        alertas.append("Última coleta não identificada.")
    elif horas <= 8:
        score_recencia = 20
    elif horas <= 16:
        score_recencia = 15
    elif horas <= 24:
        score_recencia = 8
        alertas.append("Coleta mais antiga que o esperado.")
    else:
        score_recencia = 0
        alertas.append("Dataset possivelmente desatualizado.")

    detalhes["recencia"] = {
        "score": score_recencia,
        "maximo": 20,
        "ultima_coleta": ultima_coleta,
        "idade_horas": round(horas, 1) if horas is not None else None,
    }

    snapshots = sorted(
        ler_jsonl(MARKET_DAILY_FILE),
        key=lambda item: item.get("date", ""),
    )
    atual = snapshots[-1] if snapshots else {}
    anterior = snapshots[-2] if len(snapshots) >= 2 else {}

    fontes_atual = atual.get("source_count", 0) or 0
    fontes_anterior = anterior.get("source_count", 0) or 0
    assinatura_atual = atual.get("coverage_signature")
    assinatura_anterior = anterior.get("coverage_signature")

    if not atual:
        score_cobertura = 0
        situacao_cobertura = "sem_snapshot"
        alertas.append("Snapshot de mercado ausente.")
    elif not anterior:
        score_cobertura = 20
        situacao_cobertura = "baseline"
    elif assinatura_atual and assinatura_atual == assinatura_anterior:
        score_cobertura = 25
        situacao_cobertura = "estável"
    elif fontes_atual >= fontes_anterior:
        score_cobertura = 20
        situacao_cobertura = "expandida"
    else:
        queda = (fontes_anterior - fontes_atual) / max(fontes_anterior, 1)
        if queda <= 0.05:
            score_cobertura = 15
            situacao_cobertura = "pequena_redução"
        else:
            score_cobertura = 5
            situacao_cobertura = "redução_relevante"
            alertas.append("Cobertura de fontes caiu de forma relevante.")

    detalhes["cobertura"] = {
        "score": score_cobertura,
        "maximo": 25,
        "situacao": situacao_cobertura,
        "fontes_atuais": fontes_atual,
        "fontes_anteriores": fontes_anterior,
        "coverage_signature": assinatura_atual,
    }

    vagas_atual = atual.get("total_jobs", 0) or 0
    vagas_anterior = anterior.get("total_jobs", 0) or 0
    comparavel = (
        bool(anterior)
        and assinatura_atual
        and assinatura_atual == assinatura_anterior
        and vagas_anterior > 0
    )

    variacao = None
    if not atual:
        score_volume = 0
    elif not comparavel:
        score_volume = 15
    else:
        variacao = (vagas_atual - vagas_anterior) / vagas_anterior * 100
        abs_variacao = abs(variacao)
        if abs_variacao <= 15:
            score_volume = 20
        elif abs_variacao <= 30:
            score_volume = 12
        elif abs_variacao <= 50:
            score_volume = 6
            alertas.append("Variação elevada no volume de vagas.")
        else:
            score_volume = 0
            alertas.append("Anomalia forte no volume de vagas.")

    detalhes["volume"] = {
        "score": score_volume,
        "maximo": 20,
        "vagas_atuais": vagas_atual,
        "vagas_anteriores": vagas_anterior,
        "comparavel": comparavel,
        "variacao_percentual": round(variacao, 1) if variacao is not None else None,
    }

    vagas = carregar_json(CURRENT_JOBS_FILE, [])
    faltantes = 0
    total_campos = len(vagas) * len(CAMPOS_OBRIGATORIOS)

    for vaga in vagas:
        for campo in CAMPOS_OBRIGATORIOS:
            valor = vaga.get(campo)
            if valor is None or valor == "":
                faltantes += 1

    ids = [vaga.get("id") for vaga in vagas if vaga.get("id")]
    duplicados = len(ids) - len(set(ids))
    completude = 1 - (faltantes / total_campos) if total_campos else 0

    score_qualidade = round(
        completude * 20
        + (5 if duplicados == 0 else max(0, 5 - duplicados)),
        1,
    )

    if faltantes > 0:
        alertas.append(f"{faltantes} campo(s) obrigatório(s) vazio(s).")
    if duplicados > 0:
        alertas.append(f"{duplicados} ID(s) duplicado(s) no mercado atual.")

    detalhes["qualidade"] = {
        "score": score_qualidade,
        "maximo": 25,
        "registros": len(vagas),
        "completude_percentual": round(completude * 100, 1),
        "campos_faltantes": faltantes,
        "ids_duplicados": duplicados,
    }

    historico = ler_jsonl(JOBS_FILE)
    skills = ler_jsonl(SKILLS_DAILY_FILE)

    checks = {
        "current_jobs": bool(vagas),
        "jobs_history": bool(historico),
        "market_daily": bool(snapshots),
        "skills_daily": bool(skills),
        "last_runs": bool(ultima_coleta),
    }

    score_persistencia = sum(1 for ok in checks.values() if ok) * 2
    if not all(checks.values()):
        alertas.append("Um ou mais arquivos essenciais não estão disponíveis.")

    detalhes["persistencia"] = {
        "score": score_persistencia,
        "maximo": 10,
        "checks": checks,
    }

    score = round(
        score_recencia
        + score_cobertura
        + score_volume
        + score_qualidade
        + score_persistencia,
        1,
    )

    classificacao, emoji = status_score(score)

    return {
        "score": score,
        "classificacao": classificacao,
        "emoji": emoji,
        "confiavel_para_analise": score >= 75,
        "alertas": alertas,
        "detalhes": detalhes,
    }
