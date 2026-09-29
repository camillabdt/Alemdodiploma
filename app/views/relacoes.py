"""Relações entre indicadores de trajetória (coocorrência)."""
from itertools import combinations

import numpy as np
import pandas as pd
import streamlit as st

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.privacy import mascarar
from app.views.base import Contexto, cabecalho, cartao, grafico, leitura, nota_estatistica, rodape, tabela, vazio

TITULO = "Relações entre indicadores"


def render(df, ctx: Contexto) -> None:
    cabecalho("Combinação de sinais", "Como os indicadores se combinam",
              "Quais sinais de trajetória tendem a aparecer juntos nos mesmos egressos.")

    nomes = list(INDICADORES.values())
    matriz = pd.DataFrame(np.nan, index=nomes, columns=nomes)
    linhas = []
    for a, b in combinations(INDICADORES, 2):
        ambos = int(((df[a] == 1) & (df[b] == 1)).sum())
        r = stats.associacao(df, a, b)
        if r is None:
            continue
        matriz.loc[INDICADORES[a], INDICADORES[b]] = matriz.loc[INDICADORES[b], INDICADORES[a]] = r["efeito"]
        linhas.append({"Par": f"{INDICADORES[a]} × {INDICADORES[b]}", "Ambos": mascarar(ambos),
                       "Phi": r["efeito"], "_p": r["p"]})
    for n in nomes:
        matriz.loc[n, n] = 1.0
    if not linhas:
        vazio("O recorte atual não permite calcular as associações.")
        rodape()
        return

    p_holm = stats.holm([l["_p"] for l in linhas])
    tab = pd.DataFrame([{"Par": l["Par"], "Egressos com ambos": l["Ambos"], "Phi": stats.num(l["Phi"], 3),
                         "p (Fisher)": stats.formatar_p(l["_p"]), "p ajustado (Holm)": stats.formatar_p(ph)}
                        for l, ph in zip(linhas, p_holm)])

    c1, c2 = st.columns([2, 3], gap="medium")
    with c1:
        with cartao("Matriz de associação", "Coeficiente Phi entre pares de indicadores"):
            grafico(charts.matriz_phi(matriz, ""), "matriz_phi_indicadores")
    with c2:
        with cartao("Pares de indicadores", "Coocorrência e teste de associação"):
            tabela(tab, "associacoes_entre_indicadores")
            nota_estatistica("Exato de Fisher em cada par; Phi varia de −1 a 1, e valores positivos indicam que "
                             "os sinais aparecem juntos. p-valores ajustados por Holm para os seis pares.")

    emp = int(df["Indicador_Empreendedorismo"].sum())
    emp_lid = int(((df["Indicador_Empreendedorismo"] == 1) & (df["Indicador_Lideranca"] == 1)).sum())
    if emp >= MIN_GRUPO and emp_lid >= MIN_GRUPO:
        leitura(
            f"{emp_lid} dos {emp} egressos com evidência de empreendedorismo também têm evidência de liderança. "
            "Parte dessa sobreposição decorre da própria definição: cargos como CEO e sócio-fundador costumam "
            "marcar os dois indicadores."
        )
    rodape()
