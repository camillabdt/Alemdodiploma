"""Gera a base pública consumida pelo dashboard a partir da base privada.

Uso:
    python -m pipeline.preparar_dados
    python -m pipeline.preparar_dados --entrada data/privado/dataset_gold.csv --ano-referencia 2026

Entradas (NUNCA versionadas):
    data/privado/dataset_gold.csv   base analítica completa (com cargo e local de trabalho)

Saídas:
    data/publico/dataset_publico.csv        base sem quase-identificadores diretos (NÃO versionada)
    .streamlit/secrets.toml                 a mesma base, no formato de secrets do Streamlit (NÃO versionado)
    data/publico/metadados.json             data de referência, contagens e cobertura
    data/privado/divergencias_codebook.csv  cargos em que a codificação manual difere da regra

O que sai da base pública e por quê:
    Cargo_Atual, Local_de_Trabalho  texto livre, permite reidentificar pessoas
    Local_Nascimento (município)    reduzido a UF e região
    Ano_Sabatico                    removido da análise por baixa ocorrência (n=2)
    colunas textuais Sim/Não        redundantes com os indicadores 0/1
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

from pipeline.codebook import classificar_cargo

ROOT = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = ROOT / "data" / "privado" / "dataset_gold.csv"
SAIDA_DADOS = ROOT / "data" / "publico" / "dataset_publico.csv"
SAIDA_META = ROOT / "data" / "publico" / "metadados.json"
SAIDA_DIVERGENCIAS = ROOT / "data" / "privado" / "divergencias_codebook.csv"
SAIDA_SECRETS = ROOT / ".streamlit" / "secrets.toml"

# População institucional (registros da UNIPAMPA). Atualize se a lista mudar.
POPULACAO = {"Ciência da Computação": 171, "Engenharia de Software": 158}

UF_POR_ESTADO = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
    "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
    "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
    "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
    "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
    "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
    "Sergipe": "SE", "Tocantins": "TO",
}
REGIAO_POR_UF = {
    **dict.fromkeys(["AC", "AP", "AM", "PA", "RO", "RR", "TO"], "Norte"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
    **dict.fromkeys(["DF", "GO", "MT", "MS"], "Centro-Oeste"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
    **dict.fromkeys(["PR", "RS", "SC"], "Sul"),
}

COLUNAS_OBRIGATORIAS = [
    "ID_Egresso", "Curso_de_Graduacao", "Ano_de_Conclusao", "Cargo_Atual", "Categoria_Cargo",
    "Tipo_Instituicao", "Genero", "Faixa_Etaria", "Local_Nascimento",
    "Indicador_Lideranca", "Indicador_Progressao", "Indicador_Empreendedorismo",
    "Indicador_Mudanca_Area",
]

COLUNAS_PUBLICAS = [
    "ID_Egresso", "Curso_de_Graduacao", "Ano_de_Conclusao", "Periodo_Conclusao",
    "Tempo_desde_Conclusao", "Genero", "Faixa_Etaria", "UF_Nascimento", "Regiao_Nascimento",
    "Categoria_Cargo", "Tipo_Instituicao", "Indicador_Lideranca", "Indicador_Progressao",
    "Indicador_Empreendedorismo", "Indicador_Mudanca_Area",
]


def periodo_conclusao(ano: int) -> str:
    """Intervalos usados no texto do TCC."""
    if ano <= 2014:
        return "2010–2014"
    if ano <= 2019:
        return "2015–2019"
    return "2020–2025"


def validar(df: pd.DataFrame) -> None:
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes na base privada: {faltando}")
    if df["ID_Egresso"].duplicated().any():
        raise ValueError("Há ID_Egresso duplicado na base privada.")
    for col in [c for c in df.columns if c.startswith("Indicador_")]:
        if not set(df[col].unique()) <= {0, 1}:
            raise ValueError(f"{col} deve conter apenas 0 e 1.")


def transformar(df: pd.DataFrame, ano_referencia: int) -> pd.DataFrame:
    out = df.copy()
    estado = out["Local_Nascimento"].str.split(",").str[-2].str.strip()
    out["UF_Nascimento"] = estado.map(UF_POR_ESTADO)
    if out["UF_Nascimento"].isna().any():
        desconhecidos = sorted(estado[out["UF_Nascimento"].isna()].unique())
        raise ValueError(f"Estados não reconhecidos em Local_Nascimento: {desconhecidos}")
    out["Regiao_Nascimento"] = out["UF_Nascimento"].map(REGIAO_POR_UF)
    out["Periodo_Conclusao"] = out["Ano_de_Conclusao"].map(periodo_conclusao)
    out["Tempo_desde_Conclusao"] = ano_referencia - out["Ano_de_Conclusao"]
    return out[COLUNAS_PUBLICAS].sort_values("ID_Egresso").reset_index(drop=True)


def divergencias_codebook(df: pd.DataFrame) -> pd.DataFrame:
    regra = df["Cargo_Atual"].map(classificar_cargo)
    div = df.loc[regra != df["Categoria_Cargo"], ["ID_Egresso", "Cargo_Atual", "Categoria_Cargo"]].copy()
    div["Categoria_Regra"] = regra[div.index]
    div["Decisao_Revisao"] = ""  # manter manual | adotar regra | outra (preencher)
    div["Justificativa"] = ""
    return div.rename(columns={"Categoria_Cargo": "Categoria_Manual"})


def metadados(df_priv: pd.DataFrame, df_pub: pd.DataFrame, ano_referencia: int) -> dict:
    por_curso = df_pub["Curso_de_Graduacao"].value_counts().to_dict()
    municipios = df_priv["Local_Nascimento"].str.split(",").str[0].str.strip().nunique()
    return {
        "gerado_em": date.today().isoformat(),
        "ano_referencia_tempo": ano_referencia,
        "n_base_analitica": int(len(df_pub)),
        "n_por_curso": {k: int(v) for k, v in por_curso.items()},
        "populacao_por_curso": POPULACAO,
        "cobertura_por_curso": {
            k: round(por_curso.get(k, 0) / v, 4) for k, v in POPULACAO.items()
        },
        "n_municipios_nascimento": int(municipios),
        "n_ufs_nascimento": int(df_pub["UF_Nascimento"].nunique()),
        "anos_conclusao": [int(df_pub["Ano_de_Conclusao"].min()), int(df_pub["Ano_de_Conclusao"].max())],
    }


def escrever_secrets(publico: pd.DataFrame) -> None:
    """Grava a base real em .streamlit/secrets.toml (fora do Git).

    O conteúdo desse arquivo é colado em Settings → Secrets no Streamlit Cloud,
    para que o app publicado leia os dados reais sem que eles estejam no repositório.
    """
    csv = publico.to_csv(index=False)
    if "\'\'\'" in csv:
        raise ValueError("A base contém três aspas simples seguidas; não é possível gravar em TOML literal.")
    SAIDA_SECRETS.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_SECRETS.write_text(f"[dados]\ncsv = \'\'\'\n{csv}\'\'\'\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entrada", type=Path, default=ENTRADA_PADRAO)
    parser.add_argument("--ano-referencia", type=int, default=2026)
    args = parser.parse_args()

    df = pd.read_csv(args.entrada)
    validar(df)
    publico = transformar(df, args.ano_referencia)
    div = divergencias_codebook(df)

    SAIDA_DADOS.parent.mkdir(parents=True, exist_ok=True)
    publico.to_csv(SAIDA_DADOS, index=False)
    SAIDA_META.write_text(
        json.dumps(metadados(df, publico, args.ano_referencia), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    div.to_csv(SAIDA_DIVERGENCIAS, index=False, encoding="utf-8-sig")
    escrever_secrets(publico)

    concord = 1 - len(div) / len(df)
    print(f"Base pública: {len(publico)} registros -> {SAIDA_DADOS.relative_to(ROOT)}")
    print(f"Metadados -> {SAIDA_META.relative_to(ROOT)}")
    print(f"Concordância regra × codificação manual: {concord:.1%} ({len(div)} divergências)")
    print(f"Revise as divergências em {SAIDA_DIVERGENCIAS.relative_to(ROOT)}")
    print(f"Secrets para o Streamlit Cloud -> {SAIDA_SECRETS.relative_to(ROOT)} (copie o conteúdo em Settings → Secrets)")


if __name__ == "__main__":
    main()
