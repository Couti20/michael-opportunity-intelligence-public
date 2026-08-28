from config.settings import SOURCE_REGISTRY_FILE
from src.storage.json_store import carregar_json


def fontes_validadas():
    dados = carregar_json(
        SOURCE_REGISTRY_FILE,
        {"version": 1, "sources": {}},
    )

    resultado = []

    for fonte in dados.get("sources", {}).values():
        if fonte.get("status") != "validada":
            continue
        resultado.append(fonte)

    return resultado
