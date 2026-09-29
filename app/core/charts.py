"""Gráficos padronizados (Plotly) com o tema visual do dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from app.core.config import (COR_CURSO, COR_NEUTRA, COR_PRINCIPAL, COR_SECUNDARIA, COR_TEXTO,
                             ESCALA_SEQUENCIAL, INDICADORES)

FONTE = "Source Sans Pro, Segoe UI, Helvetica, Arial, sans-serif"

pio.templates["egressos"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONTE, size=14, color=COR_TEXTO),
        title=dict(font=dict(size=16), x=0, xanchor="left", y=0.98, yanchor="top"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=[COR_PRINCIPAL, COR_SECUNDARIA, COR_NEUTRA, "#4E6E8E", "#9C5B4A"],
        xaxis=dict(showgrid=False, linecolor="#C9D3CF", ticks="outside", tickcolor="#C9D3CF"),
        yaxis=dict(gridcolor="#EDF1EF", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text=""),
        margin=dict(l=10, r=20, t=95, b=10),
        hoverlabel=dict(font_family=FONTE),
    )
)
pio.templates.default = "egressos"


def config_plotly(nome_arquivo: str) -> dict:
    """RF09: botão da barra do gráfico baixa PNG em alta resolução com nome descritivo."""
    return {
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
        "toImageButtonOptions": {"format": "png", "filename": nome_arquivo, "scale": 3},
    }


def barras_horizontais(tab: pd.DataFrame, coluna: str, titulo: str) -> go.Figure:
    tab = tab.sort_values("Quantidade")
    texto = [f"{q} ({p:.1f}%)".replace(".", ",") for q, p in zip(tab["Quantidade"], tab["Percentual"])]
    fig = go.Figure(go.Bar(x=tab["Quantidade"], y=tab[coluna], orientation="h", text=texto,
                           textposition="outside", marker_color=COR_PRINCIPAL, cliponaxis=False,
                           hovertemplate="%{y}: %{x} egressos<extra></extra>"))
    fig.update_layout(legend_title_text="", title=titulo, height=max(260, 42 * len(tab) + 90),
                      xaxis_title="Egressos", yaxis_title="",
                      xaxis_range=[0, float(tab["Quantidade"].max()) * 1.45 if len(tab) else 1])
    return fig


def barras_verticais(tab: pd.DataFrame, coluna: str, titulo: str, ordem: list | None = None) -> go.Figure:
    if ordem:
        tab = tab.set_index(coluna).reindex([o for o in ordem if o in set(tab[coluna])]).reset_index()
    fig = go.Figure(go.Bar(x=tab[coluna].astype(str), y=tab["Quantidade"], text=tab["Quantidade"],
                           textposition="outside", marker_color=COR_PRINCIPAL, cliponaxis=False))
    fig.update_layout(legend_title_text="", title=titulo, height=340, xaxis_title="", yaxis_title="Egressos")
    return fig


def barras_por_curso(pct: pd.DataFrame, titulo: str, eixo_categoria: str) -> go.Figure:
    """pct: linhas = categorias, colunas = cursos (percentual dentro do curso)."""
    longo = pct.reset_index().melt(id_vars=pct.index.name, var_name="Curso", value_name="Percentual")
    longo = longo.dropna(subset=["Percentual"])
    ordem = pct.mean(axis=1).sort_values().index.tolist()
    fig = px.bar(longo, y=pct.index.name, x="Percentual", color="Curso", barmode="group",
                 orientation="h", color_discrete_map=COR_CURSO,
                 category_orders={pct.index.name: ordem[::-1]},
                 text=longo["Percentual"].map(lambda v: f"{v:.1f}%".replace(".", ",")))
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(legend_title_text="", title=titulo, height=max(320, 60 * len(pct) + 110),
                      xaxis_title="% dentro do curso", yaxis_title="")
    fig.update_yaxes(title_text=eixo_categoria if eixo_categoria else "")
    return fig


def taxas_indicadores(taxas: pd.DataFrame, titulo: str) -> go.Figure:
    """taxas: colunas Indicador, Curso, Percentual."""
    fig = px.bar(taxas.dropna(subset=["Percentual"]), x="Indicador", y="Percentual", color="Curso",
                 barmode="group", color_discrete_map=COR_CURSO,
                 category_orders={"Indicador": list(INDICADORES.values())},
                 text=taxas.dropna(subset=["Percentual"])["Percentual"].map(lambda v: f"{v:.1f}%".replace(".", ",")))
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(legend_title_text="", title=titulo, height=400, xaxis_title="", yaxis_title="% com evidência")
    return fig


def tempo_por_indicador(linhas: pd.DataFrame, titulo: str) -> go.Figure:
    """linhas: Indicador, Grupo (Com/Sem evidência), Média."""
    fig = px.bar(linhas, x="Indicador", y="Média", color="Grupo", barmode="group",
                 color_discrete_map={"Com evidência": COR_PRINCIPAL, "Sem evidência observada": COR_NEUTRA},
                 category_orders={"Indicador": list(INDICADORES.values()),
                                  "Grupo": ["Sem evidência observada", "Com evidência"]},
                 text=linhas["Média"].map(lambda v: f"{v:.1f}".replace(".", ",")))
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(legend_title_text="", title=titulo, height=400, xaxis_title="", yaxis_title="Média de anos desde a conclusão")
    return fig


def taxa_por_periodo(tab: pd.DataFrame, titulo: str) -> go.Figure:
    """tab: Periodo_Conclusao, Indicador, Percentual."""
    fig = px.line(tab.dropna(subset=["Percentual"]), x="Periodo_Conclusao", y="Percentual",
                  color="Indicador", markers=True,
                  color_discrete_sequence=[COR_PRINCIPAL, COR_SECUNDARIA, "#4E6E8E", "#9C5B4A"])
    fig.update_layout(legend_title_text="", title=titulo, height=380, xaxis_title="Período de conclusão",
                      yaxis_title="% com evidência")
    return fig


def matriz_phi(matriz: pd.DataFrame, titulo: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=matriz.values, x=matriz.columns, y=matriz.index, zmin=-1, zmax=1,
        colorscale=[[0, "#9C5B4A"], [0.5, "#F5F7F6"], [1, COR_PRINCIPAL]],
        text=[[("" if pd.isna(v) else f"{v:.2f}".replace(".", ",")) for v in row] for row in matriz.values],
        texttemplate="%{text}", hovertemplate="%{y} × %{x}: Phi = %{z:.2f}<extra></extra>",
        colorbar=dict(title="Phi")))
    fig.update_layout(legend_title_text="", title=titulo, height=420, yaxis=dict(autorange="reversed"))
    return fig


def mapa_uf(tab: pd.DataFrame, geojson: dict, titulo: str) -> go.Figure:
    """Mapa coroplético por UF desenhado com polígonos simples.

    Não usa subplots geográficos do Plotly, que baixam um mapa-base da internet;
    assim o mapa funciona offline e em redes institucionais com bloqueios.
    Escala logarítmica: o RS concentra a maioria e, em escala linear, apagaria as demais UFs.
    tab: UF_Nascimento, Quantidade (apenas UFs com n >= MIN_GRUPO).
    """
    import math

    import plotly.colors as pc

    valores = dict(zip(tab["UF_Nascimento"], tab["Quantidade"]))
    vmin, vmax = (min(valores.values()), max(valores.values())) if valores else (1, 1)
    lmin, lmax = math.log10(vmin), math.log10(vmax)

    def cor(v):
        t = 1.0 if lmax == lmin else (math.log10(v) - lmin) / (lmax - lmin)
        return pc.sample_colorscale(ESCALA_SEQUENCIAL, [0.2 + 0.8 * t])[0]

    fig = go.Figure()
    for f in geojson["features"]:
        uf, nome = f["id"], f["properties"]["nome"]
        v = valores.get(uf)
        preenchimento = cor(v) if v else "#F1F4F2"
        texto = f"{nome}: {v} egressos" if v else f"{nome}: sem egressos ou menos de 5"
        geo = f["geometry"]
        poligonos = [geo["coordinates"]] if geo["type"] == "Polygon" else geo["coordinates"]
        for poligono in poligonos:
            xs, ys = zip(*poligono[0])
            fig.add_trace(go.Scatter(x=xs, y=ys, fill="toself", fillcolor=preenchimento, mode="lines",
                                     line=dict(color="white", width=0.8), hoveron="fills",
                                     text=texto, hoverinfo="text", showlegend=False))
    if valores:
        marcas = [m for m in (5, 10, 25, 50, 100, 250) if vmin <= m <= vmax] or [vmin, vmax]
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(colorscale=[[0, pc.sample_colorscale(ESCALA_SEQUENCIAL, [0.2])[0]],
                                    [1, ESCALA_SEQUENCIAL[-1]]],
                        cmin=lmin, cmax=lmax, color=[lmin], showscale=True,
                        colorbar=dict(title="Egressos", tickvals=[math.log10(m) for m in marcas],
                                      ticktext=[str(m) for m in marcas], thickness=12, len=0.6))))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1.05)
    fig.update_layout(legend_title_text="", title=titulo, height=560, margin=dict(l=0, r=0, t=50, b=0),
                      hovermode="closest")
    return fig


def pontos_por_categoria(df: pd.DataFrame, coluna: str, ordem_cursos: list[str], por_linha: int = 24,
                         min_grupo: int = 5) -> go.Figure:
    """Gráfico de unidades: cada ponto é um egresso, agrupado por categoria e colorido por curso.

    Mostra contagens agregadas (não identifica pessoas). Categorias com menos de
    `min_grupo` egressos em algum curso são somadas em "Outras categorias".
    """
    cont = df.groupby([coluna, "Curso_de_Graduacao"], observed=True).size().unstack(fill_value=0)
    cont = cont.reindex(columns=ordem_cursos, fill_value=0)
    pequenas = cont[(cont > 0).any(axis=1) & ((cont > 0) & (cont < min_grupo)).any(axis=1)].index
    if len(pequenas):
        outras = cont.loc[pequenas].sum()
        cont = cont.drop(pequenas)
        if outras.sum():
            cont.loc["Outras categorias"] = outras
    ordem = cont.sum(axis=1).sort_values(ascending=False).index.tolist()
    fim = [c for c in ("Outras categorias", "Sem Informação") if c in ordem]
    cont = cont.loc[[c for c in ordem if c not in fim] + fim]

    xs, ys, cores, textos = [], [], [], []
    rotulos_y, posicoes_y = [], []
    y = 0.0
    for categoria, linha in cont.iterrows():
        cursos = [c for c in ordem_cursos for _ in range(int(linha[c]))]
        n_linhas = max(1, -(-len(cursos) // por_linha))
        topo = y
        for i, curso in enumerate(cursos):
            xs.append(i % por_linha)
            ys.append(topo - (i // por_linha))
            cores.append(COR_CURSO.get(curso, COR_NEUTRA))
            textos.append(f"{categoria}<br>{curso}: {int(linha[curso])} egressos")
        rotulos_y.append(f"{categoria}  <b>{int(linha.sum())}</b>")
        posicoes_y.append(topo - (n_linhas - 1) / 2)
        y = topo - n_linhas - 0.9
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers", text=textos, hoverinfo="text",
                               marker=dict(size=11, color=cores, line=dict(width=0), symbol="circle")))
    fig.update_xaxes(visible=False, range=[-0.8, por_linha - 0.2])
    fig.update_yaxes(tickvals=posicoes_y, ticktext=rotulos_y, showgrid=False, zeroline=False,
                     ticks="", showline=False, range=[y + 0.4, 0.9], tickfont=dict(size=13.5))
    fig.update_layout(height=int(22 * (-y) + 40), margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, hovermode="closest")
    return fig
