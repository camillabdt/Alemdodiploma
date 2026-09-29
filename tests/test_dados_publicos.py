"""A base pública precisa ter o formato esperado e nenhum identificador."""
import pandas as pd
import pytest

from app.core.data import COLUNAS_ESPERADAS, COLUNAS_PROIBIDAS, ler_dados
from app.core.config import CURSOS, INDICADORES, PERIODOS


@pytest.fixture(scope="module", params=["exemplo", "real"])
def df(request, df_exemplo):
    """Valida o formato das duas bases: a fictícia sempre, a real quando existir."""
    return df_exemplo if request.param == "exemplo" else request.getfixturevalue("df_real")


def test_colunas(df):
    assert list(df.columns) == COLUNAS_ESPERADAS


def test_sem_colunas_identificaveis(df):
    assert not set(COLUNAS_PROIBIDAS) & set(df.columns)


def test_ids_unicos_e_sem_nulos(df):
    assert df["ID_Egresso"].is_unique
    assert df.isna().sum().sum() == 0


def test_dominios(df):
    assert set(df["Curso_de_Graduacao"]) <= set(CURSOS)
    assert set(df["Periodo_Conclusao"]) <= set(PERIODOS)
    for ind in INDICADORES:
        assert set(df[ind].unique()) <= {0, 1}
    assert df["UF_Nascimento"].str.fullmatch(r"[A-Z]{2}").all()


def test_ler_dados_recusa_base_com_identificador(tmp_path, df):
    caminho = tmp_path / "base.csv"
    df.assign(Local_de_Trabalho="Empresa X").to_csv(caminho, index=False)
    with pytest.raises(ValueError, match="identificáveis"):
        ler_dados(caminho)
