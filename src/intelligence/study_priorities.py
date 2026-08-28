from collections import Counter

from config.settings import CURRENT_JOBS_FILE
from config.career_profile import (
    AREAS_ALVO,
    SENIORIDADES_ALVO,
    SKILLS_JA_ESTUDADAS,
    SKILLS_FOCO,
    ALINHAMENTO_SKILLS,
)
from src.intelligence.trends import gerar_tendencias
from src.storage.json_store import carregar_json


def normalizar(valor, maximo):
    if not maximo:
        return 0.0
    return min(1.0, valor / maximo)


def classificar_prioridade(score):
    if score >= 75:
        return "máxima"
    if score >= 55:
        return "alta"
    if score >= 35:
        return "média"
    return "observar"


def calcular_prioridades(vagas, tendencias=None, limite=10):
    tendencias = tendencias or {"ready": False, "snapshots": 0}

    global_skills = Counter()
    entrada_skills = Counter()
    alvo_skills = Counter()

    vagas_entrada = 0
    vagas_alvo = 0

    for vaga in vagas:
        skills = set(vaga.get("skills", []))
        if not skills:
            continue

        global_skills.update(skills)

        if vaga.get("seniority") in SENIORIDADES_ALVO:
            vagas_entrada += 1
            entrada_skills.update(skills)

        peso_area = AREAS_ALVO.get(vaga.get("area"), 0)
        if peso_area > 0:
            vagas_alvo += 1
            for skill in skills:
                alvo_skills[skill] += peso_area

    tendencia_skills = {}
    if tendencias.get("ready"):
        for item in tendencias.get("skills", []):
            tendencia_skills[item["nome"]] = max(0, item.get("delta", 0))

    max_global = max(global_skills.values(), default=0)
    max_entrada = max(entrada_skills.values(), default=0)
    max_alvo = max(alvo_skills.values(), default=0)
    max_tendencia = max(tendencia_skills.values(), default=0)

    if tendencias.get("ready"):
        pesos = {
            "global": 0.30,
            "entrada": 0.30,
            "alvo": 0.25,
            "tendencia": 0.15,
        }
    else:
        pesos = {
            "global": 0.35,
            "entrada": 0.35,
            "alvo": 0.30,
            "tendencia": 0.00,
        }

    candidatos = (
        set(global_skills)
        | set(entrada_skills)
        | set(alvo_skills)
        | set(tendencia_skills)
    )

    resultados = []

    for skill in candidatos:
        demanda = global_skills[skill]
        entrada = entrada_skills[skill]
        alvo = alvo_skills[skill]
        crescimento = tendencia_skills.get(skill, 0)

        if demanda < 2 and entrada == 0 and skill not in SKILLS_FOCO:
            continue

        score_mercado = (
            normalizar(demanda, max_global) * pesos["global"] * 100
            + normalizar(entrada, max_entrada) * pesos["entrada"] * 100
            + normalizar(alvo, max_alvo) * pesos["alvo"] * 100
            + normalizar(crescimento, max_tendencia)
            * pesos["tendencia"]
            * 100
        )
        score_mercado = min(100, round(score_mercado, 1))

        alinhamento = ALINHAMENTO_SKILLS.get(skill, 0.50)
        score_fit = round(alinhamento * 100, 1)
        score = min(100, round(score_mercado * 0.65 + score_fit * 0.35, 1))

        resultados.append({
            "skill": skill,
            "score": score,
            "score_mercado": score_mercado,
            "score_fit": score_fit,
            "alinhamento": alinhamento,
            "prioridade": classificar_prioridade(score),
            "acao": "aprofundar" if skill in SKILLS_JA_ESTUDADAS else "aprender",
            "mercado": demanda,
            "entrada": entrada,
            "areas_alvo": round(alvo, 1),
            "crescimento": crescimento,
            "foco_pessoal": skill in SKILLS_FOCO,
        })

    resultados.sort(
        key=lambda item: (item["score"], item["entrada"], item["mercado"]),
        reverse=True,
    )

    return {
        "total_vagas": len(vagas),
        "vagas_entrada": vagas_entrada,
        "vagas_areas_alvo": vagas_alvo,
        "trend_ready": bool(tendencias.get("ready")),
        "trend_snapshots": tendencias.get("snapshots", 0),
        "metodologia": {
            "demanda_geral": int(pesos["global"] * 100),
            "mercado_entrada": int(pesos["entrada"] * 100),
            "areas_alvo": int(pesos["alvo"] * 100),
            "tendencia": int(pesos["tendencia"] * 100),
        },
        "recomendacoes": resultados[:limite],
    }


def gerar_prioridades_estudo():
    vagas = carregar_json(CURRENT_JOBS_FILE, [])
    return calcular_prioridades(vagas, gerar_tendencias())
