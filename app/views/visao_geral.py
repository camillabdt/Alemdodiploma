"""RF01 — visão geral da base (Shneiderman: visão geral primeiro)."""
import streamlit as st

from app.core import charts
from app.core.config import CURSOS, FAIXAS, PERIODOS
from app.core.privacy import frequencias
from app.core.stats import num
from app.views.base import Contexto, cabecalho, cartao, grafico, indicadores, leitura, pct, rodape

TITULO = "Visão geral"


def _bloco(df, coluna, titulo, subtitulo, nome, ordem=None, ordenar_por=None):
    tab, ocultas = frequencias(df, coluna)
    if ordenar_por:
        tab = tab.sort_values(ordenar_por)
    with cartao(titulo, subtitulo):
        grafico(charts.barras_verticais(tab, coluna, "", ordem), nome, tab, ocultas)


def render(df, ctx: Contexto) -> None:
    cabecalho("Perfil da base", "Quem são os egressos analisados",
              "Distribuição dos egressos no recorte selecionado por curso, período de conclusão, idade e gênero.")

    n = len(df)
    cc = int((df["Curso_de_Graduacao"] == CURSOS[0]).sum())
    cob = ctx.metadados.get("cobertura_por_curso", {})
    detalhe_cob = (f"Cobertura CC {pct(cob[CURSOS[0]] * 100)} · ES {pct(cob[CURSOS[1]] * 100)}"
                   if cob else None)
    indicadores([
        ("Egressos no recorte", str(n), f"de {len(ctx.total)} na base" if n != len(ctx.total) else detalhe_cob),
        ("Ciência da Computação", str(cc), pct(cc / n * 100) + " do recorte" if n else None),
        ("Engenharia de Software", str(n - cc), pct((n - cc) / n * 100) + " do recorte" if n else None),
        ("Anos de formado", num(df["Tempo_desde_Conclusao"].median(), 0), "mediana"),
    ])

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        _bloco(df, "Periodo_Conclusao", "Período de conclusão", "Egressos por quinquênio",
               "egressos_por_periodo", PERIODOS)
    with c2:
        _bloco(df, "Ano_de_Conclusao", "Ano de conclusão", "Egressos por ano", "egressos_por_ano",
               ordenar_por="Ano_de_Conclusao")
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        _bloco(df, "Faixa_Etaria", "Faixa etária", "Idade na data de organização da base",
               "egressos_por_faixa_etaria", FAIXAS)
    with c4:
        _bloco(df, "Genero", "Gênero", "Segundo os registros institucionais", "egressos_por_genero")

    tempo = df.groupby("Curso_de_Graduacao", observed=True)["Tempo_desde_Conclusao"].mean()
    if len(tempo) == 2:
        leitura(
            f"Os egressos de Ciência da Computação estão formados há {num(tempo.iloc[0], 1)} anos em média, "
            f"contra {num(tempo.iloc[1], 1)} em Engenharia de Software. Como liderança e empreendedorismo "
            "crescem com o tempo de carreira, comparações entre os cursos precisam considerar essa diferença "
            "(veja Trajetória por curso)."
        )
    rodape()
