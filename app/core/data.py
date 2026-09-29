"""Leitura da base pública, metadados e geometria dos estados.

Funções puras (sem Streamlit) para poderem ser testadas; o cache fica em app.py.
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
    """Lê a base a partir de um caminho ou de um buffer de texto (secrets)."""
    df = pd.read_csv(caminho)
    proibidas = [c for c in COLUNAS_PROIBIDAS if c in df.columns]
    if proibidas:
        raise ValueError(
            f"A base pública contém colunas identificáveis: {proibidas}. "
            "Gere-a novamente com `python -m pipeline.preparar_dados`."
        )
    faltando = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes na base pública: {faltando}")

    df["Curso_de_Graduacao"] = pd.Categorical(df["Curso_de_Graduacao"], CURSOS, ordered=True)
    df["Periodo_Conclusao"] = pd.Categorical(df["Periodo_Conclusao"], PERIODOS, ordered=True)
    df["Faixa_Etaria"] = pd.Categorical(df["Faixa_Etaria"], FAIXAS, ordered=True)
    return df


def ler_metadados(caminho: Path = METADADOS) -> dict:
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def ler_geojson(caminho: Path = GEOJSON_UF) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def ler_dados_texto(csv: str) -> pd.DataFrame:
    return ler_dados(io.StringIO(csv.strip()))
