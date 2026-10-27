"""IA explicável: fatores associados aos indicadores de trajetória (explicações globais e agregadas)."""
import pandas as pd
import streamlit as st

from app.core import charts, xai
from app.core.config import MIN_GRUPO
from app.core.stats import num
from app.views.base import (Contexto, cabecalho, cartao, grafico, indicadores, leitura, nota_estatistica, rodape,
                            secao)

TITULO = "Explicações (IA)"
USA_FILTROS = False  # o modelo é ajustado sobre a base completa

MODELO_PRINCIPAL = "Random forest"


@st.cache_data(show_spinner=False, max_entries=8)
def _explicar(df: pd.DataFrame, alvo: str) -> xai.Explicacao:
    return xai.explicar(df, alvo)


def _virada(tab: pd.DataFrame) -> int | None:
    """Primeiro ano a partir do qual o efeito médio fica positivo e assim permanece."""
    t = tab.sort_values("Valor").reset_index(drop=True)
    for i in range(len(t)):
        if (t.loc[i:, "Efeito"] > 0).all():
            return int(t.loc[i, "Valor"])
    return None


def _leitura(exp: xai.Explicacao, anos: dict[str, pd.DataFrame], nome: str) -> str:
    imp = exp.importancia
    top_rf = imp[MODELO_PRINCIPAL].idxmax()
    top_lr = imp["Regressão logística"].idxmax()
    partes = []
    if top_rf == top_lr:
        partes.append(f"Os dois modelos apontam o mesmo fator como o mais associado a {nome.lower()}: "
                      f"<b>{top_rf.lower()}</b>.")
    else:
        partes.append(f"O random forest aponta <b>{top_rf.lower()}</b> como fator principal, e a regressão "
                      f"logística aponta <b>{top_lr.lower()}</b>; a divergência pede cautela na interpretação.")
    virada = _virada(anos.get(MODELO_PRINCIPAL, pd.DataFrame(columns=["Valor", "Efeito"])))
    if top_rf == "Anos de formado" and virada:
        partes.append(f"O efeito dos anos de formado passa a ser positivo a partir de cerca de {virada} anos "
                      "depois da conclusão.")
    tipo = xai.efeito_medio(exp, MODELO_PRINCIPAL, "Tipo de instituição", MIN_GRUPO)
    sem = tipo[tipo["Valor"] == "Sem Informação"]
    if not sem.empty and sem["Efeito"].iloc[0] < -5:
        partes.append("Perfis sem informação de vínculo aparecem associados a menos evidência. Isso diz mais sobre "
                      "a completude dos perfis públicos do que sobre as trajetórias: perfis incompletos mostram "
                      "menos sinais de qualquer tipo.")
    return " ".join(partes)


def render(df, ctx: Contexto) -> None:
    cabecalho(
        "IA explicável", "O que se associa a cada trajetória",
        "Dois modelos de aprendizado de máquina estimam a chance de cada sinal de trajetória a partir do curso, "
        "dos anos de formado, da origem e do tipo de instituição. As explicações mostram quanto cada fator "
        "contribui, em média, para essas estimativas. Os resultados descrevem associações na base, não causas, "
        "e nunca se referem a pessoas individualmente.",
    )

    alvo = st.radio("Indicador", list(xai.ALVOS), format_func=xai.ALVOS.get, horizontal=True, key="xai_alvo",
                    label_visibility="collapsed")
    nome = xai.ALVOS[alvo]
    with st.spinner("Ajustando os modelos e calculando as explicações…"):
        exp = _explicar(ctx.total, alvo)

    (a_lr, s_lr), (a_rf, s_rf) = exp.auc["Regressão logística"], exp.auc[MODELO_PRINCIPAL]
    concordam = exp.importancia[MODELO_PRINCIPAL].idxmax() == exp.importancia["Regressão logística"].idxmax()
    indicadores([
        ("Taxa na base", f"{num(exp.positivos / exp.n * 100, 1)}%", f"{exp.positivos} de {exp.n} egressos"),
        ("AUC · regressão logística", num(a_lr, 2), f"± {num(s_lr, 2)} na validação cruzada"),
        ("AUC · random forest", num(a_rf, 2), f"± {num(s_rf, 2)} na validação cruzada"),
        ("Fator principal", exp.importancia[MODELO_PRINCIPAL].idxmax(),
         "os dois modelos concordam" if concordam else "os modelos divergem"),
    ])

    with st.expander("Como ler esta página"):
        st.markdown(
            "- **AUC** mede o quanto o modelo separa quem tem e quem não tem o sinal: 0,5 equivale a sorteio e "
            "1,0 seria separação perfeita. Valores entre 0,6 e 0,7 indicam associação real, mas fraca demais "
            "para prever casos individuais, e por isso o painel não faz previsões sobre pessoas.\n"
            "- **Contribuição (pp)** é o quanto um fator desloca, em média, a chance estimada, em pontos "
            "percentuais. É calculada com valores de Shapley (SHAP), que repartem a estimativa entre os fatores.\n"
            "- **Efeito positivo** (verde) indica que o grupo tende a ter mais evidência do sinal do que a média; "
            "**negativo** (terracota), menos.\n"
            "- Quando os dois modelos, um simples e um flexível, apontam o mesmo padrão, a explicação é mais confiável."
        )

    with cartao("Importância dos fatores", f"Contribuição média de cada fator para a chance estimada de {nome.lower()}"):
        imp = exp.importancia.copy()
        tabela_imp = imp.round(2).reset_index().rename(columns={"index": "Fator"})
        grafico(charts.importancia_fatores(imp), f"importancia_fatores_{alvo}", tabela_imp)

    anos = {m: xai.efeito_medio(exp, m, "Anos de formado", MIN_GRUPO) for m in exp.efeitos}
    with cartao("Efeito dos anos de formado", "Contribuição média por ano desde a conclusão, nos dois modelos"):
        dados_anos = pd.concat([t.assign(Modelo=m) for m, t in anos.items()], ignore_index=True)
        grafico(charts.efeito_anos(anos), f"efeito_anos_{alvo}",
                dados_anos.rename(columns={"Valor": "Anos de formado"}).round(2))

    with cartao("Efeito por grupo", "Random forest · média dos grupos com 5 ou mais egressos"):
        fator = st.radio("Fator", ["Tipo de instituição", "Curso", "Origem"], key="xai_fator", horizontal=True,
                         label_visibility="collapsed")
        tab = xai.efeito_medio(exp, MODELO_PRINCIPAL, fator, MIN_GRUPO)
        grafico(charts.efeito_categorias(tab), f"efeito_{fator}_{alvo}", tab.rename(columns={"Valor": fator}).round(2))

    nota_estatistica(
        "Regressão logística (com variáveis padronizadas) e random forest (150 árvores, profundidade máxima 4, "
        "mínimo de 10 egressos por folha). AUC por validação cruzada estratificada de 5 partições, repetida 5 "
        "vezes. Valores de Shapley exatos e intervencionais por fator, com fundo de 40 egressos sorteados; "
        "conferidos contra a biblioteca SHAP. A categoria do cargo e o gênero não entram como fatores, e mudança "
        "de área não é modelada por ter poucos casos (ver Metodologia)."
    )
    secao("O que os modelos mostram")
    leitura(_leitura(exp, anos, nome))
    rodape()
