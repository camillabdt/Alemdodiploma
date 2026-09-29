"""RF02 — filtros globais na barra lateral."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from app.core.config import CURSOS, FAIXAS, INDICADORES, PERIODOS, SEM_INFORMACAO


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


def barra_lateral(df: pd.DataFrame) -> Selecao:
    st.sidebar.header("Filtros")
    ano_min, ano_max = int(df["Ano_de_Conclusao"].min()), int(df["Ano_de_Conclusao"].max())
    cursos = st.sidebar.multiselect("Curso", CURSOS, default=CURSOS, key="f_curso")
    periodos = st.sidebar.multiselect("Período de conclusão", PERIODOS, default=PERIODOS, key="f_periodo")
    anos = st.sidebar.slider("Ano de conclusão", ano_min, ano_max, (ano_min, ano_max), key="f_anos")

    with st.sidebar.expander("Perfil"):
        generos_opts = sorted(df["Genero"].unique())
        generos = st.multiselect("Gênero", generos_opts, default=generos_opts, key="f_genero")
        faixas = st.multiselect("Faixa etária", FAIXAS, default=FAIXAS, key="f_faixa")

    with st.sidebar.expander("Atuação profissional"):
        cat_opts = sorted(c for c in df["Categoria_Cargo"].unique())
        categorias = st.multiselect("Categoria do cargo atual", cat_opts, default=cat_opts, key="f_categoria")
        tipo_opts = sorted(df["Tipo_Instituicao"].unique())
        tipos = st.multiselect("Tipo de instituição", tipo_opts, default=tipo_opts, key="f_tipo")
        exigir = st.multiselect(
            "Somente egressos com evidência de",
            list(INDICADORES.keys()),
            format_func=INDICADORES.get,
            key="f_indicadores",
            help="Deixe vazio para incluir todos. Com mais de um item, o egresso precisa ter todos.",
        )
    st.sidebar.caption(
        "Categorias \"" + "\" e \"".join(SEM_INFORMACAO) + "\" ficam fora dos gráficos de atuação, "
        "mas continuam nos totais."
    )
    return Selecao(cursos, periodos, anos, generos, faixas, categorias, tipos, exigir)
