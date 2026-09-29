"""Página inicial: apresenta o projeto, os números-chave e convida à exploração.

Usa sempre a base completa (sem filtros), para que a abertura seja a mesma para todos.
"""
import streamlit as st

from app.core import charts
from app.core.config import CURSOS, MIN_GRUPO
from app.core.privacy import sem_informacao
from app.core.stats import num
from app.views.base import Contexto

TITULO = "Início"

# (título da página de destino, descrição curta)
ATALHOS = [
    ("Visão geral", "Quem são os egressos: cursos, períodos, idade e gênero."),
    ("Inserção profissional", "Em que áreas e tipos de organização os egressos atuam."),
    ("Trajetória por curso", "Liderança, progressão, empreendedorismo e mudança de área."),
    ("Tempo de carreira", "Como os sinais de trajetória mudam com os anos de formado."),
    ("Origem geográfica", "De onde vêm os estudantes que se formaram em Alegrete."),
    ("Metodologia", "Fontes, definições, privacidade e limitações dos dados."),
]


def _ir_para(titulo: str) -> None:
    st.session_state["pagina"] = titulo


def _pct(parte: int, total: int) -> float:
    return parte / total * 100 if total else 0.0


def _achados(df) -> list[tuple[str, str]]:
    """Três achados calculados da base; cada um só aparece se os grupos forem grandes o bastante."""
    achados = []

    cargos = sem_informacao(df, "Categoria_Cargo")
    por_curso = {c: cargos[cargos["Curso_de_Graduacao"] == c] for c in CURSOS}
    dev = {c: int((g["Categoria_Cargo"] == "Desenvolvimento de Software").sum()) for c, g in por_curso.items()}
    if all(v >= MIN_GRUPO for v in dev.values()):
        p_cc, p_es = (_pct(dev[c], len(por_curso[c])) for c in CURSOS)
        achados.append((
            f"{num(p_es, 0)}%",
            f"dos egressos de Engenharia de Software com cargo identificado atuam em desenvolvimento de "
            f"software. Em Ciência da Computação, são {num(p_cc, 0)}%, com mais presença em ensino e pesquisa.",
        ))

    lid = df.groupby("Periodo_Conclusao", observed=True)["Indicador_Lideranca"].agg(["size", "sum"])
    if len(lid) >= 2 and (lid["size"] >= MIN_GRUPO).all() and (lid["sum"] >= MIN_GRUPO).all():
        antigo, recente = lid.iloc[0], lid.iloc[-1]
        achados.append((
            f"{num(_pct(antigo['sum'], antigo['size']), 0)}%",
            f"dos formados em {lid.index[0]} têm evidência de liderança ou gerência, contra "
            f"{num(_pct(recente['sum'], recente['size']), 0)}% dos formados em {lid.index[-1]}. "
            "A liderança acompanha o tempo de carreira.",
        ))

    rs = int((df["UF_Nascimento"] == "RS").sum())
    fora = len(df) - rs
    if fora >= MIN_GRUPO:
        achados.append((
            f"{df['UF_Nascimento'].nunique()} estados",
            f"de origem. {num(_pct(rs, len(df)), 0)}% nasceram no Rio Grande do Sul, e {fora} egressos vieram "
            "de outras partes do país para estudar no campus.",
        ))
    return achados


def render(df, ctx: Contexto, aviso=None) -> None:
    base = ctx.total
    n = len(base)
    anos = (int(base["Ano_de_Conclusao"].min()), int(base["Ano_de_Conclusao"].max()))

    st.markdown(
        f"""<section class="hero">
        <p class="kicker">UNIPAMPA · Campus Alegrete · {anos[0]}–{anos[1]}</p>
        <h1 class="hero-titulo">Além do Diploma</h1>
        <p class="hero-sub">O que acontece depois da formatura? Onde atuam os egressos de Computação,
        quem chega à liderança, quem empreende e quem muda de rumo. Um retrato de {n} trajetórias
        profissionais, construído a partir de registros da universidade e de perfis públicos.</p>
        </section>""",
        unsafe_allow_html=True,
    )
    if aviso:
        aviso()

    cc = int((base["Curso_de_Graduacao"] == CURSOS[0]).sum())
    lid = base["Indicador_Lideranca"].mean() * 100
    prog = base["Indicador_Progressao"].mean() * 100
    st.markdown(
        f"""<div class="numeros">
        <div><span class="n">{n}</span><span class="r">egressos na base</span></div>
        <div><span class="n">{cc}<small> · </small>{n - cc}</span>
             <span class="r"><i class="cc"></i>Ciência da Computação<br><i class="es"></i>Engenharia de Software</span></div>
        <div><span class="n">{num(prog, 0)}%</span><span class="r">com progressão na mesma organização</span></div>
        <div><span class="n">{num(lid, 0)}%</span><span class="r">com evidência de liderança</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

    col_graf, col_achados = st.columns([3, 2], gap="large")
    with col_graf:
        st.markdown('<p class="rotulo-secao">Cada ponto é um egresso</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="legenda-secao">Categoria do cargo atual, com as cores dos cursos.</p>',
            unsafe_allow_html=True,
        )
        fig = charts.pontos_por_categoria(base, "Categoria_Cargo", CURSOS, min_grupo=MIN_GRUPO)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col_achados:
        st.markdown('<p class="rotulo-secao">O que os dados mostram</p>', unsafe_allow_html=True)
        for numero, texto in _achados(base):
            st.markdown(
                f'<div class="achado"><span class="achado-n">{numero}</span><p>{texto}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<p class="rotulo-secao espaco">Explore o painel</p>', unsafe_allow_html=True)
    for linha in (ATALHOS[:3], ATALHOS[3:]):
        cols = st.columns(3, gap="medium")
        for col, (destino, descricao) in zip(cols, linha):
            with col.container(border=True):
                st.markdown(f'<p class="atalho-t">{destino}</p><p class="atalho-d">{descricao}</p>',
                            unsafe_allow_html=True)
                st.button("Abrir →", key=f"ir_{destino}", on_click=_ir_para, args=(destino,),
                          type="tertiary")

    st.markdown(
        f"""<footer class="rodape">
        Trabalho de Conclusão de Curso em Engenharia de Software · UNIPAMPA Alegrete.
        Resultados sempre agregados; grupos com menos de {MIN_GRUPO} egressos não são exibidos.
        Pesquisa aprovada pelo Comitê de Ética em Pesquisa (CAAE 87973525.8.0000.5323).
        </footer>""",
        unsafe_allow_html=True,
    )
