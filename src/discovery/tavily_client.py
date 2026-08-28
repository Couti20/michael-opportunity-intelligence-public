import json
import os
import urllib.error
import urllib.request

from datetime import datetime
from zoneinfo import ZoneInfo

from config.settings import TIMEZONE, TAVILY_BUDGET_FILE
from config.discovery import TAVILY_MONTHLY_BUDGET, TAVILY_MAX_RESULTS
from src.storage.json_store import carregar_json, salvar_json


TAVILY_URL = "https://api.tavily.com/search"


def mes_atual():
    return datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m")


def carregar_orcamento():
    mes = mes_atual()
    dados = carregar_json(TAVILY_BUDGET_FILE, {})

    if dados.get("month") != mes:
        dados = {
            "month": mes,
            "credits_used": 0,
            "searches": 0,
        }

    return dados


def salvar_orcamento(dados):
    dados["updated_at"] = datetime.now(
        ZoneInfo(TIMEZONE)
    ).isoformat(timespec="seconds")
    salvar_json(TAVILY_BUDGET_FILE, dados)


def buscar_tavily(consulta, domains):
    api_key = os.environ.get("TAVILY_DISCOVERY_API_KEY")

    if not api_key:
        raise RuntimeError("TAVILY_DISCOVERY_API_KEY não configurada.")

    budget = carregar_orcamento()

    if budget["credits_used"] >= TAVILY_MONTHLY_BUDGET:
        print("🛑 Limite mensal local da Tavily atingido.")
        return [], 0

    payload = json.dumps({
        "query": consulta,
        "search_depth": "basic",
        "topic": "general",
        "max_results": TAVILY_MAX_RESULTS,
        "include_domains": domains,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
        "include_usage": True,
        "auto_parameters": False,
    }).encode("utf-8")

    requisicao = urllib.request.Request(
        TAVILY_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            dados = json.load(resposta)
    except urllib.error.HTTPError as erro:
        corpo = erro.read().decode("utf-8", errors="replace")
        print(f"❌ Tavily HTTP {erro.code}")
        print(corpo[:500])
        return [], 0
    except Exception as erro:
        print(f"❌ Tavily: {erro}")
        return [], 0

    creditos = dados.get("usage", {}).get("credits") or 1
    budget["credits_used"] += creditos
    budget["searches"] += 1
    salvar_orcamento(budget)

    return dados.get("results", []), creditos
