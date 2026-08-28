from src.intelligence.classifier import normalizar


MIN_VAGAS_COMPARACAO = 5
MIN_TITULOS_COMUNS = 5
LIMIAR_SOBREPOSICAO = 0.85


def assinatura_titulo(vaga):
    return normalizar(vaga.get("title", ""))


def titulos_da_fonte(vagas):
    return {
        assinatura_titulo(vaga)
        for vaga in vagas
        if assinatura_titulo(vaga)
    }


def calcular_sobreposicao(vagas_a, vagas_b):
    titulos_a = titulos_da_fonte(vagas_a)
    titulos_b = titulos_da_fonte(vagas_b)

    if (
        len(titulos_a) < MIN_VAGAS_COMPARACAO
        or len(titulos_b) < MIN_VAGAS_COMPARACAO
    ):
        return {
            "comuns": 0,
            "sobreposicao": 0.0,
            "jaccard": 0.0,
        }

    comuns = titulos_a & titulos_b
    uniao = titulos_a | titulos_b
    menor_base = min(len(titulos_a), len(titulos_b))

    return {
        "comuns": len(comuns),
        "sobreposicao": len(comuns) / menor_base if menor_base else 0.0,
        "jaccard": len(comuns) / len(uniao) if uniao else 0.0,
    }


def sao_fontes_espelhadas(vagas_a, vagas_b):
    metricas = calcular_sobreposicao(vagas_a, vagas_b)
    return (
        metricas["comuns"] >= MIN_TITULOS_COMUNS
        and metricas["sobreposicao"] >= LIMIAR_SOBREPOSICAO
    )


def detectar_fontes_espelhadas(fontes, fontes_preferidas=None):
    fontes_preferidas = fontes_preferidas or set()

    ordenadas = sorted(
        fontes.items(),
        key=lambda item: (
            0 if item[0] in fontes_preferidas else 1,
            -len(item[1]),
            item[0],
        ),
    )

    duplicadas = set()
    resultados = []

    for indice, (source_a, vagas_a) in enumerate(ordenadas):
        if source_a in duplicadas:
            continue

        for source_b, vagas_b in ordenadas[indice + 1:]:
            if source_b in duplicadas:
                continue

            metricas = calcular_sobreposicao(vagas_a, vagas_b)

            if not (
                metricas["comuns"] >= MIN_TITULOS_COMUNS
                and metricas["sobreposicao"] >= LIMIAR_SOBREPOSICAO
            ):
                continue

            duplicadas.add(source_b)
            resultados.append({
                "canonical": source_a,
                "duplicate": source_b,
                "common_titles": metricas["comuns"],
                "overlap": round(metricas["sobreposicao"], 4),
                "jaccard": round(metricas["jaccard"], 4),
                "canonical_jobs": len(vagas_a),
                "duplicate_jobs": len(vagas_b),
            })

    return {
        "duplicates": resultados,
        "duplicate_source_ids": sorted(duplicadas),
    }
