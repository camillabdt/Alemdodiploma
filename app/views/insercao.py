"""RF03/RF04 — inserção profissional: categoria do cargo e tipo de instituição."""
import streamlit as st

from app.core import charts, stats
from app.core.export import tabela_com_download
from app.core.privacy import cruzada, frequencias, sem_informacao
from app.views.base import Contexto, leitura, nota_ocultas

TITULO = "Inserção profissional"


def _bloco_por_curso(base, coluna, titulo, nome, ctx):
    cont, pct_ = cruzada(base, coluna, "Curso_de_Graduacao")
    pct_.index.name = coluna
    if pct_.shape[1] >= 1 and pct_.notna().any().any():
        st.plotly_chart(charts.barras_por_curso(pct_, titulo, ""), use_container_width=True,
                        config=charts.config_plotly(nome))
    tabela = cont.copy()
    tabela.columns = [f"{c} (n)" for c in tabela.columns]
    for c in pct_.columns:
        tabela[f"{c} (%)"] = pct_[c]
    tabela_com_download(tabela.reset_index(), nome, ctx.mostrar_tabelas)
    res = stats.associacao(base, "Curso_de_Graduacao", coluna)
    if res:
        st.caption(
            f"{res['teste']}: n = {res['n']}, p = {stats.formatar_p(res['p'])}, "
            f"{res['medida_efeito']} = {stats.num(res['efeito'], 3)}. "
            "A associação indica que a distribuição difere entre os cursos, não a causa da diferença."
        )
        if res["aviso"]:
            st.caption(res["aviso"])


def render(df, ctx: Contexto) -> None:
    st.header("Onde os egressos atuam")
    st.caption("Cargo mais recente identificado no perfil público. Registros sem informação ficam fora dos gráficos.")

    cargos = sem_informacao(df, "Categoria_Cargo")
    tab, ocultas = frequencias(cargos, "Categoria_Cargo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Com cargo classificado", len(cargos))
    c2.metric("Sem informação de cargo", len(df) - len(cargos))
    if not tab.empty:
        c3.metric("Categoria mais frequente", f"{stats.num(tab.iloc[0]['Percentual'], 1)}%")
        c3.caption(tab.iloc[0]["Categoria_Cargo"])

    st.subheader("Categoria do cargo atual")
    if not tab.empty:
        st.plotly_chart(charts.barras_horizontais(tab, "Categoria_Cargo", "Egressos por categoria do cargo atual"),
                        use_container_width=True, config=charts.config_plotly("categoria_cargo"))
    nota_ocultas(ocultas)
    tabela_com_download(tab, "categoria_cargo", ctx.mostrar_tabelas)

    if cargos["Curso_de_Graduacao"].nunique() == 2:
        _bloco_por_curso(cargos, "Categoria_Cargo", "Categoria do cargo por curso (% dentro do curso)",
                         "categoria_cargo_por_curso", ctx)

    st.subheader("Tipo de instituição")
    inst = sem_informacao(df, "Tipo_Instituicao")
    tab, ocultas = frequencias(inst, "Tipo_Instituicao")
    if not tab.empty:
        st.plotly_chart(charts.barras_horizontais(tab, "Tipo_Instituicao", "Egressos por tipo de instituição"),
                        use_container_width=True, config=charts.config_plotly("tipo_instituicao"))
        top = tab.iloc[0]
        leitura(
            f"a maior parte dos egressos com vínculo informado está em \"{top['Tipo_Instituicao']}\" "
            f"({stats.num(top['Percentual'], 1)}%). "
            "Essa categoria reúne setores diferentes; a revisão da base prevê separar empresas não "
            "tecnológicas de outros vínculos."
        )
    nota_ocultas(ocultas)
    tabela_com_download(tab, "tipo_instituicao", ctx.mostrar_tabelas)

    if inst["Curso_de_Graduacao"].nunique() == 2:
        _bloco_por_curso(inst, "Tipo_Instituicao", "Tipo de instituição por curso (% dentro do curso)",
                         "tipo_instituicao_por_curso", ctx)
