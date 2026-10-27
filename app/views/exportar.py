"""RF09 — exportação do relatório agregado em PDF, HTML, Markdown, CSV e JSON."""
import json

import streamlit as st

from app.core import relatorio, xai
from app.core.config import CURSOS, MIN_GRUPO
from app.views.base import Contexto, cabecalho, indicadores, rodape

TITULO = "Exportar"


def _recorte_atual(df_total, df) -> dict:
    """Descreve, em linguagem comum, os filtros que diferem do padrão."""
    r = {}
    ss = st.session_state
    if set(ss.get("f_curso", CURSOS)) != set(CURSOS):
        r["Curso"] = ", ".join(ss["f_curso"]) or "nenhum"
    padrao_anos = (int(df_total["Ano_de_Conclusao"].min()), int(df_total["Ano_de_Conclusao"].max()))
    if tuple(ss.get("f_anos", padrao_anos)) != padrao_anos:
        r["Anos de conclusão"] = "{}–{}".format(*ss["f_anos"])
    for chave, rotulo in [("f_periodo", "Período"), ("f_genero", "Gênero"), ("f_faixa", "Faixa etária"),
                          ("f_categoria", "Categoria do cargo"), ("f_tipo", "Tipo de instituição")]:
        valores = ss.get(chave)
        if valores is not None:
            todos = {"f_periodo": df_total["Periodo_Conclusao"], "f_genero": df_total["Genero"],
                     "f_faixa": df_total["Faixa_Etaria"], "f_categoria": df_total["Categoria_Cargo"],
                     "f_tipo": df_total["Tipo_Instituicao"]}[chave].astype(str).unique()
            if set(map(str, valores)) != set(todos):
                r[rotulo] = ", ".join(map(str, valores)) or "nenhum"
    if ss.get("f_indicadores"):
        r["Somente com evidência de"] = ", ".join(xai.ALVOS.get(i, i) for i in ss["f_indicadores"])
    return r


@st.cache_data(show_spinner=False, max_entries=16)
def _gerar(df, df_total, recorte_json: str, origem: str, com_ia: bool) -> dict[str, tuple[str, bytes, str]]:
    explicacoes = {alvo: _explicar(df_total, alvo) for alvo in xai.ALVOS} if com_ia else None
    rel = relatorio.montar(df, json.loads(recorte_json), origem, explicacoes)
    return {nome: (relatorio.nome_arquivo(rel, ext), fn(rel), mime)
            for nome, (ext, mime, fn, _) in relatorio.FORMATOS.items()}


def _explicar(df_total, alvo):
    from app.views.explicacoes import _explicar as explicar_cache  # reaproveita o mesmo cache da página
    return explicar_cache(df_total, alvo)


def render(df, ctx: Contexto, origem: str = "real") -> None:
    cabecalho("Exportar", "Leve os dados com você",
              "Um relatório com todas as tabelas do painel para o recorte escolhido nos filtros.")

    recorte = _recorte_atual(ctx.total, df)
    indicadores([
        ("Egressos no recorte", str(len(df)), "de {} na base".format(len(ctx.total))),
        ("Filtros ativos", str(len(recorte)), "; ".join(f"{k}: {v}" for k, v in recorte.items())[:90] or "nenhum"),
        ("Formatos", "5", "PDF, HTML, Markdown, CSV e JSON"),
    ])
    com_ia = st.toggle("Incluir as explicações da IA (leva alguns segundos)", key="exp_ia")

    with st.spinner("Preparando os arquivos…"):
        arquivos = _gerar(df, ctx.total, json.dumps(recorte, ensure_ascii=False), origem, com_ia)

    cols = st.columns(len(arquivos), gap="small")
    for col, (nome, (arquivo, conteudo, mime)) in zip(cols, arquivos.items()):
        descricao = relatorio.FORMATOS[nome][3]
        with col.container(border=True):
            st.markdown(f'<p class="fmt-t">{nome}</p><p class="fmt-d">{descricao}</p>', unsafe_allow_html=True)
            st.download_button("Baixar", data=conteudo, file_name=arquivo, mime=mime, key=f"exp_{nome}",
                               use_container_width=True, type="primary" if nome == "PDF" else "secondary")

    st.markdown(
        f'<p class="nota-priv">Todos os arquivos contêm só dados agregados, com a mesma proteção do painel: '
        f"grupos com menos de {MIN_GRUPO} egressos aparecem como \"&lt;{MIN_GRUPO}\" ou são omitidos. "
        "Nenhum arquivo traz uma linha por egresso.</p>",
        unsafe_allow_html=True,
    )
    rodape()
