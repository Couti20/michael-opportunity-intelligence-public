import json
import urllib.error
import urllib.request
from urllib.parse import quote

from src.intelligence.classifier import (
    vaga_no_brasil,
    eh_vaga_tech,
    extrair_skills,
    classificar_senioridade,
    classificar_area,
)


def buscar_lever(site, empresa):
    url = (
        "https://api.lever.co/"
        f"v0/postings/{quote(site)}"
        "?mode=json"
    )

    requisicao = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Michael-Opportunity-Intelligence/1.0",
        },
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            dados = json.load(resposta)
    except urllib.error.HTTPError as erro:
        print(f"❌ Lever / {empresa}: HTTP {erro.code}")
        return None
    except Exception as erro:
        print(f"❌ Lever / {empresa}: {erro}")
        return None

    vagas = []

    for item in dados:
        titulo = (item.get("text") or "").strip()
        categorias = item.get("categories") or {}
        locais = []

        local_principal = categorias.get("location") or ""
        if local_principal:
            locais.append(local_principal)

        for local in categorias.get("allLocations") or []:
            if local and local not in locais:
                locais.append(local)

        local = "; ".join(locais)
        descricao_partes = [
            item.get("descriptionPlain") or "",
            item.get("additionalPlain") or "",
        ]

        for bloco in item.get("lists") or []:
            descricao_partes.append(bloco.get("text", ""))
            descricao_partes.append(bloco.get("content", ""))

        descricao = " ".join(
            parte for parte in descricao_partes if parte
        )

        pais = (item.get("country") or "").upper()
        brasil = pais == "BR" or vaga_no_brasil(local, descricao)

        if not brasil:
            continue
        if not eh_vaga_tech(titulo, descricao):
            continue

        vagas.append({
            "id": f"lever:{site}:{item['id']}",
            "source": "lever",
            "source_board": site,
            "company": empresa,
            "title": titulo,
            "location": local,
            "url": item.get("hostedUrl", ""),
            "description": descricao,
            "updated_at": None,
            "seniority": classificar_senioridade(titulo, descricao),
            "area": classificar_area(titulo, descricao),
            "skills": extrair_skills(f"{titulo} {descricao}"),
        })

    return vagas
