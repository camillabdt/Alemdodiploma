"""RF07 — tempo desde a conclusão e indicadores de trajetória."""
import pandas as pd
import streamlit as st

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.export import tabela_com_download
from app.core.privacy import taxa_por_grupo
from app.views.base import Contexto

TITULO = "Tempo de carreira"


def render(df, ctx: Contexto) -> None:
    st.header("Tempo desde a conclusão e maturidade profissional")

    resultados = {ind: stats.comparar_tempo(df, ind) for ind in INDICADORES}
    validos = {k: v for k, v in resultados.items()
               if v and v["n_sim"] >= MIN_GRUPO and v["n_nao"] >= MIN_GRUPO}
    if not validos:
        st.info("O recorte atual não tem egressos suficientes com e sem evidência para comparar.")
        return

    linhas = []
    for ind, r in validos.items():
        linhas += [{"Indicador": INDICADORES[ind], "Grupo": "Sem evidência observada", "Média": r["media_nao"]},
                   {"Indicador": INDICADORES[ind], "Grupo": "Com evidência", "Média": r["media_sim"]}]
    st.plotly_chart(charts.tempo_por_indicador(pd.DataFrame(linhas), "Média de anos desde a conclusão"),
                    use_container_width=True, config=charts.config_plotly("tempo_por_indicador"))

    p_holm = stats.holm([r["p"] for r in validos.values()])
    tab = pd.DataFrame([{
        "Indicador": INDICADORES[ind],
        "n com / sem": f"{r['n_sim']} / {r['n_nao']}",
        "Mediana com / sem (anos)": f"{stats.num(r['mediana_sim'], 0)} / {stats.num(r['mediana_nao'], 0)}",
        "Média com / sem (anos)": f"{stats.num(r['media_sim'], 1)} / {stats.num(r['media_nao'], 1)}",
        "Bisserial de postos": stats.num(r["efeito"]),
        "p": stats.formatar_p(r["p"]),
        "p ajustado (Holm)": stats.formatar_p(ph),
    } for (ind, r), ph in zip(validos.items(), p_holm)])
    tabela_com_download(tab, "tempo_desde_conclusao_por_indicador", True)
    st.caption(
        "Teste de Mann-Whitney U (bilateral): o tempo desde a conclusão é discreto e assimétrico, então não se "
        "assume normalidade. Bisserial de postos positivo = quem tem evidência está formado há mais tempo "
        "(0,1 pequeno, 0,3 médio, 0,5 grande)."
    )

    st.subheader("Indicadores por período de conclusão")
    linhas = []
    for ind, nome in INDICADORES.items():
        t = taxa_por_grupo(df, "Periodo_Conclusao", ind)
        t["Indicador"] = nome
        linhas.append(t)
    per = pd.concat(linhas, ignore_index=True)
    per["Periodo_Conclusao"] = per["Periodo_Conclusao"].astype(str)
    st.plotly_chart(charts.taxa_por_periodo(per, "Percentual com evidência por período de conclusão"),
                    use_container_width=True, config=charts.config_plotly("indicadores_por_periodo"))
    tabela_com_download(per[["Indicador", "Periodo_Conclusao", "n (grupo)", "Com evidência", "Percentual"]],
                        "indicadores_por_periodo", ctx.mostrar_tabelas)
