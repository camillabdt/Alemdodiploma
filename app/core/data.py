"""Leitura da base pública, metadados e geometria dos estados.

Funções puras compartilhadas pela API e pelos testes.
"""
from __future__ import annotations

import json
import io
from pathlib import Path

import pandas as pd

from app.core.config import CURSOS, DADOS_PUBLICOS, FAIXAS, GEOJSON_UF, INDICADORES, METADADOS, PERIODOS

COLUNAS_ESPERADAS = [
    "ID_Egresso", "Curso_de_Graduacao", "Ano_de_Conclusao", "Periodo_Conclusao",
    "Tempo_desde_Conclusao", "Genero", "Faixa_Etaria", "UF_Nascimento", "Regiao_Nascimento",
    "Categoria_Cargo", "Tipo_Instituicao", *INDICADORES.keys(),
]

# Colunas que jamais podem chegar ao dashboard (RNF01).
COLUNAS_PROIBIDAS = ["Cargo_Atual", "Local_de_Trabalho", "Local_Nascimento", "Nome", "URL_Perfil"]


def ler_dados(caminho: Path | io.StringIO = DADOS_PUBLICOS) -> pd.DataFrame:
    """Lê a base a partir de um caminho ou de um buffer de texto."""
    df = pd.read_csv(caminho, sep=None, engine="python", encoding="utf-8-sig")
    proibidas = [c for c in COLUNAS_PROIBIDAS if c in df.columns]
    if proibidas:
        raise ValueError(
            f"A base pública contém colunas identificáveis: {proibidas}. "
            "Gere-a novamente com `python -m pipeline.preparar_dados`."
        )
    faltando = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes na base pública: {faltando}")

    if df.empty:
        raise ValueError("A base está vazia.")
    if df["ID_Egresso"].isna().any() or df["ID_Egresso"].duplicated().any():
        raise ValueError("Cada registro precisa de um ID_Egresso preenchido e único.")
    for coluna in COLUNAS_ESPERADAS:
        if df[coluna].isna().any():
            raise ValueError(f"Preencha a coluna {coluna}; use Sem Informação para texto desconhecido.")
    for coluna in ["Ano_de_Conclusao", "Tempo_desde_Conclusao", *INDICADORES]:
        try:
            valores = pd.to_numeric(df[coluna], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{coluna} precisa conter números válidos.") from exc
        if not (valores % 1 == 0).all():
            raise ValueError(f"{coluna} precisa conter números inteiros.")
        df[coluna] = valores.astype(int)
    if not df["Ano_de_Conclusao"].between(1900, 2100).all() or (df["Tempo_desde_Conclusao"] < 0).any():
        raise ValueError("Verifique anos de conclusão e tempo desde a conclusão.")
    for coluna in INDICADORES:
        if not df[coluna].isin([0, 1]).all():
            raise ValueError(f"{coluna} aceita somente 0 ou 1, conforme o protocolo de codificação.")
    desconhecidas = sorted(set(df.columns) - set(COLUNAS_ESPERADAS))
    if desconhecidas:
        raise ValueError(f"Remova as colunas extras antes de importar: {desconhecidas}")
    for coluna in ["Curso_de_Graduacao", "Periodo_Conclusao", "Faixa_Etaria", "Genero", "Categoria_Cargo", "Tipo_Instituicao"]:
        df[coluna] = df[coluna].astype(str).str.strip()
        if (df[coluna] == "").any():
            raise ValueError(f"A coluna {coluna} contém texto vazio.")
    df["Curso_de_Graduacao"] = pd.Categorical(df["Curso_de_Graduacao"], opcoes(df, "Curso_de_Graduacao", CURSOS), ordered=True)
    df["Periodo_Conclusao"] = pd.Categorical(df["Periodo_Conclusao"], opcoes(df, "Periodo_Conclusao", PERIODOS), ordered=True)
    df["Faixa_Etaria"] = pd.Categorical(df["Faixa_Etaria"], opcoes(df, "Faixa_Etaria", FAIXAS), ordered=True)
    return df


def ler_metadados(caminho: Path = METADADOS) -> dict:
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def ler_geojson(caminho: Path = GEOJSON_UF) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def ler_dados_texto(csv: str) -> pd.DataFrame:
    return ler_dados(io.StringIO(csv.strip()))


def opcoes(df: pd.DataFrame, coluna: str, preferidas=()) -> list[str]:
    valores = set(df[coluna].dropna().astype(str))
    return [v for v in preferidas if v in valores] + sorted(valores - set(preferidas))
