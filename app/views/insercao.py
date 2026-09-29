"""RF03/RF04 — inserção profissional: categoria do cargo e tipo de instituição."""
import streamlit as st

from app.core import charts, stats
from app.core.privacy import cruzada, frequencias, sem_informacao
from app.views.base import (Contexto, cabecalho, cartao, grafico, indicadores, leitura, nota_estatistica,
                            rodape, secao)

TITULO = "Inserção profissional"


def _por_curso(base, coluna, titulo, nome):
    cont, pct_ = cruzada(base, coluna, "Curso_de_Graduacao")
    pct_.index.name = coluna
    tabela = cont.copy()
    tabela.columns = [f"{c} (n)" for c in tabela.columns]
    for c in pct_.columns:
        tabela[f"{c} (%)"] = pct_[c]
    with cartao(titulo, "Percentual dentro de cada curso"):
        if pct_.notna().any().any():
            grafico(charts.barras_por_curso(pct_, "", ""), nome, tabela.reset_index())
        res = stats.associacao(base, "Curso_de_Graduacao", coluna)
        if res:
            nota_estatistica(
                f"{res['teste']} · n = {res['n']} · p = {stats.formatar_p(res['p'])} · "
                f"{res['medida_efeito']} = {stats.num(res['efeito'], 3)}. "
                "Indica se a distribuição difere entre os cursos, não a causa da diferença.",
                res["aviso"] or None,
            )


def render(df, ctx: Contexto) -> None:
    cabecalho("Inserção profissional", "Onde os egressos atuam",
              "Cargo mais recente identificado no perfil público e tipo de organização. "
              "Registros sem informação ficam fora dos gráficos.")

    cargos = sem_informacao(df, "Categoria_Cargo")
    inst = sem_informacao(df, "Tipo_Instituicao")
    tab_c, ocultas_c = frequencias(cargos, "Categoria_Cargo")
    top = tab_c.iloc[0] if not tab_c.empty else None
    indicadores([
        ("Com cargo classificado", str(len(cargos)), f"{len(df) - len(cargos)} sem informação"),
        ("Categoria mais frequente", f"{stats.num(top['Percentual'], 1)}%" if top is not None else "—",
         top["Categoria_Cargo"] if top is not None else None),
        ("Com vínculo informado", str(len(inst)), f"{len(df) - len(inst)} sem informação"),
    ])

    secao("Categoria do cargo atual")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with cartao("Todas as categorias", "Egressos por categoria do cargo atual"):
            if not tab_c.empty:
                grafico(charts.barras_horizontais(tab_c, "Categoria_Cargo", ""), "categoria_cargo", tab_c, ocultas_c)
    with c2:
        if cargos["Curso_de_Graduacao"].nunique() == 2:
            _por_curso(cargos, "Categoria_Cargo", "Comparação entre cursos", "categoria_cargo_por_curso")

    secao("Tipo de instituição")
    tab_i, ocultas_i = frequencias(inst, "Tipo_Instituicao")
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        with cartao("Todas as organizações", "Egressos por tipo de instituição"):
            if not tab_i.empty:
                grafico(charts.barras_horizontais(tab_i, "Tipo_Instituicao", ""), "tipo_instituicao", tab_i,
                        ocultas_i)
    with c4:
        if inst["Curso_de_Graduacao"].nunique() == 2:
            _por_curso(inst, "Tipo_Instituicao", "Comparação entre cursos", "tipo_instituicao_por_curso")

    if not tab_i.empty:
        t = tab_i.iloc[0]
        leitura(
            f"A maior parte dos egressos com vínculo informado está em \"{t['Tipo_Instituicao']}\" "
            f"({stats.num(t['Percentual'], 1)}%). Essa categoria reúne setores diferentes; a revisão da base "
            "prevê separar empresas não tecnológicas de outros vínculos."
        )
    rodape()
