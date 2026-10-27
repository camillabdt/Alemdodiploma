"""IA explicável (XAI): que fatores de contexto se associam aos indicadores de trajetória?

Desenho (seguindo o padrão da literatura de XAI em análise educacional e de empregabilidade):

1. Dois modelos: regressão logística (caixa-branca, referência) e random forest (caixa-preta).
2. Desempenho por validação cruzada estratificada repetida (AUC ROC).
3. Explicações por valores de Shapley (SHAP) exatos e intervencionais, calculados por FATOR
   (um fator categórico com várias colunas conta como um único "jogador"). Com poucos fatores,
   o cálculo exato é barato e dispensa aproximações e a biblioteca `shap`.

Decisões metodológicas:
- A categoria do cargo NÃO entra como fator: "Gestão/Liderança" praticamente define o
  indicador de liderança (vazamento de informação), e o modelo só reproduziria a definição.
- Gênero NÃO entra como fator: o objetivo é descrever trajetórias, não atribuir resultados a
  um atributo sensível; além disso, o grupo feminino é pequeno.
- Mudança de área NÃO é modelada: são poucos casos positivos e o desempenho é instável.
- Só se exibem explicações GLOBAIS e AGREGADAS. Explicações locais descreveriam pessoas reais.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ALVOS = {
    "Indicador_Lideranca": "Liderança ou gerência",
    "Indicador_Empreendedorismo": "Empreendedorismo",
    "Indicador_Progressao": "Progressão interna",
}

FATORES = ["Curso", "Anos de formado", "Origem", "Tipo de instituição"]

SEMENTE = 2026


@dataclass
class Matriz:
    X: pd.DataFrame                 # colunas numéricas usadas pelos modelos
    grupos: dict[str, list[str]]    # fator -> colunas de X
    valores: pd.DataFrame           # valor legível de cada fator por egresso (para agregações)


def preparar(df: pd.DataFrame) -> Matriz:
    tipo = df["Tipo_Instituicao"].replace({"Sem vínculo informado": "Sem Informação"})
    dummies = pd.get_dummies(tipo, prefix="tipo", dtype=float)
    X = pd.concat([
        pd.DataFrame({
            "curso_es": (df["Curso_de_Graduacao"] == "Engenharia de Software").astype(float).values,
            "anos": df["Tempo_desde_Conclusao"].astype(float).values,
            "fora_rs": (df["UF_Nascimento"] != "RS").astype(float).values,
        }, index=df.index),
        dummies,
    ], axis=1)
    grupos = {
        "Curso": ["curso_es"],
        "Anos de formado": ["anos"],
        "Origem": ["fora_rs"],
        "Tipo de instituição": list(dummies.columns),
    }
    valores = pd.DataFrame({
        "Curso": df["Curso_de_Graduacao"].astype(str).values,
        "Anos de formado": df["Tempo_desde_Conclusao"].astype(int).values,
        "Origem": np.where(df["UF_Nascimento"] == "RS", "Nascido(a) no RS", "Nascido(a) fora do RS"),
        "Tipo de instituição": tipo.values,
    }, index=df.index)
    return Matriz(X=X, grupos=grupos, valores=valores)


def modelos() -> dict:
    return {
        "Regressão logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        # Sem class_weight: assim o valor base do SHAP coincide com a taxa real do indicador
        # e as contribuições ficam em pontos percentuais de probabilidade, fáceis de ler.
        "Random forest": RandomForestClassifier(
            n_estimators=150, max_depth=4, min_samples_leaf=10, random_state=SEMENTE, n_jobs=1,
        ),
    }


def avaliar(X: pd.DataFrame, y: np.ndarray, repeticoes: int = 5) -> dict[str, tuple[float, float]]:
    """AUC ROC média e desvio padrão em validação cruzada estratificada 5×repetições."""
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeticoes, random_state=SEMENTE)
    return {nome: tuple(float(v) for v in (lambda s: (s.mean(), s.std()))(
                cross_val_score(m, X, y, cv=cv, scoring="roc_auc")))
            for nome, m in modelos().items()}


def shapley_por_fator(prever, X: pd.DataFrame, grupos: dict[str, list[str]],
                      fundo: pd.DataFrame) -> tuple[np.ndarray, float]:
    """Valores de Shapley exatos e intervencionais, com fatores como jogadores.

    v(S)(x) = média sobre o fundo b de f(x nas colunas de S, b nas demais).
    phi_i(x) = Σ_{S ⊆ N\\{i}} |S|!(M-|S|-1)!/M! · [v(S ∪ {i})(x) − v(S)(x)]

    Retorna (phi com forma n × M, na escala de probabilidade; valor base = v(∅)).
    Propriedade de eficiência: Σ_i phi_i(x) = f(x) − v(∅) para todo x.
    """
    jogadores = list(grupos)
    M, n, k = len(jogadores), len(X), len(fundo)
    Xv, Fv = X.to_numpy(float), fundo.to_numpy(float)
    idx = {c: i for i, c in enumerate(X.columns)}
    cols = [[idx[c] for c in grupos[j]] for j in jogadores]

    v = {}
    for tam in range(M + 1):
        for S in combinations(range(M), tam):
            dados = np.tile(Fv, (n, 1))                       # n·k linhas: cada x com todo o fundo
            for j in S:
                dados[:, cols[j]] = np.repeat(Xv[:, cols[j]], k, axis=0)
            v[S] = prever(dados).reshape(n, k).mean(axis=1)
    phi = np.zeros((n, M))
    for i in range(M):
        outros = [j for j in range(M) if j != i]
        for tam in range(M):
            peso = factorial(tam) * factorial(M - tam - 1) / factorial(M)
            for S in combinations(outros, tam):
                com_i = tuple(sorted(S + (i,)))
                phi[:, i] += peso * (v[com_i] - v[S])
    return phi, float(v[()].mean())


@dataclass
class Explicacao:
    alvo: str
    n: int
    positivos: int
    auc: dict[str, tuple[float, float]]
    importancia: pd.DataFrame        # Fator × modelo: média de |SHAP| (pontos percentuais)
    efeitos: dict[str, pd.DataFrame]  # modelo -> SHAP por egresso (pp), colunas = fatores
    valores: pd.DataFrame
    base: dict[str, float]


def explicar(df: pd.DataFrame, alvo: str, tamanho_fundo: int = 40, repeticoes: int = 5) -> Explicacao:
    m = preparar(df)
    y = df[alvo].to_numpy(int)
    auc = avaliar(m.X, y, repeticoes)
    rng = np.random.default_rng(SEMENTE)
    fundo = m.X.iloc[rng.choice(len(m.X), size=min(tamanho_fundo, len(m.X)), replace=False)]
    importancia, efeitos, base = {}, {}, {}
    for nome, modelo in modelos().items():
        modelo.fit(m.X, y)
        prever = lambda A, mod=modelo: mod.predict_proba(pd.DataFrame(A, columns=m.X.columns))[:, 1]  # noqa: E731
        phi, b = shapley_por_fator(prever, m.X, m.grupos, fundo)
        phi_pp = pd.DataFrame(phi * 100, columns=FATORES, index=df.index)
        efeitos[nome] = phi_pp
        importancia[nome] = phi_pp.abs().mean()
        base[nome] = b * 100
    return Explicacao(alvo=alvo, n=len(df), positivos=int(y.sum()), auc=auc,
                      importancia=pd.DataFrame(importancia), efeitos=efeitos, valores=m.valores, base=base)


def efeito_medio(exp: Explicacao, modelo: str, fator: str, min_grupo: int) -> pd.DataFrame:
    """SHAP médio (pp) por valor do fator, só para grupos com pelo menos min_grupo egressos."""
    tab = pd.DataFrame({"Valor": exp.valores[fator], "SHAP": exp.efeitos[modelo][fator]})
    g = tab.groupby("Valor").agg(n=("SHAP", "size"), Efeito=("SHAP", "mean")).reset_index()
    return g[g["n"] >= min_grupo].reset_index(drop=True)
