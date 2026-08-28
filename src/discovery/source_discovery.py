from datetime import datetime
from zoneinfo import ZoneInfo

from config.discovery import DISCOVERY_SEARCHES, TAVILY_MONTHLY_BUDGET
from config.settings import TIMEZONE, SOURCE_REGISTRY_FILE, TAVILY_BUDGET_FILE
from config.sources import GREENHOUSE_BOARDS
from src.collectors.greenhouse import buscar_board
from src.discovery.tavily_client import buscar_tavily
from src.discovery.source_parser import identificar_fonte
from src.storage.json_store import carregar_json, salvar_json


def agora():
    return datetime.now(ZoneInfo(TIMEZONE)).isoformat(timespec="seconds")


def fontes_greenhouse_conhecidas():
    return {item["board"] for item in GREENHOUSE_BOARDS}


def validar_fonte(candidato):
    ats = candidato["ats"]

    if ats == "greenhouse":
        vagas = buscar_board(
            candidato["source_key"],
            candidato["company_hint"],
        )

        if vagas:
            return {
                "status": "validada",
                "tech_br_jobs": len(vagas),
            }

        return {
            "status": "sem_vagas_tech_br",
            "tech_br_jobs": 0,
        }

    return {
        "status": "pendente_coletor",
        "tech_br_jobs": None,
    }


def executar_descoberta():
    print("📡 Source Discovery Engine")

    conhecidos_greenhouse = fontes_greenhouse_conhecidas()
    registro = carregar_json(
        SOURCE_REGISTRY_FILE,
        {"version": 1, "sources": {}},
    )
    fontes = registro.setdefault("sources", {})

    resultados_unicos = {}
    creditos_execucao = 0

    for busca in DISCOVERY_SEARCHES:
        print(f"🔎 {busca['name']}...")
        resultados, creditos = buscar_tavily(
            busca["query"],
            busca["domains"],
        )
        creditos_execucao += creditos

        for resultado in resultados:
            url = (resultado.get("url") or "").strip()
            if not url:
                continue

            chave = url.lower()
            if chave in resultados_unicos:
                continue

            resultados_unicos[chave] = {
                **resultado,
                "_query": busca["name"],
            }

    novas = 0
    validadas = 0

    for resultado in resultados_unicos.values():
        url = resultado["url"]
        fonte = identificar_fonte(url)
        if not fonte:
            continue

        if (
            fonte["ats"] == "greenhouse"
            and fonte["source_key"] in conhecidos_greenhouse
        ):
            continue

        source_id = fonte["source_id"]
        existente = fontes.get(source_id)

        if existente:
            existente["last_seen"] = agora()
            existente["search_score"] = resultado.get("score")
            consultas = set(existente.get("queries", []))
            consultas.add(resultado["_query"])
            existente["queries"] = sorted(consultas)
            continue

        candidato = {
            **fonte,
            "company_hint": fonte["source_key"]
                .replace("-", " ")
                .replace("_", " ")
                .title(),
            "sample_title": resultado.get("title") or fonte["source_key"],
            "sample_url": url,
            "search_score": resultado.get("score"),
            "first_seen": agora(),
            "last_seen": agora(),
            "queries": [resultado["_query"]],
        }

        candidato.update(validar_fonte(candidato))
        fontes[source_id] = candidato
        novas += 1
        if candidato["status"] == "validada":
            validadas += 1

    registro["updated_at"] = agora()
    salvar_json(SOURCE_REGISTRY_FILE, registro)

    budget = carregar_json(TAVILY_BUDGET_FILE, {})

    print(f"🆕 Novas fontes: {novas}")
    print(f"✅ Validadas: {validadas}")
    print(f"💳 Créditos nesta execução: {creditos_execucao}")
    print(
        "📊 Orçamento Tavily: "
        f"{budget.get('credits_used', 0)}/{TAVILY_MONTHLY_BUDGET}"
    )
