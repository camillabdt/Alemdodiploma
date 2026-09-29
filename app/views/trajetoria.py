"""RF05 — indicadores de trajetória por curso, com controle do tempo desde a conclusão."""
import pandas as pd

from app.core import charts, stats
from app.core.config import INDICADORES, MIN_GRUPO
from app.core.privacy import taxa_por_grupo
from app.views.base import (Contexto, cabecalho, cartao, grafico, indicadores, leitura, nota_estatistica, pct,
                            rodape, secao, tabela, vazio)

TITULO = "Trajetória por curso"


def render(df, ctx: Contexto) -> None:
    cabecalho("Trajetória profissional", "Sinais de trajetória além do cargo atual",
              "\"Com evidência\" significa que o perfil público mostra o fenômeno de forma explícita; "
              "a ausência não prova que ele não ocorreu. Definições na página Metodologia.")

    indicadores([(nome, pct(df[ind].mean() * 100), f"{int(df[ind].sum())} de {len(df)} egressos")
                 for ind, nome in INDICADORES.items()])

    linhas = []
    for ind, nome in INDICADORES.items():
        t = taxa_por_grupo(df, "Curso_de_Graduacao", ind)
        t["Indicador"] = nome
        linhas.append(t.rename(columns={"Curso_de_Graduacao": "Curso"}))
    taxas = pd.concat(linhas, ignore_index=True)
    with cartao("Indicadores por curso", "Percentual de egressos com evidência de cada sinal"):
        grafico(charts.taxas_indicadores(taxas, ""), "indicadores_por_curso",
                taxas[["Indicador", "Curso", "n (grupo)", "Com evidência", "Percentual"]])

    if df["Curso_de_Graduacao"].nunique() < 2:
        vazio("Selecione os dois cursos nos filtros para ver as comparações estatísticas.")
        rodape()
        return

    secao("Os cursos diferem?",
          "Primeiro a comparação direta; depois, a comparação que mantém constante o tempo de formado, "
          "já que os egressos de CC estão formados há mais tempo, em média.")

    brutos = [stats.associacao(df, "Curso_de_Graduacao", ind) for ind in INDICADORES]
    p_holm = stats.holm([r["p"] if r else 1.0 for r in brutos])
    testes = pd.DataFrame({
        "Indicador": list(INDICADORES.values()),
        "Teste": [r["teste"] if r else "—" for r in brutos],
        "Phi": [stats.num(r["efeito"], 3) if r else "—" for r in brutos],
        "p": [stats.formatar_p(r["p"]) if r else "—" for r in brutos],
        "p ajustado (Holm)": [stats.formatar_p(p) for p in p_holm],
    })
    with cartao("Comparação direta", "Curso × indicador"):
        tabela(testes, "comparacao_cursos_indicadores")
        nota_estatistica("Exato de Fisher em cada tabela 2×2; efeito pelo coeficiente Phi; p-valores ajustados "
                         "pelo método de Holm para os quatro indicadores.")

    linhas_reg = []
    for ind, nome in INDICADORES.items():
        r = stats.regressao_logistica(df, ind)
        if r is None:
            continue
        for c in r["coeficientes"]:
            linhas_reg.append({"Indicador": nome, "Termo": c["Termo"],
                               "Razão de chances": stats.num(c["Razão de chances"]),
                               "IC 95%": f"{stats.num(c['IC 95% inf.'])} a {stats.num(c['IC 95% sup.'])}",
                               "p": stats.formatar_p(c["p"]), "n": r["n"]})
    with cartao("Comparação controlada pelo tempo de formado", "Regressão logística: indicador ~ curso + tempo"):
        if linhas_reg:
            tabela(pd.DataFrame(linhas_reg), "regressao_logistica_indicadores")
            nota_estatistica(
                "Razão de chances acima de 1 indica maior chance de evidência. Para o curso, compara ES com CC; "
                "para o tempo, o efeito de cada ano a mais de formado. Intervalos que incluem 1 indicam efeito "
                f"incerto. Indicadores com menos de {MIN_GRUPO} casos em algum grupo não são modelados."
            )
        else:
            vazio("O recorte atual é pequeno demais para estimar os modelos.")

    lid = [l for l in linhas_reg if l["Indicador"] == "Liderança ou gerência"]
    if len(lid) == 2:
        leitura(
            f"Mantido o tempo de formado constante, a razão de chances de liderança de ES em relação a CC é "
            f"{lid[0]['Razão de chances']} (IC 95% {lid[0]['IC 95%']}; p = {lid[0]['p']}). Cada ano a mais "
            f"desde a conclusão multiplica a chance por {lid[1]['Razão de chances']}."
        )
    rodape()
