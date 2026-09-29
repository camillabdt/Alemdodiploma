"""RNF01 — apresentação agregada com supressão de grupos pequenos.

Regra: nenhuma contagem ou percentual é exibido para grupos com menos de
MIN_GRUPO egressos. Isso impede que combinações de filtros isolem uma pessoa
e revelem seus indicadores (divulgação de atributo).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.core.config import MIN_GRUPO, MIN_TOTAL, SEM_INFORMACAO

MASCARA = f"<{MIN_GRUPO}"


def recorte_suficiente(df: pd.DataFrame) -> bool:
    return len(df) >= MIN_TOTAL


def sem_informacao(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Remove categorias que não representam um fenômeno observável."""
    return df[~df[coluna].isin(SEM_INFORMACAO)]


def mascarar(n) -> str:
    n = int(n)
    return MASCARA if 0 < n < MIN_GRUPO else str(n)


def frequencias(df: pd.DataFrame, coluna: str) -> tuple[pd.DataFrame, int]:
    """Frequência de uma variável. Devolve (tabela visível, nº de categorias ocultadas).

    O percentual usa como base todos os registros válidos, inclusive os de
    categorias ocultadas, para não inflar as categorias exibidas.
    """
    contagem = df[coluna].value_counts(sort=True)
    contagem = contagem[contagem > 0]
    total = int(contagem.sum())
    tab = contagem.rename_axis(coluna).reset_index(name="Quantidade")
    tab["Percentual"] = (tab["Quantidade"] / total * 100).round(1) if total else 0.0
    visivel = tab[tab["Quantidade"] >= MIN_GRUPO].reset_index(drop=True)
    return visivel, int((tab["Quantidade"] < MIN_GRUPO).sum())


def cruzada(df: pd.DataFrame, linha: str, coluna: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabela cruzada de contagens e percentual dentro de cada coluna.

    Células com 1 a MIN_GRUPO-1 registros viram NaN no percentual e máscara nas contagens.
    Colunas inteiras com total < MIN_GRUPO são suprimidas.
    """
    cont = pd.crosstab(df[linha], df[coluna])
    cont = cont.loc[cont.sum(axis=1) > 0, cont.sum(axis=0) > 0]
    pct = cont.div(cont.sum(axis=0), axis=1) * 100
    pequeno = (cont > 0) & (cont < MIN_GRUPO)
    coluna_pequena = cont.sum(axis=0) < MIN_GRUPO
    pct = pct.mask(pequeno).round(1)
    pct.loc[:, coluna_pequena] = np.nan
    cont_txt = cont.astype(object).where(~pequeno, MASCARA)
    cont_txt.loc[:, coluna_pequena] = MASCARA
    return cont_txt, pct


def taxa_por_grupo(df: pd.DataFrame, grupo: str, indicador: str) -> pd.DataFrame:
    """Percentual de egressos com evidência do indicador, por grupo.

    Suprime o grupo inteiro (contagem e percentual) se n < MIN_GRUPO e mascara
    a contagem de evidências quando ela fica entre 1 e MIN_GRUPO-1.
    """
    g = df.groupby(grupo, observed=True)[indicador].agg(n="size", com_evidencia="sum").reset_index()
    g["Percentual"] = (g["com_evidencia"] / g["n"] * 100).round(1)
    pequeno = g["n"] < MIN_GRUPO
    g.loc[pequeno, "Percentual"] = np.nan
    g["Com evidência"] = g["com_evidencia"].map(mascarar)
    g.loc[pequeno, "Com evidência"] = MASCARA
    g["n (grupo)"] = g["n"].map(mascarar)
    return g
