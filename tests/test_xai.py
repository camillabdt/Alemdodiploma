"""IA explicável: propriedades do SHAP, escolhas de fatores e privacidade."""
import numpy as np
import pandas as pd
import pytest

from app.core import xai


def _linear(pesos):
    return lambda A: A @ np.asarray(pesos, dtype=float)


def test_shapley_modelo_linear_tem_solucao_conhecida():
    # Para f linear e fundo independente, phi_i(x) = w_i * (x_i - média do fundo em i).
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(30, 3)), columns=["a", "b", "c"])
    fundo = X.iloc[:10]
    w = [2.0, -1.0, 0.5]
    phi, base = xai.shapley_por_fator(_linear(w), X, {c: [c] for c in X.columns}, fundo)
    esperado = (X.to_numpy() - fundo.to_numpy().mean(axis=0)) * np.asarray(w)
    assert np.allclose(phi, esperado)
    assert base == pytest.approx(float(fundo.to_numpy().mean(axis=0) @ np.asarray(w)))


def test_eficiencia_e_fator_ignorado():
    rng = np.random.default_rng(1)
    X = pd.DataFrame(rng.normal(size=(25, 4)), columns=["a", "b1", "b2", "c"])
    f = lambda A: np.tanh(A[:, 0] * A[:, 1]) + A[:, 2] ** 2  # não usa a coluna "c"  # noqa: E731
    grupos = {"A": ["a"], "B": ["b1", "b2"], "C": ["c"]}
    phi, base = xai.shapley_por_fator(f, X, grupos, X.iloc[:8])
    assert np.allclose(phi.sum(axis=1) + base, f(X.to_numpy()))  # eficiência
    assert np.allclose(phi[:, 2], 0)                               # fator sem uso recebe zero


def test_fatores_sem_vazamento_nem_atributo_sensivel(df_exemplo):
    m = xai.preparar(df_exemplo)
    assert list(m.grupos) == xai.FATORES
    colunas = " ".join(m.X.columns).lower()
    assert "categoria" not in colunas and "gestao" not in colunas
    assert "genero" not in colunas and "feminino" not in colunas
    assert "Indicador_Mudanca_Area" not in xai.ALVOS


def test_explicar_e_efeito_medio_respeitam_grupo_minimo(df_exemplo):
    exp = xai.explicar(df_exemplo, "Indicador_Lideranca", tamanho_fundo=15, repeticoes=1)
    assert set(exp.importancia.columns) == {"Regressão logística", "Random forest"}
    assert list(exp.importancia.index) == xai.FATORES
    for nome, (auc, _) in exp.auc.items():
        assert 0 <= auc <= 1
    # o valor base fica próximo da taxa real (sem reponderação de classes)
    assert exp.base["Random forest"] == pytest.approx(exp.positivos / exp.n * 100, abs=8)
    tab = xai.efeito_medio(exp, "Random forest", "Anos de formado", min_grupo=5)
    assert (tab["n"] >= 5).all()
