import unittest

from src.discovery.source_parser import identificar_fonte


class TestSourceParser(unittest.TestCase):
    def test_greenhouse(self):
        resultado = identificar_fonte(
            "https://job-boards.greenhouse.io/empresa/jobs/123"
        )
        self.assertEqual(resultado["source_id"], "greenhouse:empresa")

    def test_greenhouse_embed(self):
        resultado = identificar_fonte(
            "https://boards.greenhouse.io/embed/job_board?for=empresa"
        )
        self.assertEqual(resultado["source_id"], "greenhouse:empresa")

    def test_lever(self):
        resultado = identificar_fonte(
            "https://jobs.lever.co/empresa/abc123"
        )
        self.assertEqual(resultado["source_id"], "lever:empresa")

    def test_ashby(self):
        resultado = identificar_fonte(
            "https://jobs.ashbyhq.com/empresa/abc123"
        )
        self.assertEqual(resultado["source_id"], "ashby:empresa")

    def test_workable(self):
        resultado = identificar_fonte(
            "https://apply.workable.com/empresa/j/ABC123/"
        )
        self.assertEqual(resultado["source_id"], "workable:empresa")


if __name__ == "__main__":
    unittest.main()
