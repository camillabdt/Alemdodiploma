"""RF02 — filtros globais na barra lateral."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from app.core.config import CURSOS, FAIXAS, INDICADORES, PERIODOS


@dataclass
class Selecao:
    cursos: list[str] = field(default_factory=lambda: list(CURSOS))
    periodos: list[str] = field(default_factory=lambda: list(PERIODOS))
    anos: tuple[int, int] = (2010, 2025)
    generos: list[str] | None = None
    faixas: list[str] = field(default_factory=lambda: list(FAIXAS))
    categorias: list[str] | None = None
    tipos: list[str] | None = None
    exigir_indicadores: list[str] = field(default_factory=list)

    def ativos(self, df: pd.DataFrame) -> int:
        """Quantos filtros diferem do padrão (para exibir na barra lateral)."""
        n = 0
        n += set(self.cursos) != set(CURSOS)
        n += set(self.periodos) != set(PERIODOS)
        n += self.anos != (int(df["Ano_de_Conclusao"].min()), int(df["Ano_de_Conclusao"].max()))
        n += self.generos is not None and set(self.generos) != set(df["Genero"].unique())
        n += set(self.faixas) != set(FAIXAS)
        n += self.categorias is not None and set(self.categorias) != set(df["Categoria_Cargo"].unique())
        n += self.tipos is not None and set(self.tipos) != set(df["Tipo_Instituicao"].unique())
        n += bool(self.exigir_indicadores)
        return int(n)


def aplicar(df: pd.DataFrame, s: Selecao) -> pd.DataFrame:
    m = (
        df["Curso_de_Graduacao"].isin(s.cursos)
        & df["Periodo_Conclusao"].isin(s.periodos)
        & df["Ano_de_Conclusao"].between(*s.anos)
        & df["Faixa_Etaria"].isin(s.faixas)
    )
    if s.generos is not None:
        m &= df["Genero"].isin(s.generos)
    if s.categorias is not None:
        m &= df["Categoria_Cargo"].isin(s.categorias)
    if s.tipos is not None:
        m &= df["Tipo_Instituicao"].isin(s.tipos)
    for ind in s.exigir_indicadores:
        m &= df[ind] == 1
    return df[m]


def padroes(df: pd.DataFrame) -> dict:
    """Valor inicial de cada filtro (chave do session_state → valor)."""
    return {
        "f_curso": list(CURSOS),
        "f_periodo": list(PERIODOS),
        "f_anos": (int(df["Ano_de_Conclusao"].min()), int(df["Ano_de_Conclusao"].max())),
        "f_genero": sorted(df["Genero"].unique()),
        "f_faixa": list(FAIXAS),
        "f_categoria": sorted(df["Categoria_Cargo"].unique()),
        "f_tipo": sorted(df["Tipo_Instituicao"].unique()),
        "f_indicadores": [],
    }


def limpar(df: pd.DataFrame) -> None:
    for chave, valor in padroes(df).items():
        st.session_state[chave] = valor


def barra_lateral(df: pd.DataFrame) -> Selecao:
    # Os valores iniciais vão para o session_state uma única vez; os widgets não recebem
    # "default", o que evita o aviso de valor definido em dois lugares.
    for chave, valor in padroes(df).items():
        st.session_state.setdefault(chave, valor)
    ano_min, ano_max = int(df["Ano_de_Conclusao"].min()), int(df["Ano_de_Conclusao"].max())

    cab, botao = st.sidebar.columns([3, 2], vertical_alignment="center")
    cab.markdown('<p class="side-sec">Filtros</p>', unsafe_allow_html=True)
    botao.button("Limpar", key="limpar_filtros", on_click=limpar, args=(df,), type="tertiary")

    cursos = st.sidebar.multiselect("Curso", CURSOS, key="f_curso")
    periodos = st.sidebar.multiselect("Período de conclusão", PERIODOS, key="f_periodo")
    anos = st.sidebar.slider("Ano de conclusão", ano_min, ano_max, key="f_anos")

    with st.sidebar.expander("Perfil"):
        generos = st.multiselect("Gênero", sorted(df["Genero"].unique()), key="f_genero")
        faixas = st.multiselect("Faixa etária", FAIXAS, key="f_faixa")

    with st.sidebar.expander("Atuação profissional"):
        categorias = st.multiselect("Categoria do cargo atual", sorted(df["Categoria_Cargo"].unique()),
                                    key="f_categoria")
        tipos = st.multiselect("Tipo de instituição", sorted(df["Tipo_Instituicao"].unique()), key="f_tipo")
        exigir = st.multiselect(
            "Somente egressos com evidência de",
            list(INDICADORES.keys()),
            format_func=INDICADORES.get,
            key="f_indicadores",
            help="Deixe vazio para incluir todos. Com mais de um item, o egresso precisa ter todos.",
        )
    return Selecao(cursos, periodos, tuple(anos), generos, faixas, categorias, tipos, exigir)
