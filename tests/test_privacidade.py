"""RNF01: nenhum grupo com menos de MIN_GRUPO egressos pode ter números exibidos."""
import numpy as np
import pandas as pd

from app.core.config import MIN_GRUPO, MIN_TOTAL
from app.core.privacy import MASCARA, cruzada, frequencias, mascarar, recorte_suficiente, taxa_por_grupo


def _base():
    # Grupo A com 20 pessoas, grupo B com 3 (pequeno demais).
    return pd.DataFrame({
        "grupo": ["A"] * 20 + ["B"] * 3,
        "cat": ["x"] * 12 + ["y"] * 6 + ["z"] * 2 + ["x"] * 3,
        "ind": [1] * 8 + [0] * 12 + [1, 1, 0],
    })


def test_mascarar():
    assert mascarar(0) == "0"
    assert mascarar(MIN_GRUPO - 1) == MASCARA
    assert mascarar(MIN_GRUPO) == str(MIN_GRUPO)


def test_frequencias_oculta_categorias_pequenas():
    tab, ocultas = frequencias(_base(), "cat")
    assert (tab["Quantidade"] >= MIN_GRUPO).all()
    assert ocultas == 1  # "z" tem 2
    # O percentual usa a base inteira (23), não só as categorias visíveis.
    assert tab.loc[tab["cat"] == "x", "Percentual"].item() == round(15 / 23 * 100, 1)


def test_taxa_por_grupo_suprime_grupo_pequeno():
    t = taxa_por_grupo(_base(), "grupo", "ind").set_index("grupo")
    assert t.loc["A", "Percentual"] == 40.0
    assert np.isnan(t.loc["B", "Percentual"])
    assert t.loc["B", "Com evidência"] == MASCARA


def test_cruzada_suprime_celulas_e_colunas_pequenas():
    cont, pct = cruzada(_base(), "cat", "grupo")
    assert pct["B"].isna().all()          # coluna B tem 3 pessoas
    assert np.isnan(pct.loc["z", "A"])     # célula z/A tem 2
    assert cont.loc["z", "A"] == MASCARA


def test_recorte_minimo():
    assert not recorte_suficiente(pd.DataFrame({"a": range(MIN_TOTAL - 1)}))
    assert recorte_suficiente(pd.DataFrame({"a": range(MIN_TOTAL)}))
