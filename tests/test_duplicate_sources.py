import unittest

from src.intelligence.duplicate_sources import (
    calcular_sobreposicao,
    detectar_fontes_espelhadas,
)


def vagas(titulos):
    return [{"title": titulo} for titulo in titulos]


class TestDuplicateSources(unittest.TestCase):
    def test_detecta_board_espelhado(self):
        fonte_a = vagas([
            "Backend Engineer",
            "Data Analyst",
            "Data Engineer",
            "ML Engineer",
            "Frontend Developer",
            "QA Engineer",
            "Cloud Engineer",
            "Java Developer",
            "Python Developer",
            "DevOps Engineer",
        ])
        fonte_b = vagas([
            "Backend Engineer",
            "Data Analyst",
            "Data Engineer",
            "ML Engineer",
            "Frontend Developer",
            "QA Engineer",
            "Cloud Engineer",
            "Java Developer",
            "Python Developer",
        ])
        resultado = detectar_fontes_espelhadas({
            "greenhouse:a": fonte_a,
            "greenhouse:b": fonte_b,
        })
        self.assertEqual(len(resultado["duplicate_source_ids"]), 1)

    def test_nao_confunde_empresas_normais(self):
        fonte_a = vagas([
            "Backend Engineer",
            "Data Analyst",
            "Data Engineer",
            "ML Engineer",
            "Frontend Developer",
            "QA Engineer",
        ])
        fonte_b = vagas([
            "Product Manager",
            "Cloud Architect",
            "Security Engineer",
            "Mobile Engineer",
            "React Developer",
            "Database Engineer",
        ])
        resultado = detectar_fontes_espelhadas({
            "greenhouse:a": fonte_a,
            "ashby:b": fonte_b,
        })
        self.assertEqual(resultado["duplicate_source_ids"], [])

    def test_fonte_preferida_e_canonica(self):
        mesmos = vagas([
            "Software Engineer",
            "Data Engineer",
            "ML Engineer",
            "Backend Engineer",
            "Frontend Engineer",
            "QA Engineer",
        ])
        resultado = detectar_fontes_espelhadas(
            {
                "greenhouse:principal": mesmos,
                "greenhouse:espelho": mesmos,
            },
            fontes_preferidas={"greenhouse:principal"},
        )
        duplicata = resultado["duplicates"][0]
        self.assertEqual(duplicata["canonical"], "greenhouse:principal")
        self.assertEqual(duplicata["duplicate"], "greenhouse:espelho")

    def test_calcula_sobreposicao(self):
        a = vagas(["A", "B", "C", "D", "E"])
        b = vagas(["A", "B", "C", "D", "E", "F"])
        resultado = calcular_sobreposicao(a, b)
        self.assertEqual(resultado["comuns"], 5)
        self.assertEqual(resultado["sobreposicao"], 1.0)


if __name__ == "__main__":
    unittest.main()
