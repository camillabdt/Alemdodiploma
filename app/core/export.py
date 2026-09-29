"""RF09 — exportação de tabelas para relatórios e reuniões."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd
import streamlit as st


def _slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def botao_csv(df: pd.DataFrame, nome: str) -> None:
    """CSV com ; e vírgula decimal, UTF-8 com BOM: abre direto no Excel em português."""
    st.download_button(
        "↓ Baixar CSV",
        data=df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"{_slug(nome)}.csv",
        mime="text/csv",
        key=f"dl_{_slug(nome)}",
        type="tertiary",
    )


def tabela_com_download(df: pd.DataFrame, nome: str, mostrar: bool = True, **kwargs) -> None:
    """Mantida por compatibilidade com código antigo."""
    if mostrar:
        st.dataframe(df, hide_index=kwargs.pop("hide_index", True), use_container_width=True, **kwargs)
    botao_csv(df, nome)
