import html
import json
import urllib.request

from html.parser import HTMLParser

from src.intelligence.classifier import (
    vaga_no_brasil,
    eh_vaga_tech,
    extrair_skills,
    classificar_senioridade,
    classificar_area,
)


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []

    def handle_data(self, data):
        if data.strip():
            self.partes.append(data.strip())


def limpar_html(conteudo):
    if not conteudo:
        return ""

    parser = HTMLTextExtractor()
    try:
        parser.feed(html.unescape(conteudo))
        return " ".join(parser.partes)
    except Exception:
        return html.unescape(conteudo)


def buscar_board(board, empresa):
    url = (
        "https://boards-api.greenhouse.io/"
        f"v1/boards/{board}/jobs"
        "?content=true"
    )

    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Michael-Opportunity-Intelligence/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            dados = json.load(resposta)
    except Exception as erro:
        print(f"❌ Greenhouse / {empresa}: {erro}")
        return []

    vagas = []

    for item in dados.get("jobs", []):
        titulo = (item.get("title") or "").strip()
        local = (item.get("location", {}).get("name") or "").strip()
        descricao = limpar_html(item.get("content") or "")

        if not vaga_no_brasil(local, descricao):
            continue
        if not eh_vaga_tech(titulo, descricao):
            continue

        vagas.append({
            "id": f"greenhouse:{board}:{item['id']}",
            "source": "greenhouse",
            "source_board": board,
            "company": empresa,
            "title": titulo,
            "location": local,
            "url": item.get("absolute_url", ""),
            "description": descricao,
            "updated_at": item.get("updated_at"),
            "seniority": classificar_senioridade(titulo, descricao),
            "area": classificar_area(titulo, descricao),
            "skills": extrair_skills(f"{titulo} {descricao}"),
        })

    return vagas
