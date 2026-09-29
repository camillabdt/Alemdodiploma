"""Teste de fumaça: todas as páginas carregam sem erro, e a trava de privacidade atua."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.views import geografia, inicio, insercao, maturidade, metodologia, relacoes, trajetoria, visao_geral

PAGINAS = [inicio, visao_geral, insercao, trajetoria, maturidade, relacoes, geografia, metodologia]

APP = str(Path(__file__).resolve().parents[1] / "app" / "app.py")


@pytest.fixture(scope="module")
def at():
    return AppTest.from_file(APP, default_timeout=60).run()


@pytest.mark.parametrize("titulo", [p.TITULO for p in PAGINAS])
def test_pagina_carrega(at, titulo):
    at.sidebar.radio(key="pagina").set_value(titulo).run()
    assert not at.exception, [e.value for e in at.exception]


def test_recorte_pequeno_bloqueia_resultados():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.radio(key="pagina").set_value("Trajetória por curso").run()
    at.multiselect(key="f_indicadores").set_value(
        ["Indicador_Empreendedorismo", "Indicador_Mudanca_Area"]).run()
    assert any("proteger a privacidade" in w.value for w in at.warning)
    assert len(at.get("plotly_chart")) == 0


def test_app_le_dados_dos_secrets(df_exemplo):
    """Em produção a base vem de st.secrets; aqui usamos a fictícia para simular."""
    import streamlit as st

    st.cache_data.clear()  # o carregamento é cacheado entre execuções no mesmo processo
    at = AppTest.from_file(APP, default_timeout=60)
    at.secrets["dados"] = {"csv": df_exemplo.to_csv(index=False)}
    at.run()
    at.sidebar.radio(key="pagina").set_value("Visão geral").run()
    assert not at.exception
    assert any(str(len(df_exemplo)) in m.value for m in at.sidebar.markdown)


def test_inicio_e_pagina_padrao_e_atalho_navega():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert at.sidebar.radio(key="pagina").value == "Início"
    assert not at.sidebar.multiselect  # a página inicial não mostra filtros
    at.button(key="ir_Trajetória por curso").click().run()
    assert at.sidebar.radio(key="pagina").value == "Trajetória por curso"
    assert not at.exception


def test_filtros_sobrevivem_a_ida_ao_inicio():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.radio(key="pagina").set_value("Visão geral").run()
    at.multiselect(key="f_curso").set_value(["Engenharia de Software"]).run()
    at.sidebar.radio(key="pagina").set_value("Início").run()
    at.sidebar.radio(key="pagina").set_value("Visão geral").run()
    assert at.multiselect(key="f_curso").value == ["Engenharia de Software"]
