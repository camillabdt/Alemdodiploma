"""RF07 — tempo desde a conclusão e indicadores de trajetória."""
import pandas as pd
import streamlit as st

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.privacy import taxa_por_grupo
from app.views.base import Contexto, cabecalho, cartao, grafico, leitura, nota_estatistica, rodape, tabela, vazio

TITULO = "Tempo de carreira"


def render(df, ctx: Contexto) -> None:
    cabecalho("Maturidade profissional", "Tempo desde a conclusão",
              "Como os sinais de trajetória se relacionam com os anos de formado.")

    resultados = {ind: stats.comparar_tempo(df, ind) for ind in INDICADORES}
    validos = {k: v for k, v in resultados.items()
               if v and v["n_sim"] >= MIN_GRUPO and v["n_nao"] >= MIN_GRUPO}
    if not validos:
        vazio("O recorte atual não tem egressos suficientes com e sem evidência para comparar.")
        rodape()
        return

    linhas = []
    for ind, r in validos.items():
        linhas += [{"Indicador": INDICADORES[ind], "Grupo": "Sem evidência observada", "Média": r["media_nao"]},
                   {"Indicador": INDICADORES[ind], "Grupo": "Com evidência", "Média": r["media_sim"]}]
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

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        with cartao("Anos de formado, com e sem evidência", "Média de anos desde a conclusão"):
            grafico(charts.tempo_por_indicador(pd.DataFrame(linhas), ""), "tempo_por_indicador")
    with c2:
        per = []
        for ind, nome in INDICADORES.items():
            t = taxa_por_grupo(df, "Periodo_Conclusao", ind)
            t["Indicador"] = nome
            per.append(t)
        per = pd.concat(per, ignore_index=True)
        per["Periodo_Conclusao"] = per["Periodo_Conclusao"].astype(str)
        with cartao("Por período de conclusão", "Percentual com evidência"):
            grafico(charts.taxa_por_periodo(per, ""), "indicadores_por_periodo",
                    per[["Indicador", "Periodo_Conclusao", "n (grupo)", "Com evidência", "Percentual"]])

    with cartao("Teste de diferença", "Tempo desde a conclusão, com × sem evidência"):
        tabela(tab, "tempo_desde_conclusao_por_indicador")
        nota_estatistica(
            "Mann-Whitney U bilateral: o tempo desde a conclusão é discreto e assimétrico, então não se assume "
            "normalidade. Bisserial de postos positivo indica que quem tem evidência está formado há mais tempo "
            "(0,1 pequeno; 0,3 médio; 0,5 grande). p-valores ajustados por Holm."
        )

    lid = validos.get("Indicador_Lideranca")
    if lid:
        leitura(
            f"Egressos com evidência de liderança estão formados há {stats.num(lid['mediana_sim'], 0)} anos "
            f"(mediana), contra {stats.num(lid['mediana_nao'], 0)} entre os demais. A liderança acompanha o "
            "tempo de carreira, o que afeta qualquer comparação entre grupos com tempos de formado diferentes."
        )
    rodape()
