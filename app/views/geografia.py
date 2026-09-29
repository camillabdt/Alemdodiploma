"""RF06 — origem geográfica (UF de nascimento)."""
import streamlit as st

from app.core import charts
from app.core.config import MIN_GRUPO
from app.core.privacy import frequencias
from app.views.base import Contexto, cabecalho, cartao, grafico, indicadores, leitura, pct, rodape

TITULO = "Origem geográfica"


def render(df, ctx: Contexto) -> None:
    cabecalho("Origem", "De onde vêm os egressos",
              "UF de nascimento, segundo os registros institucionais. Municípios não são exibidos.")

    tab_uf, ocultas = frequencias(df, "UF_Nascimento")
    n_ufs = df["UF_Nascimento"].nunique()
    rs = int((df["UF_Nascimento"] == "RS").sum())
    mun = ctx.metadados.get("n_municipios_nascimento") if len(df) == len(ctx.total) else None
    indicadores([
        ("Estados de origem", str(n_ufs), f"{mun} municípios na base completa" if mun else None),
        ("Nascidos no RS", pct(rs / len(df) * 100), f"{rs} egressos"),
        ("Nascidos fora do RS", str(len(df) - rs), pct((len(df) - rs) / len(df) * 100) + " do recorte"),
    ])

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        with cartao("Mapa de origem", f"Egressos por UF de nascimento; UFs com menos de {MIN_GRUPO} ficam em cinza"):
            if not tab_uf.empty:
                grafico(charts.mapa_uf(tab_uf, ctx.geojson, ""), "mapa_uf_nascimento", tab_uf, ocultas)
    with c2:
        tab_reg, ocultas_reg = frequencias(df, "Regiao_Nascimento")
        with cartao("Por região", "Egressos por região de nascimento"):
            grafico(charts.barras_horizontais(tab_reg, "Regiao_Nascimento", ""), "egressos_por_regiao", tab_reg,
                    ocultas_reg)

    if len(df) - rs >= MIN_GRUPO:
        leitura(
            f"{pct(rs / len(df) * 100)} nasceram no Rio Grande do Sul, o que confirma o papel regional do campus. "
            f"Os outros {len(df) - rs} egressos vêm de {n_ufs - 1} UFs, sinal de atração de estudantes de fora do "
            "estado."
        )
    rodape()
