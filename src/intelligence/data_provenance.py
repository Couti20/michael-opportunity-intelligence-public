from collections import Counter

from config.sources import GREENHOUSE_BOARDS
from config.settings import SOURCE_REGISTRY_FILE, SOURCE_DUPLICATES_FILE
from src.storage.json_store import carregar_json


def gerar_proveniencia():
    registro = carregar_json(
        SOURCE_REGISTRY_FILE,
        {"version": 1, "sources": {}},
    )
    duplicadas = carregar_json(
        SOURCE_DUPLICATES_FILE,
        {"duplicates": [], "ignored_sources": []},
    )

    ignoradas = set(duplicadas.get("ignored_sources", []))
    fontes = {}

    for fonte in GREENHOUSE_BOARDS:
        source_id = f"greenhouse:{fonte['board']}"
        if source_id in ignoradas:
            continue

        fontes[source_id] = {
            "source_id": source_id,
            "ats": "greenhouse",
            "empresa": fonte["name"],
            "origem": "configurada",
        }

    registradas = registro.get("sources", {})

    for source_id, fonte in registradas.items():
        if fonte.get("status") != "validada":
            continue
        if source_id in ignoradas or source_id in fontes:
            continue

        fontes[source_id] = {
            "source_id": source_id,
            "ats": fonte.get("ats", "desconhecido"),
            "empresa": fonte.get(
                "company_hint",
                fonte.get("source_key", source_id),
            ),
            "origem": "discovery",
        }

    por_ats = Counter(fonte["ats"] for fonte in fontes.values())
    fontes_por_ats = {}

    for fonte in fontes.values():
        ats = fonte["ats"]
        fontes_por_ats.setdefault(ats, [])
        fontes_por_ats[ats].append(fonte["empresa"])

    for ats in fontes_por_ats:
        fontes_por_ats[ats] = sorted(
            set(fontes_por_ats[ats]),
            key=str.lower,
        )

    status_discovery = Counter(
        fonte.get("status", "desconhecido")
        for fonte in registradas.values()
    )

    return {
        "fontes_operacionais": len(fontes),
        "por_ats": dict(sorted(por_ats.items())),
        "fontes_por_ats": fontes_por_ats,
        "fontes_descobertas_registradas": len(registradas),
        "status_discovery": dict(status_discovery),
        "duplicadas_identificadas_discovery": status_discovery.get(
            "duplicada", 0
        ),
        "duplicadas_ignoradas_coleta_atual": len(ignoradas),
        "discovery_atualizado_em": registro.get("updated_at"),
        "discovery_engine": {
            "motor": "Tavily",
            "papel": "Descobrir novos boards públicos de recrutamento",
            "fonte_de_vagas": False,
        },
        "metodologia": [
            "Filtro de elegibilidade no Brasil",
            "Filtro de vagas de tecnologia",
            "Extração de skills",
            "Classificação de senioridade",
            "Classificação por área",
            "Detecção de fontes espelhadas",
            "Deduplicação final de vagas",
        ],
    }
