"""Além do Diploma — painel de acompanhamento de egressos de Computação da UNIPAMPA.

Executar:  streamlit run app/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from app.core import data, estilo  # noqa: E402
from app.core.config import DADOS_EXEMPLO, DADOS_PUBLICOS, MIN_TOTAL  # noqa: E402
from app.core.filters import aplicar, barra_lateral  # noqa: E402
from app.core.privacy import recorte_suficiente  # noqa: E402
from app.views import (geografia, inicio, insercao, maturidade, metodologia, relacoes,  # noqa: E402
                       trajetoria, visao_geral)
from app.views.base import Contexto  # noqa: E402

st.set_page_config(page_title="Além do Diploma · Egressos UNIPAMPA", page_icon="🎓", layout="wide")
estilo.aplicar()

PAGINAS = [inicio, visao_geral, insercao, trajetoria, maturidade, relacoes, geografia, metodologia]


def _csv_dos_secrets() -> str | None:
    try:
        return st.secrets["dados"]["csv"]
    except Exception:  # sem secrets.toml ou sem a chave
        return None


@st.cache_data
def carregar():
    """Ordem: secrets (produção) → arquivo local fora do Git → base fictícia do repositório."""
    geo = data.ler_geojson()
    csv = _csv_dos_secrets()
    if csv:
        return data.ler_dados_texto(csv), data.ler_metadados(), geo, "real"
    if DADOS_PUBLICOS.exists():
        return data.ler_dados(DADOS_PUBLICOS), data.ler_metadados(), geo, "real"
    return data.ler_dados(DADOS_EXEMPLO), {}, geo, "exemplo"


df_total, metadados, geojson, origem = carregar()

st.sidebar.title("Além do Diploma")
st.sidebar.caption("Egressos de Ciência da Computação e Engenharia de Software · UNIPAMPA Alegrete")
titulo = st.sidebar.radio("Página", [p.TITULO for p in PAGINAS], key="pagina")
pagina = next(p for p in PAGINAS if p.TITULO == titulo)

# O Streamlit descarta o estado de widgets que não são desenhados numa execução.
# Como a página inicial não mostra filtros, preservamos os valores escolhidos.
for chave in [k for k in st.session_state if str(k).startswith("f_")]:
    st.session_state[chave] = st.session_state[chave]

ctx_base = dict(total=df_total, metadados=metadados, geojson=geojson)

if pagina is inicio:
    st.sidebar.caption("A página inicial mostra a base completa. Os filtros aparecem nas demais páginas.")
    inicio.render(df_total, Contexto(**ctx_base, mostrar_tabelas=False), aviso=lambda: estilo.aviso_origem(origem))
    st.stop()

selecao = barra_lateral(df_total)
mostrar_tabelas = st.sidebar.toggle("Mostrar tabelas junto aos gráficos", value=False, key="f_tabelas")
df = aplicar(df_total, selecao)

ativos = selecao.ativos(df_total)
st.sidebar.markdown(
    f"**{len(df)}** de {len(df_total)} egressos no recorte"
    + (f" · {ativos} filtro(s) ativo(s)" if ativos else "")
)

ctx = Contexto(**ctx_base, mostrar_tabelas=mostrar_tabelas)

if pagina is not metodologia and not recorte_suficiente(df):
    st.header(pagina.TITULO)
    st.warning(
        f"O recorte tem {len(df)} egresso(s). Para proteger a privacidade, o painel só mostra resultados "
        f"com pelo menos {MIN_TOTAL} egressos. Amplie os filtros na barra lateral."
    )
    st.stop()

estilo.aviso_origem(origem)
pagina.render(df, ctx)
