"""RF06 — origem geográfica (UF de nascimento)."""
import streamlit as st

from app.core import charts
from app.core.config import MIN_GRUPO
from app.core.export import tabela_com_download
from app.core.privacy import frequencias
from app.views.base import Contexto, leitura, nota_ocultas, pct

TITULO = "Origem geográfica"


def render(df, ctx: Contexto) -> None:
    st.header("De onde vêm os egressos")
    st.caption("UF de nascimento, a partir dos registros institucionais. Municípios não são exibidos.")

    tab_uf, ocultas = frequencias(df, "UF_Nascimento")
    n_ufs = df["UF_Nascimento"].nunique()
    rs = int((df["UF_Nascimento"] == "RS").sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("UFs de nascimento", n_ufs)
    c2.metric("Nascidos no RS", pct(rs / len(df) * 100))
    c3.metric("Nascidos fora do RS", len(df) - rs)
    if ctx.metadados.get("n_municipios_nascimento") and len(df) == len(ctx.total):
        st.caption(f"Na base completa, os egressos nasceram em {ctx.metadados['n_municipios_nascimento']} municípios.")

    col1, col2 = st.columns([3, 2])
    with col1:
        if not tab_uf.empty:
            st.plotly_chart(charts.mapa_uf(tab_uf, ctx.geojson, "Egressos por UF de nascimento"),
                            use_container_width=True, config=charts.config_plotly("mapa_uf_nascimento"))
        nota_ocultas(ocultas)
        if ocultas:
            st.caption(f"UFs com menos de {MIN_GRUPO} egressos aparecem em cinza, sem valor.")
    with col2:
        tab_reg, ocultas_reg = frequencias(df, "Regiao_Nascimento")
        st.plotly_chart(charts.barras_horizontais(tab_reg, "Regiao_Nascimento", "Por região"),
                        use_container_width=True, config=charts.config_plotly("egressos_por_regiao"))
        nota_ocultas(ocultas_reg)
    tabela_com_download(tab_uf, "egressos_por_uf_nascimento", ctx.mostrar_tabelas)

    if len(df) - rs >= MIN_GRUPO:
        leitura(
            f"{pct(rs / len(df) * 100)} nasceram no Rio Grande do Sul, o que confirma o papel regional do campus. "
            f"Os outros {len(df) - rs} egressos vêm de {n_ufs - 1} UFs, sinal de atração de estudantes de fora do estado."
        )
