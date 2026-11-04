"""IA explicável (XAI): que fatores de contexto se associam aos indicadores de trajetória?

Desenho (seguindo o padrão da literatura de XAI em análise educacional e de empregabilidade):

1. Dois modelos: regressão logística (caixa-branca, referência) e random forest (caixa-preta).
2. Desempenho por validação cruzada estratificada repetida (AUC ROC).
3. Explicações por valores de Shapley (SHAP) exatos e intervencionais, calculados por FATOR
   (um fator categórico com várias colunas conta como um único "jogador"). Com poucos fatores,
   o cálculo exato é barato e dispensa aproximações e a biblioteca `shap`.

Decisões metodológicas:
- A categoria do cargo NÃO entra como fator: "Gestão/Liderança" praticamente define o
  indicador de liderança (vazamento de informação), e o modelo só reproduziria a definição.
- Gênero NÃO entra como fator: o objetivo é descrever trajetórias, não atribuir resultados a
  um atributo sensível; além disso, o grupo feminino é pequeno.
- Mudança de área NÃO é modelada: são poucos casos positivos e o desempenho é instável.
- Só se exibem explicações GLOBAIS e AGREGADAS. Explicações locais descreveriam pessoas reais.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ALVOS = {
    "Indicador_Lideranca": "Liderança ou gerência",
    "Indicador_Empreendedorismo": "Empreendedorismo",
    "Indicador_Progressao": "Progressão interna",
}

FATORES = ["Curso", "Anos de formado", "Origem", "Tipo de instituição"]

SEMENTE = 2026


@dataclass
class Matriz:
    X: pd.DataFrame                 # colunas numéricas usadas pelos modelos
    grupos: dict[str, list[str]]    # fator -> colunas de X
    valores: pd.DataFrame           # valor legível de cada fator por egresso (para agregações)


def preparar(df: pd.DataFrame) -> Matriz:
    tipo = df["Tipo_Instituicao"].replace({"Sem vínculo informado": "Sem Informação"})
    dummies = pd.get_dummies(tipo, prefix="tipo", dtype=float)
    cursos = pd.get_dummies(df["Curso_de_Graduacao"].astype(str), prefix="curso", dtype=float)
    origens = pd.get_dummies(df["UF_Nascimento"].astype(str), prefix="origem", dtype=float)
    X = pd.concat([cursos, pd.DataFrame({"anos": df["Tempo_desde_Conclusao"].astype(float)}, index=df.index), origens, dummies], axis=1)
    grupos = {"Curso": list(cursos.columns), "Anos de formado": ["anos"],
              "Origem": list(origens.columns), "Tipo de instituição": list(dummies.columns)}
    valores = pd.DataFrame({
        "Curso": df["Curso_de_Graduacao"].astype(str),
        "Anos de formado": df["Tempo_desde_Conclusao"].astype(int),
        "Origem": df["UF_Nascimento"].astype(str), "Tipo de instituição": tipo,
    }, index=df.index)
    return Matriz(X=X, grupos=grupos, valores=valores)


def modelos() -> dict:
    return {
        "Regressão logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        # Sem reponderação de classes. O valor base é a média das predições
        # sobre o fundo selecionado; não é necessariamente a prevalência observada.
        "Random forest": RandomForestClassifier(
            n_estimators=150, max_depth=4, min_samples_leaf=10, random_state=SEMENTE, n_jobs=1,
        ),
    }


def shapley_por_fator(prever, X: pd.DataFrame, grupos: dict[str, list[str]],
                      fundo: pd.DataFrame) -> tuple[np.ndarray, float]:
    """Valores de Shapley exatos e intervencionais, com fatores como jogadores.

    v(S)(x) = média sobre o fundo b de f(x nas colunas de S, b nas demais).
    phi_i(x) = Σ_{S ⊆ N\\{i}} |S|!(M-|S|-1)!/M! · [v(S ∪ {i})(x) − v(S)(x)]

    Retorna (phi com forma n × M, na escala de probabilidade; valor base = v(∅)).
    Propriedade de eficiência: Σ_i phi_i(x) = f(x) − v(∅) para todo x.
    """
    jogadores = list(grupos)
    M, n, k = len(jogadores), len(X), len(fundo)
    Xv, Fv = X.to_numpy(float), fundo.to_numpy(float)
    idx = {c: i for i, c in enumerate(X.columns)}
    cols = [[idx[c] for c in grupos[j]] for j in jogadores]

    v = {}
    for tam in range(M + 1):
        for S in combinations(range(M), tam):
            dados = np.tile(Fv, (n, 1))                       # n·k linhas: cada x com todo o fundo
            for j in S:
                dados[:, cols[j]] = np.repeat(Xv[:, cols[j]], k, axis=0)
            v[S] = prever(dados).reshape(n, k).mean(axis=1)
    phi = np.zeros((n, M))
    for i in range(M):
        outros = [j for j in range(M) if j != i]
        for tam in range(M):
            peso = factorial(tam) * factorial(M - tam - 1) / factorial(M)
            for S in combinations(outros, tam):
                com_i = tuple(sorted(S + (i,)))
                phi[:, i] += peso * (v[com_i] - v[S])
    return phi, float(v[()].mean())


def explicar_validado(df: pd.DataFrame, alvo: str, repeticoes: int = 3,
                       tamanho_fundo: int = 24) -> dict:
    """Validação e Shapley fora da amostra, sem expor previsões individuais.

    Cada explicação usa um modelo que não viu o registro explicado. A primeira
    repetição de cinco partições produz as contribuições; todas as repetições
    compõem as métricas. Vocabulário e agrupamento de categorias raras são
    aprendidos só no treino. DP entre partições não é intervalo de confiança.
    """
    import hashlib
    import sklearn
    from sklearn.dummy import DummyClassifier
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
    from sklearn.base import clone

    if alvo not in ALVOS:
        raise ValueError("Indicador indisponível para o laboratório XAI.")
    if len(df) < 30:
        raise ValueError("O XAI requer pelo menos 30 registros para esta análise exploratória.")
    if len(df) > 1000:
        raise ValueError("O laboratório aceita até 1.000 registros por base.")
    y = df[alvo].to_numpy(int)
    if set(np.unique(y)) != {0, 1} or min(y.sum(), (1-y).sum()) < 10:
        raise ValueError("O XAI requer pelo menos dez registros com evidência e dez sem evidência.")
    if not 1 <= repeticoes <= 5 or not 1 <= tamanho_fundo <= 40:
        raise ValueError("Configuração de validação inválida.")
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeticoes, random_state=SEMENTE)
    nomes = list(modelos())
    dados_metricas = {n: [] for n in [*nomes, "Referência (prevalência)"]}
    contribuicoes = {n: np.zeros((len(df), len(FATORES))) for n in nomes}
    bases = {n: np.zeros(len(df)) for n in nomes}
    predicoes = {n: np.zeros(len(df)) for n in nomes}
    importancias_particao = {n: [] for n in nomes}
    erro_aditividade = {n: 0.0 for n in nomes}
    valores = preparar(df).valores
    # Grupos legíveis permanecem os originais; os modelos agrupam categorias raras.
    for particao, (treino_idx, teste_idx) in enumerate(cv.split(df, y)):
        treino, teste = df.iloc[treino_idx].copy(), df.iloc[teste_idx].copy()
        for coluna in ["Curso_de_Graduacao", "UF_Nascimento", "Tipo_Instituicao"]:
            mantidas = set(treino[coluna].astype(str).value_counts().loc[lambda x: x >= 5].index)
            treino[coluna] = treino[coluna].astype(str).where(treino[coluna].astype(str).isin(mantidas), "Outras categorias")
            teste[coluna] = teste[coluna].astype(str).where(teste[coluna].astype(str).isin(mantidas), "Outras categorias")
        mt, mv = preparar(treino), preparar(teste)
        Xt, Xv = mt.X, mv.X.reindex(columns=mt.X.columns, fill_value=0.0)
        estimadores = {**modelos(), "Referência (prevalência)": DummyClassifier(strategy="prior")}
        for nome, estimador in estimadores.items():
            modelo = clone(estimador).fit(Xt, y[treino_idx])
            probs = modelo.predict_proba(Xv)[:, 1]
            dados_metricas[nome].append({"auc": float(roc_auc_score(y[teste_idx], probs)),
                "ap": float(average_precision_score(y[teste_idx], probs)),
                "brier": float(brier_score_loss(y[teste_idx], probs))})
            if nome in nomes and particao < 5:
                fundo = Xt.sample(n=min(tamanho_fundo, len(Xt)), random_state=SEMENTE + particao)
                def prever(A, mod=modelo, cols=Xt.columns):
                    return mod.predict_proba(pd.DataFrame(A, columns=cols))[:, 1]
                phi, base = shapley_por_fator(prever, Xv, mt.grupos, fundo)
                erro = float(np.max(np.abs(phi.sum(axis=1) + base - probs)))
                if erro > 1e-7:
                    raise ValueError("Não foi possível verificar a aditividade das explicações.")
                erro_aditividade[nome] = max(erro_aditividade[nome], erro)
                contribuicoes[nome][teste_idx] = phi * 100
                bases[nome][teste_idx] = base * 100
                predicoes[nome][teste_idx] = probs * 100
                importancias_particao[nome].append(np.abs(phi * 100).mean(axis=0))
    metricas = {}
    for nome, linhas in dados_metricas.items():
        metricas[nome] = {metrica: {"mean": float(np.mean([v[metrica] for v in linhas])),
                                   "sd": float(np.std([v[metrica] for v in linhas]))}
                          for metrica in ["auc", "ap", "brier"]}
    importancia = [{"Fator": f, **{nome: float(np.abs(contribuicoes[nome][:, i]).mean()) for nome in nomes}}
                   for i, f in enumerate(FATORES)]
    efeitos = {}
    estabilidade = {}
    for nome in nomes:
        efeitos[nome] = {}
        for i, fator in enumerate(FATORES):
            tabela = pd.DataFrame({"Valor": valores[fator].to_numpy(), "SHAP": contribuicoes[nome][:, i]})
            tab = tabela.groupby("Valor").agg(n=("SHAP", "size"), Efeito=("SHAP", "mean")).reset_index()
            tab = tab[tab["n"] >= 5]
            # Supressão complementar evita isolar um único grupo raro pela média geral.
            if int(tabela.Valor.nunique()) - len(tab) == 1 and len(tab) > 0:
                tab = tab.drop(tab.n.idxmax())
            efeitos[nome][fator] = tab.to_dict(orient="records")
        parts = np.asarray(importancias_particao[nome])
        estabilidade[nome] = [{"factor": f, "mean": float(parts[:,i].mean()),
                               "sd": float(parts[:,i].std())} for i,f in enumerate(FATORES)]
    auc = {nome: [metricas[nome]["auc"]["mean"], metricas[nome]["auc"]["sd"]] for nome in nomes}
    avisos = ["Contribuições de modelos não representam causas nem efeitos de intervenções.",
              "Métricas em validação estratificada repetida; partições se sobrepõem. O desvio padrão não é um IC.",
              "Explicações fora da amostra na primeira repetição; não são explicações de um único modelo final.",
              "Combinações intervencionais de fatores podem romper correlações presentes nos dados."]
    # Zero por ausência de dados não deve ser interpretado como irrelevância do fator.
    desconhecidos = {'', 'sem informação', 'sem informacao', 'não informado', 'nao informado',
                    'não especificado', 'nao especificado', 'sem vínculo informado', 'nan', 'none'}
    qualidade = []
    for fator, coluna in zip(FATORES, ['Curso_de_Graduacao', 'Tempo_desde_Conclusao', 'UF_Nascimento', 'Tipo_Instituicao']):
        serie = df[coluna].astype(str).str.strip().str.lower()
        sem_info = serie.isin(desconhecidos).all()
        status = 'sem informação' if sem_info else 'sem variação' if serie.nunique() <= 1 else 'com variação'
        qualidade.append({'factor': fator, 'status': status})
    limitados = [q['factor'] + ' (' + q['status'] + ')' for q in qualidade if q['status'] != 'com variação']
    if limitados:
        avisos.append('Fatores limitados nesta base: ' + ', '.join(limitados) +
                      '. Contribuição zero nesses casos não demonstra irrelevância do fator.')
    if any(metricas[n]["auc"]["mean"] <= .55 for n in nomes):
        avisos.append("Ao menos um modelo ficou próximo ou abaixo da referência de AUC 0,5. Suas explicações exigem especial cautela.")
    canonico = df.sort_values("ID_Egresso").to_csv(index=False).encode()
    return {"n": len(df), "positive": int(y.sum()), "negative": int((1-y).sum()),
            "prevalence": float(y.mean()*100), "auc": auc, "metrics": metricas,
            "importance": importancia, "effects": efeitos, "stability": estabilidade,
            "factor_quality": qualidade,
            "base": {n: float(bases[n].mean()) for n in nomes},
            "prediction_mean": {n: float(predicoes[n].mean()) for n in nomes},
            "additivity_error": erro_aditividade,
            "protocol": {"version": "xai-oof-v1", "seed": SEMENTE, "folds": 5,
                         "repeats": repeticoes, "explanation_folds": 5,
                         "background_max": tamanho_fundo, "rare_category_min_train": 5,
                         "sklearn": sklearn.__version__,
                         "data_sha256": hashlib.sha256(canonico).hexdigest(),
                         "scope": "base completa", "explanations": "fora da amostra, primeira repetição"},
            "warnings": avisos,
            "references": ["https://papers.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html",
                           "https://scikit-learn.org/stable/modules/model_evaluation.html"]}
