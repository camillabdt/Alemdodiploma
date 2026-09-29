"""Gera uma base FICTÍCIA com o mesmo formato da base pública.

Uso:
    python -m pipeline.gerar_exemplo

Serve para o repositório público: permite rodar o painel e os testes sem expor
dados de pessoas reais. Cada linha é sorteada de forma independente a partir de
proporções aproximadas; nenhuma linha é derivada de um egresso real.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.core.config import DADOS_EXEMPLO
from pipeline.preparar_dados import COLUNAS_PUBLICAS, REGIAO_POR_UF, periodo_conclusao

N = 280
SEMENTE = 42
ANO_REFERENCIA = 2026

CATEGORIAS = {
    "Desenvolvimento de Software": 0.34, "Dados/IA": 0.11, "Outros em Computação/TI": 0.11,
    "Gestão/Liderança": 0.09, "Ensino/Pesquisa": 0.08, "Área não relacionada à Computação": 0.07,
    "Infraestrutura/DevOps/Qualidade": 0.06, "Produto/UX/Agilidade": 0.05, "Sem Informação": 0.09,
}
TIPOS = {
    "Empresa Privada não Tecnológica/Outros": 0.55, "Empresa Privada de Tecnologia": 0.24,
    "Ensino/Pesquisa": 0.09, "Setor Público": 0.04, "Sem Informação": 0.08,
}
UFS = {"RS": 0.84, "SC": 0.03, "PR": 0.02, "SP": 0.03, "MG": 0.03, "GO": 0.02, "RJ": 0.01, "PA": 0.01, "BA": 0.01}


def _sorteio(rng, dist: dict, n: int):
    chaves = list(dist)
    p = np.array(list(dist.values()), dtype=float)
    return rng.choice(chaves, size=n, p=p / p.sum())


def _logit(x):
    return 1 / (1 + np.exp(-x))


def gerar(n: int = N, semente: int = SEMENTE) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    curso = rng.choice(["Ciência da Computação", "Engenharia de Software"], size=n)
    anos = np.arange(2010, 2026)
    pesos = np.linspace(1, 3, len(anos))
    ano = np.array([
        rng.choice(anos[anos >= (2010 if c == "Ciência da Computação" else 2013)],
                   p=(w := pesos[anos >= (2010 if c == "Ciência da Computação" else 2013)]) / w.sum())
        for c in curso
    ])
    tempo = ANO_REFERENCIA - ano
    idade = 23 + tempo + rng.integers(-1, 4, size=n)
    faixa = pd.cut(idade, [0, 24, 29, 34, 39, 200],
                   labels=["20–24", "25–29", "30–34", "35–39", "40 ou mais"]).astype(str)
    uf = _sorteio(rng, UFS, n)
    df = pd.DataFrame({
        "ID_Egresso": [f"X{i:03d}" for i in range(1, n + 1)],
        "Curso_de_Graduacao": curso,
        "Ano_de_Conclusao": ano,
        "Periodo_Conclusao": [periodo_conclusao(a) for a in ano],
        "Tempo_desde_Conclusao": tempo,
        "Genero": rng.choice(["Masculino", "Feminino"], size=n, p=[0.82, 0.18]),
        "Faixa_Etaria": faixa,
        "UF_Nascimento": uf,
        "Regiao_Nascimento": [REGIAO_POR_UF[u] for u in uf],
        "Categoria_Cargo": _sorteio(rng, CATEGORIAS, n),
        "Tipo_Instituicao": _sorteio(rng, TIPOS, n),
    })
    lid = rng.random(n) < _logit(-2.2 + 0.15 * tempo)
    df["Indicador_Lideranca"] = lid.astype(int)
    df["Indicador_Progressao"] = (rng.random(n) < _logit(-0.7 + 0.04 * tempo + 0.8 * lid)).astype(int)
    df["Indicador_Empreendedorismo"] = (rng.random(n) < _logit(-3.8 + 0.1 * tempo + 1.8 * lid)).astype(int)
    df["Indicador_Mudanca_Area"] = (rng.random(n) < _logit(-3.2 + 0.08 * tempo)).astype(int)
    return df[COLUNAS_PUBLICAS]


def main() -> None:
    df = gerar()
    DADOS_EXEMPLO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DADOS_EXEMPLO, index=False)
    print(f"Base fictícia: {len(df)} registros -> {DADOS_EXEMPLO}")


if __name__ == "__main__":
    main()
