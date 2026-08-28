import json
import os
import tempfile
from pathlib import Path


def carregar_json(caminho, padrao=None):
    caminho = Path(caminho)
    if padrao is None:
        padrao = {}
    if not caminho.exists():
        return padrao

    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return padrao


def salvar_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=caminho.parent,
        delete=False,
    ) as temporario:
        temporario.write(conteudo)
        temporario.flush()
        os.fsync(temporario.fileno())
        nome_temp = temporario.name

    os.replace(nome_temp, caminho)


def ler_jsonl(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return []

    registros = []
    with caminho.open("r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            try:
                registros.append(json.loads(linha))
            except json.JSONDecodeError:
                continue

    return registros


def adicionar_jsonl(caminho, registro):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False))
        arquivo.write("\n")


def adicionar_varios_jsonl(caminho, registros):
    if not registros:
        return

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("a", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False))
            arquivo.write("\n")


def upsert_jsonl(caminho, novos_registros, campos_chave):
    caminho = Path(caminho)
    existentes = ler_jsonl(caminho)
    indice = {}

    for registro in existentes:
        chave = tuple(registro.get(campo) for campo in campos_chave)
        indice[chave] = registro

    for registro in novos_registros:
        chave = tuple(registro.get(campo) for campo in campos_chave)
        indice[chave] = registro

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=caminho.parent,
        delete=False,
    ) as temporario:
        for registro in indice.values():
            temporario.write(json.dumps(registro, ensure_ascii=False))
            temporario.write("\n")
        temporario.flush()
        os.fsync(temporario.fileno())
        nome_temp = temporario.name

    os.replace(nome_temp, caminho)


def contar_jsonl(caminho):
    return len(ler_jsonl(caminho))
