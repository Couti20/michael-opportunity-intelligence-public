from datetime import datetime
from zoneinfo import ZoneInfo

from config.sources import GREENHOUSE_BOARDS
from config.settings import TIMEZONE, SOURCE_DUPLICATES_FILE
from src.collectors.greenhouse import buscar_board
from src.collectors.lever import buscar_lever
from src.collectors.ashby import buscar_ashby
from src.discovery.registry import fontes_validadas
from src.intelligence.duplicate_sources import detectar_fontes_espelhadas
from src.storage.json_store import salvar_json


def coletar_mercado():
    fontes_coletadas = {}
    fontes_executadas = set()
    fontes_preferidas = set()

    for fonte in GREENHOUSE_BOARDS:
        source_id = f"greenhouse:{fonte['board']}"
        fontes_executadas.add(source_id)
        fontes_preferidas.add(source_id)

        vagas = buscar_board(fonte["board"], fonte["name"])
        fontes_coletadas[source_id] = vagas
        print(f"📥 Greenhouse / {fonte['name']}: {len(vagas)}")

    for fonte in fontes_validadas():
        source_id = fonte["source_id"]
        if source_id in fontes_executadas:
            continue

        ats = fonte["ats"]
        chave = fonte["source_key"]
        empresa = fonte.get("company_hint", chave)

        if ats == "greenhouse":
            vagas = buscar_board(chave, empresa)
        elif ats == "lever":
            vagas = buscar_lever(chave, empresa)
        elif ats == "ashby":
            vagas = buscar_ashby(chave, empresa)
        else:
            continue

        fontes_executadas.add(source_id)

        if vagas is None:
            print(f"⚠️ {ats} / {empresa}: fonte indisponível")
            continue

        fontes_coletadas[source_id] = vagas
        print(f"📥 {ats.title()} / {empresa}: {len(vagas)}")

    analise = detectar_fontes_espelhadas(
        fontes_coletadas,
        fontes_preferidas,
    )

    duplicadas = set(analise["duplicate_source_ids"])

    for item in analise["duplicates"]:
        print()
        print("🚨 Fonte espelhada detectada:")
        print(f"   ✅ Mantida: {item['canonical']}")
        print(f"   🚫 Ignorada: {item['duplicate']}")
        print(f"   📊 Sobreposição: {item['overlap'] * 100:.1f}%")
        print(f"   🧬 Títulos iguais: {item['common_titles']}")

    salvar_json(
        SOURCE_DUPLICATES_FILE,
        {
            "updated_at": datetime.now(
                ZoneInfo(TIMEZONE)
            ).isoformat(timespec="seconds"),
            "duplicates": analise["duplicates"],
            "ignored_sources": sorted(duplicadas),
        },
    )

    todas = []
    for source_id, vagas in fontes_coletadas.items():
        if source_id in duplicadas:
            continue
        todas.extend(vagas)

    unicas = {}
    for vaga in todas:
        unicas[vaga["id"]] = vaga

    return list(unicas.values())
