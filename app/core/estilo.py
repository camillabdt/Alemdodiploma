"""Camada visual: tipografia, cartões de indicadores e aviso de dados preliminares."""
import streamlit as st

from app.core.config import COR_PRINCIPAL, COR_SECUNDARIA, COR_TEXTO

# Mude para False quando a base revisada (auditoria + dupla codificação) estiver pronta.
DADOS_PRELIMINARES = True

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,650&display=swap');

h1, h2, h3 {{ font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif !important;
              color: {COR_TEXTO}; letter-spacing: -0.01em; }}
h1 {{ font-weight: 650 !important; }}
h2, h3 {{ font-weight: 500 !important; }}
.block-container {{ padding-top: 2.2rem; max-width: 1180px; }}

[data-testid="stMetric"] {{ border-left: 3px solid {COR_PRINCIPAL}; padding: 0.35rem 0 0.35rem 0.9rem; }}
[data-testid="stMetricValue"] {{ font-family: 'Source Serif 4', Georgia, serif; font-weight: 500; }}

.capa {{ margin: 0 0 1.6rem 0; padding-bottom: 1.4rem; border-bottom: 1px solid #DCE4E0; }}
.capa .titulo {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 2.9rem; font-weight: 650;
                 line-height: 1.05; color: {COR_TEXTO}; margin: 0; }}
.capa .sub {{ font-size: 1.1rem; color: #4A5A56; max-width: 62ch; margin-top: 0.6rem; line-height: 1.5; }}
.capa .cursos {{ margin-top: 0.9rem; font-size: 0.95rem; color: #4A5A56; }}
.capa .cc, .capa .es {{ display: inline-block; width: 0.7rem; height: 0.7rem; border-radius: 2px;
                        margin: 0 0.35rem 0 0; vertical-align: baseline; }}
.capa .cc {{ background: {COR_PRINCIPAL}; }}
.capa .es {{ background: {COR_SECUNDARIA}; margin-left: 1rem; }}

.aviso {{ background: #FBF4E8; border-left: 3px solid {COR_SECUNDARIA}; padding: 0.6rem 0.9rem;
          font-size: 0.92rem; color: #5A4520; margin-bottom: 1.4rem; }}
</style>
"""


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def aviso_origem(origem: str) -> None:
    if origem == "exemplo":
        st.markdown(
            '<div class="aviso"><b>Dados fictícios.</b> Esta instância está usando a base de demonstração do '
            "repositório. Os números não correspondem a egressos reais.</div>",
            unsafe_allow_html=True,
        )
    elif DADOS_PRELIMINARES:
        st.markdown(
            '<div class="aviso"><b>Versão preliminar.</b> A base ainda passa por auditoria da coleta e revisão '
            "da codificação dos cargos; os números podem mudar na versão final.</div>",
            unsafe_allow_html=True,
        )


def capa(n: int) -> None:
    st.markdown(
        f"""<div class="capa">
        <p class="titulo">Além do Diploma</p>
        <p class="sub">Para onde vão os egressos de Computação da UNIPAMPA depois da formatura: onde atuam,
        quem chega à liderança, quem empreende e quem muda de área. {n} trajetórias de 2010 a 2025.</p>
        <p class="cursos"><span class="cc"></span>Ciência da Computação<span class="es"></span>Engenharia de Software</p>
        </div>""",
        unsafe_allow_html=True,
    )
