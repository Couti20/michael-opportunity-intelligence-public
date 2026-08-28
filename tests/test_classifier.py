import unittest

from src.intelligence.classifier import (
    extrair_skills,
    classificar_area,
    classificar_senioridade,
)


class TestClassifier(unittest.TestCase):
    def test_nao_confundir_ios_com_solutions(self):
        skills = extrair_skills(
            "Solutions Engineer working with customers"
        )
        self.assertNotIn("ios", skills)

    def test_nao_confundir_rust_com_trust(self):
        skills = extrair_skills(
            "Build trust with customers"
        )
        self.assertNotIn("rust", skills)

    def test_nao_confundir_java_com_javascript(self):
        skills = extrair_skills(
            "React and JavaScript developer"
        )
        self.assertIn("javascript", skills)
        self.assertNotIn("java", skills)

    def test_java_real(self):
        skills = extrair_skills(
            "Java Developer with Spring Boot"
        )
        self.assertIn("java", skills)

    def test_software_java_nao_vira_ia(self):
        area = classificar_area(
            "Senior Software Engineer, Java",
            "Product uses machine learning internally.",
        )
        self.assertEqual(area, "Engenharia de Software")

    def test_visao_computacional(self):
        area = classificar_area(
            "Computer Vision Engineer",
            "Python OpenCV PyTorch",
        )
        self.assertEqual(area, "Visão Computacional")

    def test_associate_como_entrada(self):
        nivel = classificar_senioridade(
            "Associate Java Developer"
        )
        self.assertEqual(nivel, "junior")


if __name__ == "__main__":
    unittest.main()
