"""Escolha de testes, medidas de efeito e reprodução dos resultados do TCC I."""
import math

import pandas as pd
import pytest

from app.core import stats
from app.core.privacy import sem_informacao


from tests.conftest import requer_base_real


@pytest.fixture(scope="module")
def df(df_exemplo):
    return df_exemplo


def test_fisher_em_tabela_2x2(df):
    r = stats.associacao(df, "Curso_de_Graduacao", "Indicador_Lideranca")
    assert r["teste"] == "Exato de Fisher"
    assert r["medida_efeito"] == "Phi"


@requer_base_real
def test_qui_quadrado_reproduz_tcc1(df_real):
    df = df_real
    r = stats.associacao(sem_informacao(df, "Categoria_Cargo"), "Curso_de_Graduacao", "Categoria_Cargo")
    assert r["teste"].startswith("Qui-quadrado")
    assert r["n"] == 262
    assert r["estatistica"] == pytest.approx(20.16, abs=0.01)
    assert r["p"] == pytest.approx(0.005, abs=0.001)
    assert r["efeito"] == pytest.approx(0.277, abs=0.001)


def test_aviso_quando_pressuposto_falha():
    base = pd.DataFrame({"a": ["x"] * 30 + ["y"] * 2 + ["z"] * 2, "b": ["p", "q"] * 17})
    r = stats.associacao(base, "a", "b")
    assert not r["pressuposto_ok"] and r["aviso"]


@requer_base_real
def test_mann_whitney_reproduz_tcc1(df_real):
    r = stats.comparar_tempo(df_real, "Indicador_Lideranca")
    assert r["n_sim"] == 86
    assert r["media_sim"] == pytest.approx(8.22, abs=0.01)
    assert r["p"] < 0.001


def test_mann_whitney_direcao(df):
    r = stats.comparar_tempo(df, "Indicador_Lideranca")
    assert r["teste"] == "Mann-Whitney U"
    assert r["efeito"] > 0  # na base fictícia a liderança também cresce com o tempo


def test_holm():
    assert stats.holm([0.01, 0.04, 0.03, 0.5]) == pytest.approx([0.04, 0.09, 0.09, 0.5])
    assert stats.holm([0.9, 0.9]) == [1.0, 1.0]


def test_regressao_logistica(df):
    r = stats.regressao_logistica(df, "Indicador_Lideranca")
    termos = {c["Termo"]: c for c in r["coeficientes"]}
    tempo = termos["Anos desde a conclusão (+1)"]
    assert tempo["Razão de chances"] > 1 and tempo["p"] < 0.05
    assert r["n"] == len(df)


def test_regressao_recusa_recorte_pequeno(df):
    assert stats.regressao_logistica(df.head(8), "Indicador_Empreendedorismo") is None


def test_formatacao():
    assert stats.formatar_p(0.0001) == "< 0,001"
    assert stats.formatar_p(0.0456) == "0,046"
    assert stats.num(math.nan) == "—"
