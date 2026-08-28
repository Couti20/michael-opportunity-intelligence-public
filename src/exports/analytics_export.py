import csv
import json
from pathlib import Path

from config.settings import (
    JOBS_FILE,
    CURRENT_JOBS_FILE,
    SKILLS_DAILY_FILE,
    MARKET_DAILY_FILE,
    JOBS_CURRENT_CSV,
    JOBS_HISTORY_CSV,
    SKILLS_DAILY_CSV,
    AREAS_DAILY_CSV,
    COMPANIES_DAILY_CSV,
    MARKET_DAILY_CSV,
)


def ler_json(caminho, padrao=None):
    caminho = Path(caminho)
    if not caminho.exists():
        return padrao if padrao is not None else []
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return padrao if padrao is not None else []


def ler_jsonl(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return []

    registros = []
    with caminho.open("r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            try:
                registros.append(json.loads(linha))
            except json.JSONDecodeError:
                continue
    return registros


def escrever_csv(caminho, campos, registros):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(registros)


def normalizar_skills(skills):
    if not skills:
        return ""
    if isinstance(skills, list):
        return " | ".join(str(skill) for skill in skills)
    return str(skills)


def exportar_vagas_atuais():
    vagas = ler_json(CURRENT_JOBS_FILE, [])
    registros = [
        {
            "id": vaga.get("id", ""),
            "empresa": vaga.get("company", ""),
            "titulo": vaga.get("title", ""),
            "localizacao": vaga.get("location", ""),
            "senioridade": vaga.get("seniority", ""),
            "area": vaga.get("area", ""),
            "skills": normalizar_skills(vaga.get("skills")),
            "url": vaga.get("url", ""),
        }
        for vaga in vagas
    ]

    escrever_csv(
        JOBS_CURRENT_CSV,
        [
            "id",
            "empresa",
            "titulo",
            "localizacao",
            "senioridade",
            "area",
            "skills",
            "url",
        ],
        registros,
    )
    return len(registros)


def exportar_historico_vagas():
    vagas = ler_jsonl(JOBS_FILE)
    registros = [
        {
            "id": vaga.get("id", ""),
            "empresa": vaga.get("company", ""),
            "titulo": vaga.get("title", ""),
            "localizacao": vaga.get("location", ""),
            "senioridade": vaga.get("seniority", ""),
            "area": vaga.get("area", ""),
            "skills": normalizar_skills(vaga.get("skills")),
            "first_seen": vaga.get("first_seen", ""),
            "url": vaga.get("url", ""),
        }
        for vaga in vagas
    ]

    escrever_csv(
        JOBS_HISTORY_CSV,
        [
            "id",
            "empresa",
            "titulo",
            "localizacao",
            "senioridade",
            "area",
            "skills",
            "first_seen",
            "url",
        ],
        registros,
    )
    return len(registros)


def exportar_skills_diarias():
    snapshots = ler_jsonl(SKILLS_DAILY_FILE)
    registros = []

    for snapshot in snapshots:
        total_jobs = snapshot.get("total_jobs", 0) or 0
        for skill, total in snapshot.get("skills", {}).items():
            percentual = round(total / total_jobs * 100, 2) if total_jobs else 0
            registros.append({
                "data": snapshot.get("date", ""),
                "skill": skill,
                "vagas": total,
                "total_vagas": total_jobs,
                "percentual": percentual,
                "fontes": snapshot.get("source_count", ""),
                "coverage_signature": snapshot.get("coverage_signature", ""),
                "schema_version": snapshot.get("schema_version", ""),
                "classifier_version": snapshot.get("classifier_version", ""),
            })

    escrever_csv(
        SKILLS_DAILY_CSV,
        [
            "data",
            "skill",
            "vagas",
            "total_vagas",
            "percentual",
            "fontes",
            "coverage_signature",
            "schema_version",
            "classifier_version",
        ],
        registros,
    )
    return len(registros)


def exportar_areas_diarias():
    snapshots = ler_jsonl(MARKET_DAILY_FILE)
    registros = []

    for snapshot in snapshots:
        total_jobs = snapshot.get("total_jobs", 0) or 0
        for area, total in snapshot.get("areas", {}).items():
            percentual = round(total / total_jobs * 100, 2) if total_jobs else 0
            registros.append({
                "data": snapshot.get("date", ""),
                "area": area,
                "vagas": total,
                "total_vagas": total_jobs,
                "percentual": percentual,
                "coverage_signature": snapshot.get("coverage_signature", ""),
            })

    escrever_csv(
        AREAS_DAILY_CSV,
        [
            "data",
            "area",
            "vagas",
            "total_vagas",
            "percentual",
            "coverage_signature",
        ],
        registros,
    )
    return len(registros)


def exportar_empresas_diarias():
    snapshots = ler_jsonl(MARKET_DAILY_FILE)
    registros = []

    for snapshot in snapshots:
        total_jobs = snapshot.get("total_jobs", 0) or 0
        for empresa, total in snapshot.get("companies", {}).items():
            percentual = round(total / total_jobs * 100, 2) if total_jobs else 0
            registros.append({
                "data": snapshot.get("date", ""),
                "empresa": empresa,
                "vagas": total,
                "total_vagas": total_jobs,
                "percentual": percentual,
                "coverage_signature": snapshot.get("coverage_signature", ""),
            })

    escrever_csv(
        COMPANIES_DAILY_CSV,
        [
            "data",
            "empresa",
            "vagas",
            "total_vagas",
            "percentual",
            "coverage_signature",
        ],
        registros,
    )
    return len(registros)


def exportar_mercado_diario():
    snapshots = ler_jsonl(MARKET_DAILY_FILE)
    registros = []

    for snapshot in snapshots:
        senioridades = snapshot.get("seniorities", {})
        registros.append({
            "data": snapshot.get("date", ""),
            "atualizado_em": snapshot.get("updated_at", ""),
            "vagas_ativas": snapshot.get("total_jobs", 0),
            "vagas_novas": snapshot.get("new_jobs", 0),
            "fontes": snapshot.get("source_count", ""),
            "estagio": senioridades.get("estagio", 0),
            "junior": senioridades.get("junior", 0),
            "pleno": senioridades.get("pleno", 0),
            "senior": senioridades.get("senior", 0),
            "nao_informado": senioridades.get("nao_informado", 0),
            "coverage_signature": snapshot.get("coverage_signature", ""),
            "schema_version": snapshot.get("schema_version", ""),
            "classifier_version": snapshot.get("classifier_version", ""),
        })

    escrever_csv(
        MARKET_DAILY_CSV,
        [
            "data",
            "atualizado_em",
            "vagas_ativas",
            "vagas_novas",
            "fontes",
            "estagio",
            "junior",
            "pleno",
            "senior",
            "nao_informado",
            "coverage_signature",
            "schema_version",
            "classifier_version",
        ],
        registros,
    )
    return len(registros)


def gerar_exports():
    return {
        "jobs_current": exportar_vagas_atuais(),
        "jobs_history": exportar_historico_vagas(),
        "skills_daily": exportar_skills_diarias(),
        "areas_daily": exportar_areas_diarias(),
        "companies_daily": exportar_empresas_diarias(),
        "market_daily": exportar_mercado_diario(),
    }
