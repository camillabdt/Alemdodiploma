"""RF01 — visão geral da base (Shneiderman: visão geral primeiro)."""
import streamlit as st

from app.core import charts
from app.core.config import FAIXAS, PERIODOS
from app.core.export import tabela_com_download
from app.core.privacy import frequencias
from app.core.stats import num
from app.views.base import Contexto, leitura, nota_ocultas, pct

TITULO = "Visão geral"


def render(df, ctx: Contexto) -> None:
    st.subheader("Quem são os egressos analisados")
    n, n_total = len(df), len(ctx.total)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Egressos no recorte", n, help=f"De {n_total} na base analítica.")
    c2.metric("Ciência da Computação", int((df["Curso_de_Graduacao"] == "Ciência da Computação").sum()))
    c3.metric("Engenharia de Software", int((df["Curso_de_Graduacao"] == "Engenharia de Software").sum()))
    c4.metric("Anos de formado (mediana)", f"{df['Tempo_desde_Conclusao'].median():.0f}")

    meta = ctx.metadados
    if meta.get("populacao_por_curso"):
        cob = meta["cobertura_por_curso"]
        st.caption(
            f"Cobertura da base em relação à população institucional: "
            f"CC {pct(cob['Ciência da Computação'] * 100)}, ES {pct(cob['Engenharia de Software'] * 100)}. "
            "Os resultados representam os egressos com perfil público localizado e validado."
        )

    col1, col2 = st.columns(2)
    with col1:
        tab, ocultas = frequencias(df, "Periodo_Conclusao")
        st.plotly_chart(charts.barras_verticais(tab, "Periodo_Conclusao", "Por período de conclusão", PERIODOS),
                        use_container_width=True, config=charts.config_plotly("egressos_por_periodo"))
        nota_ocultas(ocultas)
        tabela_com_download(tab, "egressos_por_periodo", ctx.mostrar_tabelas)
    with col2:
        tab, ocultas = frequencias(df, "Ano_de_Conclusao")
        tab = tab.sort_values("Ano_de_Conclusao")
        st.plotly_chart(charts.barras_verticais(tab, "Ano_de_Conclusao", "Por ano de conclusão"),
                        use_container_width=True, config=charts.config_plotly("egressos_por_ano"))
        nota_ocultas(ocultas)
        tabela_com_download(tab, "egressos_por_ano", ctx.mostrar_tabelas)

    col3, col4 = st.columns(2)
    with col3:
        tab, ocultas = frequencias(df, "Faixa_Etaria")
        st.plotly_chart(charts.barras_verticais(tab, "Faixa_Etaria", "Por faixa etária", FAIXAS),
                        use_container_width=True, config=charts.config_plotly("egressos_por_faixa"))
        nota_ocultas(ocultas)
        tabela_com_download(tab, "egressos_por_faixa_etaria", ctx.mostrar_tabelas)
    with col4:
        tab, ocultas = frequencias(df, "Genero")
        st.plotly_chart(charts.barras_verticais(tab, "Genero", "Por gênero"),
                        use_container_width=True, config=charts.config_plotly("egressos_por_genero"))
        nota_ocultas(ocultas)
        tabela_com_download(tab, "egressos_por_genero", ctx.mostrar_tabelas)

    tempo = df.groupby("Curso_de_Graduacao", observed=True)["Tempo_desde_Conclusao"].mean()
    if len(tempo) == 2:
        leitura(
            f"os egressos de Ciência da Computação estão formados há {num(tempo.iloc[0], 1)} anos em média, "
            f"contra {num(tempo.iloc[1], 1)} em Engenharia de Software. Como liderança e empreendedorismo "
            "crescem com o tempo de carreira, comparações entre cursos precisam considerar essa diferença "
            "(veja a página Trajetória por curso)."
        )
