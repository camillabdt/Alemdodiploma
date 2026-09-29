"""RF09 — exportação de tabelas para relatórios e reuniões."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd
import streamlit as st


def _slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def tabela_com_download(df: pd.DataFrame, nome: str, mostrar: bool = True, **kwargs) -> None:
    """Mostra a tabela (se pedido) e oferece o CSV. UTF-8 com BOM abre corretamente no Excel."""
    if mostrar:
        st.dataframe(df, hide_index=kwargs.pop("hide_index", True), use_container_width=True, **kwargs)
    st.download_button(
        "Baixar tabela (CSV)",
        data=df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"{_slug(nome)}.csv",
        mime="text/csv",
        key=f"dl_{_slug(nome)}",
    )
