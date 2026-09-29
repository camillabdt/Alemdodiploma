"""RF08/RNF06 — metodologia, definições dos indicadores e limitações."""
import pandas as pd
import streamlit as st

from app.core.config import MIN_GRUPO, MIN_TOTAL
from app.views.base import Contexto, cabecalho, pct, rodape

TITULO = "Metodologia"

DEFINICOES = pd.DataFrame([
    ["Liderança ou gerência",
     "Algum cargo, atual ou anterior, com liderança ou gestão explícita: Tech Lead, coordenador, gerente, "
     "head, supervisor, líder de equipe.",
     "\"Sênior\", \"Especialista\", \"Mentor\" ou \"Scrum Master\" isolados; liderança só em atividade estudantil."],
    ["Progressão interna",
     "Dois ou mais cargos na mesma organização com aumento de nível ou responsabilidade "
     "(júnior → pleno, estagiário → efetivo, dev → tech lead).",
     "Troca de time no mesmo nível; promoção citada em texto sem mudança de cargo."],
    ["Empreendedorismo",
     "Fundador, cofundador, sócio, proprietário ou CEO de empresa própria, em qualquer setor.",
     "Freelancer sem empresa; CEO contratado; \"intraempreendedor\"."],
    ["Mudança de área",
     "Transição explícita entre áreas distantes: da Computação para área não relacionada (ou o inverso), "
     "ou de função técnica para função não técnica.",
     "Movimentos dentro da Computação, como dev → dados, dev → gestão de TI ou técnico → produto."],
], columns=["Indicador", "É \"com evidência\" quando", "Não conta"])

CATEGORIAS = pd.DataFrame([
    ["Desenvolvimento de Software", "Desenvolvedor, engenheiro de software, full stack, mobile, tech lead"],
    ["Dados/IA", "Cientista, analista ou engenheiro de dados, ML, BI"],
    ["Infraestrutura/DevOps/Qualidade", "DevOps, SRE, cloud, segurança, DBA, QA, testes"],
    ["Produto/UX/Agilidade", "Product owner/manager, UX/UI, Scrum Master"],
    ["Gestão/Liderança", "Gerente, coordenador, head, diretor, C-level, sócio-administrador"],
    ["Ensino/Pesquisa", "Professor, pesquisador, pós-doutorando, mestrando, doutorando"],
    ["Outros em Computação/TI", "Analista de TI, analista de sistemas, suporte, consultoria de TI"],
    ["Área não relacionada à Computação", "Cargos sem componente tecnológico"],
], columns=["Categoria", "Exemplos de cargos"])


def render(df, ctx: Contexto) -> None:
    cabecalho("Metodologia", "Como os dados foram construídos",
              "Fontes, definições dos indicadores, regras de privacidade, testes estatísticos e limitações.")
    meta = ctx.metadados

    st.subheader("Fontes e cobertura")
    pop = meta.get("populacao_por_curso", {})
    n_curso = meta.get("n_por_curso", {})
    st.markdown(
        "A base integra **registros institucionais da UNIPAMPA** (curso, ano de conclusão, gênero, idade e "
        "naturalidade) com **perfis profissionais públicos do LinkedIn** (cargos, organizações e histórico). "
        "Cada perfil foi confirmado por critérios de identidade definidos no protocolo de coleta."
    )
    if pop:
        cob = pd.DataFrame({
            "Curso": list(pop.keys()),
            "População institucional": list(pop.values()),
            "Base analítica": [n_curso.get(c, 0) for c in pop],
            "Cobertura": [pct(n_curso.get(c, 0) / v * 100) for c, v in pop.items()],
        })
        st.dataframe(cob, hide_index=True, use_container_width=True)
        st.caption(
            f"Tempo desde a conclusão calculado em relação a {meta.get('ano_referencia_tempo', '—')}. "
            f"Base gerada em {meta.get('gerado_em', '—')}."
        )

    st.subheader("Indicadores de trajetória")
    st.markdown(
        "A codificação é conservadora: só conta como **com evidência** o que aparece explicitamente no perfil. "
        "\"Sem evidência observada\" não significa que o fenômeno não ocorreu."
    )
    st.dataframe(DEFINICOES, hide_index=True, use_container_width=True)

    st.subheader("Categorias do cargo atual")
    st.markdown(
        "Codifica-se o cargo mais recente. Títulos com gestão de pessoas vão para Gestão/Liderança; "
        "Tech Lead e líder técnico permanecem na categoria técnica e marcam o indicador de liderança."
    )
    st.dataframe(CATEGORIAS, hide_index=True, use_container_width=True)

    st.subheader("Privacidade")
    st.markdown(
        f"O painel mostra apenas dados agregados. Grupos com menos de {MIN_GRUPO} egressos não têm contagens nem "
        f"percentuais exibidos, e recortes com menos de {MIN_TOTAL} egressos não são mostrados. Nomes, cargos "
        "por extenso, empresas e municípios não fazem parte da base do painel. Pesquisa aprovada pelo Comitê de "
        "Ética em Pesquisa (CAAE 87973525.8.0000.5323)."
    )

    st.subheader("Testes estatísticos")
    st.dataframe(pd.DataFrame([
        ["Curso × indicador; indicador × indicador", "Exato de Fisher", "Phi",
         "Tabelas 2×2; válido com frequências baixas"],
        ["Curso × categoria do cargo ou tipo de instituição", "Qui-quadrado de independência", "V de Cramér",
         "Pressuposto verificado (≤ 20% das células com esperado < 5)"],
        ["Tempo desde a conclusão, com × sem evidência", "Mann-Whitney U", "Bisserial de postos",
         "Variável discreta e assimétrica"],
        ["Indicador ~ curso + tempo", "Regressão logística", "Razão de chances (IC 95%)",
         "Separa o efeito do curso do tempo de formado"],
    ], columns=["Pergunta", "Teste", "Efeito", "Justificativa"]), hide_index=True, use_container_width=True)
    st.caption(
        "Nível de significância de 5%. Em famílias de testes (os quatro indicadores, os seis pares) os p-valores "
        "são ajustados pelo método de Holm. As análises são associativas e não permitem conclusões causais."
    )

    st.subheader("Limitações")
    st.markdown(
        "- Perfis públicos são autodeclarados e podem estar incompletos ou desatualizados.\n"
        "- Egressos sem perfil localizável não estão na base, o que pode enviesar os resultados.\n"
        "- A base cobre uma instituição e dois cursos; não generalize para outros contextos.\n"
        "- Algumas categorias têm poucos registros, o que limita comparações.\n"
        "- A distribuição por gênero é desbalanceada; comparações por gênero exigem cautela."
    )
    rodape()
