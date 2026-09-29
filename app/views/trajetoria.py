"""RF05 — indicadores de trajetória por curso, com controle do tempo desde a conclusão."""
import pandas as pd
import streamlit as st

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.export import tabela_com_download
from app.core.privacy import taxa_por_grupo
from app.views.base import Contexto, leitura, pct

TITULO = "Trajetória por curso"


def render(df, ctx: Contexto) -> None:
    st.header("Sinais de trajetória além do cargo atual")
    st.caption(
        "\"Com evidência\" = o perfil público mostra explicitamente o fenômeno. A ausência não prova que ele "
        "não ocorreu. Definições completas na página Metodologia."
    )

    cols = st.columns(4)
    for col, (ind, nome) in zip(cols, INDICADORES.items()):
        col.metric(nome, pct(df[ind].mean() * 100), help=f"{int(df[ind].sum())} de {len(df)} egressos")

    linhas = []
    for ind, nome in INDICADORES.items():
        t = taxa_por_grupo(df, "Curso_de_Graduacao", ind)
        t["Indicador"] = nome
        linhas.append(t.rename(columns={"Curso_de_Graduacao": "Curso"}))
    taxas = pd.concat(linhas, ignore_index=True)
    st.plotly_chart(charts.taxas_indicadores(taxas, "Percentual com evidência, por curso"),
                    use_container_width=True, config=charts.config_plotly("indicadores_por_curso"))
    tabela_com_download(taxas[["Indicador", "Curso", "n (grupo)", "Com evidência", "Percentual"]],
                        "indicadores_por_curso", ctx.mostrar_tabelas)

    if df["Curso_de_Graduacao"].nunique() < 2:
        st.info("Selecione os dois cursos para ver as comparações estatísticas.")
        return

    st.subheader("Os cursos diferem?")
    brutos = [stats.associacao(df, "Curso_de_Graduacao", ind) for ind in INDICADORES]
    p_holm = stats.holm([r["p"] if r else 1.0 for r in brutos])
    tab_testes = pd.DataFrame({
        "Indicador": list(INDICADORES.values()),
        "Teste": [r["teste"] if r else "—" for r in brutos],
        "Phi": [stats.num(r["efeito"], 3) if r else "—" for r in brutos],
        "p": [stats.formatar_p(r["p"]) if r else "—" for r in brutos],
        "p ajustado (Holm)": [stats.formatar_p(p) for p in p_holm],
    })
    st.dataframe(tab_testes, hide_index=True, use_container_width=True)

    st.markdown(
        "A comparação direta ignora que os cursos têm tempos de formação diferentes. A regressão logística "
        "abaixo estima a chance de cada indicador **mantendo constante** o tempo desde a conclusão."
    )
    linhas_reg = []
    for ind, nome in INDICADORES.items():
        r = stats.regressao_logistica(df, ind)
        if r is None:
            continue
        for c in r["coeficientes"]:
            linhas_reg.append({"Indicador": nome, "Termo": c["Termo"],
                               "Razão de chances": stats.num(c["Razão de chances"]),
                               "IC 95%": f"{stats.num(c['IC 95% inf.'])} a {stats.num(c['IC 95% sup.'])}",
                               "p": stats.formatar_p(c["p"]), "n": r["n"]})
    if linhas_reg:
        reg = pd.DataFrame(linhas_reg)
        tabela_com_download(reg, "regressao_logistica_indicadores", True)
        st.caption(
            "Razão de chances > 1: maior chance de evidência. Para o curso, compara ES com CC; para o tempo, "
            "o efeito de cada ano a mais de formado. Intervalos que incluem 1 indicam efeito incerto. "
            f"Indicadores com menos de {MIN_GRUPO} casos em algum grupo não são modelados."
        )
        lid = [l for l in linhas_reg if l["Indicador"] == "Liderança ou gerência"]
        if len(lid) == 2:
            leitura(
                f"controlando o tempo de formado, a razão de chances de liderança para ES em relação a CC é "
                f"{lid[0]['Razão de chances']} (IC 95% {lid[0]['IC 95%']}; p = {lid[0]['p']}), e cada ano a "
                f"mais desde a conclusão multiplica a chance por {lid[1]['Razão de chances']}."
            )
    else:
        st.info("O recorte atual é pequeno demais para estimar os modelos.")
