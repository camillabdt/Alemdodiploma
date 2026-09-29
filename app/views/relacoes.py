"""Relações entre indicadores de trajetória (coocorrência)."""
from itertools import combinations

import numpy as np
import pandas as pd
import streamlit as st

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.export import tabela_com_download
from app.core.privacy import mascarar
from app.views.base import Contexto, leitura

TITULO = "Relações entre indicadores"


def render(df, ctx: Contexto) -> None:
    st.header("Como os indicadores se combinam")
    st.caption("Phi varia de -1 a 1: positivo indica que os dois sinais tendem a aparecer juntos.")

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
                       "_ambos": ambos, "Phi": r["efeito"], "_p": r["p"]})
    for n in nomes:
        matriz.loc[n, n] = 1.0

    if not linhas:
        st.info("O recorte atual não permite calcular as associações.")
        return
    st.plotly_chart(charts.matriz_phi(matriz, "Associação entre indicadores (Phi)"),
                    use_container_width=True, config=charts.config_plotly("matriz_phi_indicadores"))

    p_holm = stats.holm([l["_p"] for l in linhas])
    tab = pd.DataFrame([{"Par": l["Par"], "Egressos com ambos": l["Ambos"], "Phi": stats.num(l["Phi"], 3),
                         "p (Fisher)": stats.formatar_p(l["_p"]), "p ajustado (Holm)": stats.formatar_p(ph)}
                        for l, ph in zip(linhas, p_holm)])
    tabela_com_download(tab, "associacoes_entre_indicadores", True)

    emp = int(df["Indicador_Empreendedorismo"].sum())
    emp_lid = int(((df["Indicador_Empreendedorismo"] == 1) & (df["Indicador_Lideranca"] == 1)).sum())
    if emp >= MIN_GRUPO and emp_lid >= MIN_GRUPO:
        leitura(
            f"{emp_lid} dos {emp} egressos com evidência de empreendedorismo também têm evidência de liderança. "
            "Parte dessa sobreposição decorre da própria definição: cargos como CEO e sócio-fundador costumam "
            "ser codificados nos dois indicadores."
        )
