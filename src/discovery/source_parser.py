from urllib.parse import urlparse, parse_qs, unquote


def identificar_fonte(url):
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower().removeprefix("www.")
        partes = [parte for parte in parsed.path.split("/") if parte]
    except Exception:
        return None

    if host in {"job-boards.greenhouse.io", "boards.greenhouse.io"}:
        if len(partes) >= 2 and partes[0] == "embed":
            parametros = parse_qs(parsed.query)
            valores = parametros.get("for", [])
            if not valores:
                return None
            board = valores[0].strip()
        else:
            if not partes:
                return None
            board = partes[0]

        if board.lower() in {"embed", "jobs", "job_board"}:
            return None

        return {
            "ats": "greenhouse",
            "source_key": board,
            "source_id": f"greenhouse:{board}",
        }

    if host == "jobs.lever.co":
        if not partes:
            return None
        empresa = unquote(partes[0])
        return {
            "ats": "lever",
            "source_key": empresa,
            "source_id": f"lever:{empresa}",
        }

    if host == "jobs.ashbyhq.com":
        if not partes:
            return None
        empresa = unquote(partes[0])
        return {
            "ats": "ashby",
            "source_key": empresa,
            "source_id": f"ashby:{empresa}",
        }

    if host == "apply.workable.com":
        if not partes:
            return None
        empresa = unquote(partes[0])
        return {
            "ats": "workable",
            "source_key": empresa,
            "source_id": f"workable:{empresa}",
        }

    return None
