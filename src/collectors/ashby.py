import hashlib
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


def buscar_ashby(board, empresa):
    url = (
        "https://api.ashbyhq.com/"
        "posting-api/job-board/"
        f"{quote(board)}"
        "?includeCompensation=false"
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
        print(f"❌ Ashby / {empresa}: HTTP {erro.code}")
        return None
    except Exception as erro:
        print(f"❌ Ashby / {empresa}: {erro}")
        return None

    vagas = []

    for item in dados.get("jobs", []):
        if item.get("isListed") is False:
            continue

        titulo = (item.get("title") or "").strip()
        locais = []
        principal = item.get("location") or ""
        if principal:
            locais.append(principal)

        for secundario in item.get("secondaryLocations") or []:
            local_sec = secundario.get("location") or ""
            if local_sec and local_sec not in locais:
                locais.append(local_sec)

        postal = (item.get("address") or {}).get("postalAddress") or {}
        pais = postal.get("addressCountry") or ""
        if pais:
            locais.append(pais)

        local = "; ".join(locais)
        descricao = item.get("descriptionPlain") or ""

        if not vaga_no_brasil(local, descricao):
            continue
        if not eh_vaga_tech(titulo, descricao):
            continue

        job_url = item.get("jobUrl") or ""
        identificador = hashlib.sha256(job_url.encode("utf-8")).hexdigest()[:20]

        senioridade = classificar_senioridade(titulo, descricao)
        if item.get("employmentType") == "Intern":
            senioridade = "estagio"

        vagas.append({
            "id": f"ashby:{board}:{identificador}",
            "source": "ashby",
            "source_board": board,
            "company": empresa,
            "title": titulo,
            "location": local,
            "url": job_url,
            "description": descricao,
            "updated_at": item.get("publishedAt"),
            "seniority": senioridade,
            "area": classificar_area(titulo, descricao),
            "skills": extrair_skills(f"{titulo} {descricao}"),
        })

    return vagas
