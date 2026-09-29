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

/* ---------- menu lateral ---------- */
[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 0.1rem; }}
[data-testid="stSidebar"] div[role="radiogroup"] label {{ padding: 0.38rem 0.7rem; border-radius: 6px;
    border-left: 3px solid transparent; width: 100%; margin: 0; cursor: pointer; }}
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{ display: none; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: #E4ECE8; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
    background: #FFFFFF; border-left-color: {COR_PRINCIPAL}; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{ font-weight: 600; color: {COR_TEXTO}; }}

/* ---------- página inicial ---------- */
.hero {{ padding: 1.2rem 0 1.6rem 0; }}
.kicker {{ text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.78rem; font-weight: 600;
          color: {COR_PRINCIPAL}; margin: 0 0 0.6rem 0; }}
.hero-titulo {{ font-family: 'Source Serif 4', Georgia, serif !important; font-size: clamp(2.8rem, 6vw, 4.6rem) !important;
               font-weight: 650 !important; line-height: 0.98 !important; margin: 0 !important; padding: 0 !important;
               color: {COR_TEXTO}; letter-spacing: -0.025em; }}
.hero-sub {{ font-size: 1.18rem; line-height: 1.55; color: #3E4E4A; max-width: 60ch; margin: 1rem 0 0 0; }}

.numeros {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.4rem;
           border-top: 1px solid #DCE4E0; border-bottom: 1px solid #DCE4E0; padding: 1.3rem 0; margin-bottom: 2rem; }}
.numeros > div {{ display: flex; flex-direction: column; gap: 0.3rem; }}
.numeros .n {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 2.5rem; line-height: 1; color: {COR_TEXTO}; }}
.numeros .n small {{ color: #9AA8A3; font-size: 1.6rem; }}
.numeros .r {{ font-size: 0.9rem; color: #4A5A56; line-height: 1.35; }}
.numeros i {{ display: inline-block; width: 0.62rem; height: 0.62rem; border-radius: 2px; margin-right: 0.3rem; }}
.numeros i.cc {{ background: {COR_PRINCIPAL}; }} .numeros i.es {{ background: {COR_SECUNDARIA}; }}
@media (max-width: 800px) {{ .numeros {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

.rotulo-secao {{ text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.76rem; font-weight: 600;
                color: #5C6B67; margin: 0 0 0.3rem 0; }}
.rotulo-secao.espaco {{ margin-top: 2.2rem; margin-bottom: 0.8rem; }}
.legenda-secao {{ font-size: 0.92rem; color: #5C6B67; margin: 0; }}

.achado {{ border-left: 3px solid {COR_SECUNDARIA}; padding: 0.2rem 0 0.2rem 1rem; margin: 0.9rem 0 1.4rem 0; }}
.achado-n {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 2.3rem; line-height: 1; color: {COR_TEXTO}; }}
.achado p {{ margin: 0.35rem 0 0 0; font-size: 1rem; line-height: 1.5; color: #3E4E4A; }}

.atalho-t {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.25rem; margin: 0 0 0.2rem 0; color: {COR_TEXTO}; }}
.atalho-d {{ font-size: 0.92rem; color: #4A5A56; margin: 0; min-height: 2.8em; line-height: 1.4; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: #DCE4E0 !important; border-radius: 10px !important;
    transition: border-color .15s ease, box-shadow .15s ease; }}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{ border-color: {COR_PRINCIPAL} !important;
    box-shadow: 0 2px 10px rgba(27, 110, 106, 0.08); }}

.rodape {{ margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid #DCE4E0; font-size: 0.85rem;
          color: #6A7874; line-height: 1.55; }}
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
