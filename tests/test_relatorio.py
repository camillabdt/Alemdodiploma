"""Relatório exportável: conteúdo agregado e os cinco formatos."""
import io
import json
import zipfile

import pytest

from app.core import relatorio as R
from app.core.config import MIN_GRUPO, MIN_TOTAL


@pytest.fixture(scope="module")
def rel(df_exemplo):
    return R.montar(df_exemplo, {"Curso": "ambos"}, "exemplo")


def test_so_dados_agregados(rel, df_exemplo):
    for t in rel.tabelas():
        assert len(t.dados) < len(df_exemplo) / 5, t.nome      # nenhuma tabela tem uma linha por egresso
        assert not {"ID_Egresso", "Cargo_Atual", "Local_de_Trabalho"} & set(t.dados.columns)


def test_frequencias_respeitam_grupo_minimo(rel):
    for t in rel.tabelas():
        if "Quantidade" in t.dados.columns:
            assert (t.dados["Quantidade"] >= MIN_GRUPO).all(), t.nome


def test_recorte_pequeno_e_recusado(df_exemplo):
    with pytest.raises(ValueError):
        R.montar(df_exemplo.head(MIN_TOTAL - 1), {})


def test_cinco_formatos(rel):
    pdf = R.para_pdf(rel)
    assert pdf[:4] == b"%PDF"
    html = R.para_html(rel).decode()
    assert html.startswith("<!doctype html>") and "prefers-color-scheme" in html
    md = R.para_markdown(rel).decode()
    assert md.startswith("# ") and "| --- |" in md
    doc = json.loads(R.para_json(rel))
    assert doc["dados"].startswith("fictícios") and len(doc["secoes"]) >= 6
    z = zipfile.ZipFile(io.BytesIO(R.para_csv_zip(rel)))
    assert "LEIAME.txt" in z.namelist() and len(z.namelist()) == len(rel.tabelas()) + 1


def test_pdf_aceita_caracteres_fora_do_latin1():
    assert R._latin1("2010–2014 ≥ 5 → “ok”") == '2010-2014 >= 5 -> "ok"'
