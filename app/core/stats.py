"""Testes estatísticos usados no dashboard (item 4 do parecer).

Escolhas:
- Tabelas 2×2 (curso × indicador, indicador × indicador): teste exato de Fisher,
  válido com qualquer frequência; efeito = coeficiente Phi (com sinal).
- Tabelas maiores (curso × categoria): qui-quadrado de independência; efeito =
  V de Cramér. Verifica-se o pressuposto de frequência esperada (no máximo 20%
  das células com esperado < 5 e nenhuma < 1, critério de Cochran).
- Tempo desde a conclusão entre grupos com e sem evidência: Mann-Whitney U
  (a variável é discreta e assimétrica, sem normalidade); efeito = correlação
  bisserial de postos.
- Famílias de testes: correção de Holm para múltiplas comparações.
- Controle de confusão curso × tempo: regressão logística
  indicador ~ curso + tempo desde a conclusão, com razões de chance e IC 95%.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
from scipy import stats

ALFA = 0.05


def _phi_2x2(tab: np.ndarray) -> float:
    a, b = tab[0]
    c, d = tab[1]
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return float((a * d - b * c) / den) if den else float("nan")


def associacao(df: pd.DataFrame, linha: str, coluna: str) -> dict | None:
    """Escolhe Fisher (2×2) ou qui-quadrado (maior) e devolve teste, p e efeito."""
    tab = pd.crosstab(df[linha], df[coluna])
    tab = tab.loc[tab.sum(axis=1) > 0, tab.sum(axis=0) > 0]
    if tab.shape[0] < 2 or tab.shape[1] < 2:
        return None
    n = int(tab.values.sum())
    if tab.shape == (2, 2):
        _, p = stats.fisher_exact(tab.values)
        return {"teste": "Exato de Fisher", "n": n, "estatistica": None, "p": float(p),
                "efeito": _phi_2x2(tab.values), "medida_efeito": "Phi",
                "pressuposto_ok": True, "aviso": ""}
    chi2, p, gl, esperado = stats.chi2_contingency(tab.values)
    prop_baixo = float((esperado < 5).mean())
    ok = bool(prop_baixo <= 0.20 and esperado.min() >= 1)
    v = math.sqrt(chi2 / (n * (min(tab.shape) - 1)))
    aviso = "" if ok else (
        f"{prop_baixo:.0%} das células têm frequência esperada < 5; "
        "o qui-quadrado é aproximado. Interprete junto com a análise descritiva."
    )
    return {"teste": f"Qui-quadrado (gl={gl})", "n": n, "estatistica": float(chi2), "p": float(p),
            "efeito": v, "medida_efeito": "V de Cramér", "pressuposto_ok": ok, "aviso": aviso}


def comparar_tempo(df: pd.DataFrame, indicador: str, tempo: str = "Tempo_desde_Conclusao") -> dict | None:
    sim = df.loc[df[indicador] == 1, tempo]
    nao = df.loc[df[indicador] == 0, tempo]
    if len(sim) < 2 or len(nao) < 2:
        return None
    u, p = stats.mannwhitneyu(sim, nao, alternative="two-sided")
    r = 2 * u / (len(sim) * len(nao)) - 1  # bisserial de postos: >0 => grupo "sim" tem mais tempo
    return {"teste": "Mann-Whitney U", "n_sim": len(sim), "n_nao": len(nao),
            "media_sim": float(sim.mean()), "media_nao": float(nao.mean()),
            "mediana_sim": float(sim.median()), "mediana_nao": float(nao.median()),
            "estatistica": float(u), "p": float(p), "efeito": float(r),
            "medida_efeito": "Correlação bisserial de postos"}


def holm(pvalores: list[float]) -> list[float]:
    """Ajuste de Holm-Bonferroni (mantém a ordem original)."""
    m = len(pvalores)
    ordem = np.argsort(pvalores)
    ajustados = np.empty(m)
    acumulado = 0.0
    for rank, idx in enumerate(ordem):
        valor = min(1.0, (m - rank) * pvalores[idx])
        acumulado = max(acumulado, valor)
        ajustados[idx] = acumulado
    return ajustados.tolist()


def regressao_logistica(df: pd.DataFrame, indicador: str, curso: str = "Curso_de_Graduacao",
                        tempo: str = "Tempo_desde_Conclusao",
                        referencia: str = "Ciência da Computação") -> dict | None:
    """indicador ~ curso + tempo. Devolve razões de chance (OR) com IC 95%."""
    import statsmodels.api as sm

    base = df[[indicador, curso, tempo]].dropna()
    y = base[indicador].astype(int)
    if base[curso].nunique() < 2 or y.nunique() < 2 or y.sum() < 5 or (1 - y).sum() < 5:
        return None
    outros = [c for c in base[curso].unique() if c != referencia]
    if len(outros) != 1:
        return None
    rotulo_curso = f"{outros[0]} (vs. {referencia})"
    X = pd.DataFrame({rotulo_curso: (base[curso] == outros[0]).astype(float),
                      "Anos desde a conclusão (+1)": base[tempo].astype(float)})
    X = sm.add_constant(X)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            modelo = sm.Logit(y, X).fit(disp=False)
    except Exception:  # separação perfeita, matriz singular etc.
        return None
    ic = modelo.conf_int()
    linhas = []
    for termo in X.columns[1:]:
        linhas.append({"Termo": termo, "Razão de chances": float(np.exp(modelo.params[termo])),
                       "IC 95% inf.": float(np.exp(ic.loc[termo, 0])),
                       "IC 95% sup.": float(np.exp(ic.loc[termo, 1])),
                       "p": float(modelo.pvalues[termo])})
    return {"n": int(len(base)), "pseudo_r2": float(modelo.prsquared), "coeficientes": linhas}


def formatar_p(p: float | None) -> str:
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "—"
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def num(x: float | None, casas: int = 2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.{casas}f}".replace(".", ",")
