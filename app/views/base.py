"""Utilidades compartilhadas pelas páginas."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from app.core.config import MIN_GRUPO


@dataclass
class Contexto:
    total: pd.DataFrame          # base completa (sem filtros)
    metadados: dict
    geojson: dict
    mostrar_tabelas: bool


def nota_ocultas(n: int) -> None:
    if n:
        st.caption(
            f"{n} categoria(s) com menos de {MIN_GRUPO} egressos não aparecem, para proteger a privacidade."
        )


def leitura(texto: str) -> None:
    """Síntese curta, calculada a partir dos dados filtrados (nunca texto fixo)."""
    st.markdown(f"**Leitura:** {texto}")


def pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")
