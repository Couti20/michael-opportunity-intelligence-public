import tempfile
import unittest
from pathlib import Path

from src.storage.json_store import (
    carregar_json,
    salvar_json,
    adicionar_jsonl,
    contar_jsonl,
)


class TestJsonStore(unittest.TestCase):
    def test_json(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "teste.json"
            dados = {"python": 10}
            salvar_json(arquivo, dados)
            carregado = carregar_json(arquivo)
            self.assertEqual(carregado, dados)

    def test_jsonl(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "teste.jsonl"
            adicionar_jsonl(arquivo, {"skill": "python"})
            adicionar_jsonl(arquivo, {"skill": "pytorch"})
            self.assertEqual(contar_jsonl(arquivo), 2)


if __name__ == "__main__":
    unittest.main()
