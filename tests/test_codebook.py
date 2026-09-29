"""Regras do livro de códigos (protocolo, Etapa 6)."""
import pytest

from pipeline.codebook import classificar_cargo, normalizar


@pytest.mark.parametrize("cargo, esperado", [
    ("Desenvolvedor Full Stack", "Desenvolvimento de Software"),
    ("Engenheiro de Software Sênior", "Desenvolvimento de Software"),
    ("Tech Lead", "Desenvolvimento de Software"),          # liderança técnica fica na área técnica
    ("Líder Técnico", "Desenvolvimento de Software"),
    ("Gerente de Engenharia de Software", "Gestão/Liderança"),  # gestão de pessoas vence a área
    ("CEO", "Gestão/Liderança"),
    ("Cientista de dados Senior", "Dados/IA"),
    ("Analista QA Pleno", "Infraestrutura/DevOps/Qualidade"),
    ("Product Owner", "Produto/UX/Agilidade"),
    ("Professor", "Ensino/Pesquisa"),
    ("Posdoc", "Ensino/Pesquisa"),
    ("Analista de TI", "Outros em Computação/TI"),
    ("Engenheiro Civil", "Área não relacionada à Computação"),
    ("Auxiliar administrativo", "Área não relacionada à Computação"),
    ("Sem Informação", "Sem Informação"),
])
def test_classificacao(cargo, esperado):
    assert classificar_cargo(cargo) == esperado


def test_normalizar():
    assert normalizar("  Líder   Técnico/Dev ") == "lider tecnico dev"
    assert normalizar(None) == ""
