"""Pipeline de preparação e ferramentas de auditoria (com dados sintéticos)."""
import pandas as pd
import pytest

from auditoria.auditoria import calcular_pontos, concordancia, kappa_cohen, sortear
from pipeline.preparar_dados import periodo_conclusao, transformar, validar


def _privada(n=40):
    return pd.DataFrame({
        "ID_Egresso": [f"E{i:03d}" for i in range(n)],
        "Curso_de_Graduacao": ["Ciência da Computação", "Engenharia de Software"] * (n // 2),
        "Ano_de_Conclusao": [2012, 2017, 2023, 2025] * (n // 4),
        "Cargo_Atual": ["Desenvolvedor"] * n, "Categoria_Cargo": ["Desenvolvimento de Software"] * n,
        "Tipo_Instituicao": ["Empresa Privada de Tecnologia"] * n, "Genero": ["Feminino"] * n,
        "Faixa_Etaria": ["25–29"] * n, "Local_Nascimento": ["Alegrete, Rio Grande do Sul, Brasil"] * n,
        "Local_de_Trabalho": ["Empresa X"] * n,
        "Indicador_Lideranca": [0, 1] * (n // 2), "Indicador_Progressao": [0] * n,
        "Indicador_Empreendedorismo": [0] * n, "Indicador_Mudanca_Area": [0] * n,
    })


def test_periodos():
    assert [periodo_conclusao(a) for a in (2010, 2014, 2015, 2019, 2020, 2025)] == \
        ["2010–2014", "2010–2014", "2015–2019", "2015–2019", "2020–2025", "2020–2025"]


def test_transformar_remove_identificadores_e_deriva_uf():
    pub = transformar(_privada(), ano_referencia=2026)
    assert "Local_de_Trabalho" not in pub and "Cargo_Atual" not in pub
    assert (pub["UF_Nascimento"] == "RS").all() and (pub["Regiao_Nascimento"] == "Sul").all()
    assert (pub["Tempo_desde_Conclusao"] == 2026 - pub["Ano_de_Conclusao"]).all()


def test_validar_detecta_id_duplicado():
    df = _privada()
    df.loc[1, "ID_Egresso"] = df.loc[0, "ID_Egresso"]
    with pytest.raises(ValueError, match="duplicado"):
        validar(df)


def test_pontuacao_do_protocolo():
    df = pd.DataFrame({"C1_Nome": [1, 1, 0], "C2_UNIPAMPA": [1, 1, 1], "C3_Periodo": [1, 0, 1],
                       "C4_Curso": [0, 0, 1], "C5_Contexto": [1, 1, 1], "C6_Vinculo": [0, 0, 0]})
    out = calcular_pontos(df)
    assert out["Pontos_Validacao"].tolist() == [3, 1, 5]
    assert out["Status_Sugerido"].tolist() == ["A", "AMB", "REJEITAR"]


def test_amostra_estratificada_tem_tamanho_exato_e_reproduzivel():
    df = _privada(80)
    a, b = sortear(df, 20, 1), sortear(df, 20, 1)
    assert len(a) == 20 and a["ID_Egresso"].tolist() == b["ID_Egresso"].tolist()
    assert a["Curso_de_Graduacao"].value_counts().tolist() == [10, 10]


def test_kappa():
    a = pd.Series(["s", "s", "n", "n"])
    assert kappa_cohen(a, a) == 1.0
    assert kappa_cohen(a, pd.Series(["n", "n", "s", "s"])) == -1.0


def test_concordancia_gera_divergencias():
    gab = pd.DataFrame({"ID_Egresso": ["E1", "E2"], "Categoria_Cargo": ["Dados/IA", "Dados/IA"],
                        "Tipo_Instituicao": ["Setor Público"] * 2, "Lideranca_ou_Gerencia": ["Sim", "Não"],
                        "Progressao_Interna": ["Não"] * 2, "Empreendeu": ["Não"] * 2,
                        "Mudanca_de_Area": ["Não"] * 2})
    c2 = gab.copy()
    c2.loc[0, "Categoria_Cargo"] = "Desenvolvimento de Software"
    res, div = concordancia(gab, c2)
    assert len(div) == 1 and div.iloc[0]["Variavel"] == "Categoria_Cargo"
    assert res.set_index("Variável").loc["Categoria_Cargo", "Concordância (%)"] == 50.0
