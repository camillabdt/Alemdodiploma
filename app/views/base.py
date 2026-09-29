"""Componentes visuais compartilhados pelas páginas.

Toda página segue o mesmo esqueleto: cabeçalho → indicadores → cartões de gráfico
(com dados e download recolhidos) → leitura → rodapé. Assim o painel tem uma
identidade única e o conteúdo é o que chama atenção, não os controles.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from html import escape

import pandas as pd
import streamlit as st

from app.core import charts
from app.core.config import MIN_GRUPO
from app.core.export import botao_csv


@dataclass
class Contexto:
    total: pd.DataFrame          # base completa (sem filtros)
    metadados: dict
    geojson: dict
    mostrar_tabelas: bool = False


def pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")


def cabecalho(kicker: str, titulo: str, descricao: str | None = None) -> None:
    desc = f'<p class="pg-desc">{descricao}</p>' if descricao else ""
    st.markdown(
        f'<header class="pg"><p class="kicker">{escape(kicker)}</p>'
        f'<h1 class="pg-titulo">{escape(titulo)}</h1>{desc}</header>',
        unsafe_allow_html=True,
    )


def indicadores(itens: list[tuple[str, str, str | None]]) -> None:
    """Cartões de número: (rótulo, valor, detalhe opcional)."""
    celulas = "".join(
        f'<div class="kpi"><span class="kpi-r">{escape(r)}</span><span class="kpi-v">{escape(v)}</span>'
        + (f'<span class="kpi-d">{escape(d)}</span>' if d else "")
        + "</div>"
        for r, v, d in itens
    )
    st.markdown(f'<div class="kpis kpis-{min(len(itens), 4)}">{celulas}</div>', unsafe_allow_html=True)


def secao(titulo: str, descricao: str | None = None) -> None:
    desc = f'<p class="sec-desc">{descricao}</p>' if descricao else ""
    st.markdown(f'<h2 class="sec">{escape(titulo)}</h2>{desc}', unsafe_allow_html=True)


@contextmanager
def cartao(titulo: str, subtitulo: str | None = None):
    with st.container(border=True):
        sub = f'<p class="card-sub">{escape(subtitulo)}</p>' if subtitulo else ""
        st.markdown(f'<p class="card-t">{escape(titulo)}</p>{sub}', unsafe_allow_html=True)
        yield


def grafico(fig, nome: str, dados: pd.DataFrame | None = None, ocultas: int = 0) -> None:
    """Desenha a figura sem título próprio (o título vem do cartão) e recolhe os dados."""
    tem_legenda = any(getattr(t, "showlegend", None) is not False for t in fig.data) and len(fig.data) > 1
    fig.update_layout(title_text="", margin=dict(t=36 if tem_legenda else 12))
    st.plotly_chart(fig, use_container_width=True, config=charts.config_plotly(nome))
    if ocultas:
        st.markdown(
            f'<p class="nota-priv">{ocultas} categoria(s) com menos de {MIN_GRUPO} egressos ocultada(s) '
            "para proteger a privacidade.</p>",
            unsafe_allow_html=True,
        )
    if dados is not None and not dados.empty:
        with st.expander("Ver dados"):
            st.dataframe(dados, hide_index=True, use_container_width=True)
            botao_csv(dados, nome)


def tabela(dados: pd.DataFrame, nome: str) -> None:
    """Tabela principal (conteúdo, não apoio), com download discreto."""
    st.dataframe(dados, hide_index=True, use_container_width=True)
    botao_csv(dados, nome)


def nota_estatistica(texto: str, aviso: str | None = None) -> None:
    extra = f'<br><span class="nota-aviso">{escape(aviso)}</span>' if aviso else ""
    st.markdown(f'<p class="nota-est"><span>Teste</span>{texto}{extra}</p>', unsafe_allow_html=True)


def leitura(texto: str) -> None:
    """Síntese curta calculada a partir do recorte filtrado (nunca texto fixo)."""
    st.markdown(f'<div class="leitura"><span>Leitura</span><p>{texto}</p></div>', unsafe_allow_html=True)


def vazio(texto: str) -> None:
    st.markdown(f'<div class="vazio">{escape(texto)}</div>', unsafe_allow_html=True)


def rodape() -> None:
    st.markdown(
        '<footer class="rodape">Além do Diploma · Trabalho de Conclusão de Curso em Engenharia de Software · '
        f"UNIPAMPA Alegrete. Resultados agregados; grupos com menos de {MIN_GRUPO} egressos não são exibidos. "
        "CAAE 87973525.8.0000.5323.</footer>",
        unsafe_allow_html=True,
    )


# Compatibilidade: nota de categorias ocultas fora de um cartão.
def nota_ocultas(n: int) -> None:
    if n:
        st.markdown(f'<p class="nota-priv">{n} categoria(s) com menos de {MIN_GRUPO} egressos ocultada(s).</p>',
                    unsafe_allow_html=True)
