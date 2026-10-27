"""Relatório exportável (RF09): as mesmas tabelas agregadas do painel, em cinco formatos.

Regra de privacidade: o relatório é montado apenas com as funções de app.core.privacy,
então herda a supressão de grupos com menos de MIN_GRUPO egressos. Nenhum formato
contém uma linha por egresso.
"""
from __future__ import annotations

import io
import json
import re
import unicodedata
import zipfile
from dataclasses import dataclass, field
from datetime import date
from html import escape
from itertools import combinations

import numpy as np
import pandas as pd

from app.core import stats
from app.core.config import CURSOS, FAIXAS, INDICADORES, MIN_GRUPO, MIN_TOTAL, PERIODOS, ROTULOS
from app.core.privacy import cruzada, frequencias, mascarar, sem_informacao, taxa_por_grupo

TITULO = "Além do Diploma · Relatório de egressos"


@dataclass
class Tabela:
    nome: str            # identificador de arquivo (sem espaços)
    titulo: str
    dados: pd.DataFrame
    nota: str = ""


@dataclass
class Secao:
    titulo: str
    texto: str = ""
    tabelas: list[Tabela] = field(default_factory=list)


@dataclass
class Relatorio:
    gerado_em: str
    recorte: dict
    secoes: list[Secao]
    origem_dados: str

    def tabelas(self) -> list[Tabela]:
        return [t for s in self.secoes for t in s.tabelas]


# --------------------------------------------------------------------------- montagem
ORDENS = {"Periodo_Conclusao": PERIODOS, "Faixa_Etaria": FAIXAS}


def _freq(df, col):
    tab, ocultas = frequencias(df, col)
    if col in ORDENS:
        tab = tab.set_index(col).reindex([v for v in ORDENS[col] if v in set(tab[col])]).reset_index()
    tab = tab.rename(columns={col: ROTULOS.get(col, col), "Percentual": "Percentual (%)"})
    nota = f"{ocultas} categoria(s) com menos de {MIN_GRUPO} egressos omitida(s)." if ocultas else ""
    return tab, nota


def _cruzada(df, linha):
    cont, pct = cruzada(df, linha, "Curso_de_Graduacao")
    out = pd.DataFrame(index=cont.index)
    for c in cont.columns:
        out[f"{c} (n)"] = cont[c]
        out[f"{c} (%)"] = pct[c]
    return out.reset_index().rename(columns={linha: ROTULOS.get(linha, linha)})


def montar(df: pd.DataFrame, recorte: dict, origem_dados: str = "real",
           explicacoes: dict | None = None) -> Relatorio:
    if len(df) < MIN_TOTAL:
        raise ValueError(f"O recorte tem {len(df)} egressos; o mínimo para exportar é {MIN_TOTAL}.")
    secoes: list[Secao] = []
    n = len(df)
    cc = int((df["Curso_de_Graduacao"] == CURSOS[0]).sum())

    # 1. Resumo
    resumo = pd.DataFrame([
        ("Egressos no recorte", n),
        (CURSOS[0], mascarar(cc)),
        (CURSOS[1], mascarar(n - cc)),
        ("Anos de formado (mediana)", float(df["Tempo_desde_Conclusao"].median())),
        *[(nome, f"{df[ind].mean() * 100:.1f}%") for ind, nome in INDICADORES.items()],
    ], columns=["Indicador", "Valor"])
    secoes.append(Secao("Resumo", tabelas=[Tabela("resumo", "Números principais", resumo)]))

    # 2. Perfil
    perfil = []
    for col, nome in [("Periodo_Conclusao", "periodo"), ("Ano_de_Conclusao", "ano"),
                      ("Faixa_Etaria", "faixa_etaria"), ("Genero", "genero")]:
        tab, nota = _freq(df, col)
        if col == "Ano_de_Conclusao":
            tab = tab.sort_values(ROTULOS[col])
        perfil.append(Tabela(f"perfil_{nome}", f"Egressos por {ROTULOS[col].lower()}", tab, nota))
    secoes.append(Secao("Perfil dos egressos", tabelas=perfil))

    # 3. Inserção profissional
    cargos = sem_informacao(df, "Categoria_Cargo")
    inst = sem_informacao(df, "Tipo_Instituicao")
    ins = []
    tab, nota = _freq(cargos, "Categoria_Cargo")
    ins.append(Tabela("insercao_categoria", "Categoria do cargo atual", tab, nota))
    if cargos["Curso_de_Graduacao"].nunique() == 2:
        r = stats.associacao(cargos, "Curso_de_Graduacao", "Categoria_Cargo")
        ins.append(Tabela("insercao_categoria_por_curso", "Categoria do cargo por curso", _cruzada(cargos, "Categoria_Cargo"),
                          f"{r['teste']}: p = {stats.formatar_p(r['p'])}; {r['medida_efeito']} = "
                          f"{stats.num(r['efeito'], 3)}. {r['aviso']}".strip() if r else ""))
    tab, nota = _freq(inst, "Tipo_Instituicao")
    ins.append(Tabela("insercao_tipo_instituicao", "Tipo de instituição", tab, nota))
    if inst["Curso_de_Graduacao"].nunique() == 2:
        ins.append(Tabela("insercao_tipo_por_curso", "Tipo de instituição por curso", _cruzada(inst, "Tipo_Instituicao")))
    secoes.append(Secao("Inserção profissional",
                        "Registros sem informação de cargo ou vínculo ficam fora destas tabelas.", ins))

    # 4. Indicadores de trajetória
    traj = []
    linhas = []
    for ind, nome in INDICADORES.items():
        t = taxa_por_grupo(df, "Curso_de_Graduacao", ind)
        for _, row in t.iterrows():
            linhas.append({"Indicador": nome, "Curso": row["Curso_de_Graduacao"], "n (grupo)": row["n (grupo)"],
                           "Com evidência": row["Com evidência"], "Percentual (%)": row["Percentual"]})
    traj.append(Tabela("trajetoria_indicadores_por_curso", "Indicadores por curso", pd.DataFrame(linhas)))
    if df["Curso_de_Graduacao"].nunique() == 2:
        brutos = [stats.associacao(df, "Curso_de_Graduacao", ind) for ind in INDICADORES]
        p_holm = stats.holm([r["p"] if r else 1.0 for r in brutos])
        traj.append(Tabela("trajetoria_testes_curso", "Comparação direta entre cursos", pd.DataFrame({
            "Indicador": list(INDICADORES.values()),
            "Phi": [round(r["efeito"], 3) if r else None for r in brutos],
            "p (Fisher)": [stats.formatar_p(r["p"]) if r else "—" for r in brutos],
            "p ajustado (Holm)": [stats.formatar_p(p) for p in p_holm],
        })))
        reg = []
        for ind, nome in INDICADORES.items():
            r = stats.regressao_logistica(df, ind)
            for c in (r or {}).get("coeficientes", []):
                reg.append({"Indicador": nome, "Termo": c["Termo"], "Razão de chances": round(c["Razão de chances"], 2),
                            "IC 95%": f"{c['IC 95% inf.']:.2f} a {c['IC 95% sup.']:.2f}", "p": stats.formatar_p(c["p"])})
        if reg:
            traj.append(Tabela("trajetoria_regressao", "Regressão logística: indicador ~ curso + anos de formado",
                               pd.DataFrame(reg)))
    secoes.append(Secao("Trajetória profissional",
                        "Evidência = o perfil público mostra o fenômeno explicitamente.", traj))

    # 5. Tempo de carreira
    tempo, linhas = [], []
    for ind, nome in INDICADORES.items():
        r = stats.comparar_tempo(df, ind)
        if r and r["n_sim"] >= MIN_GRUPO and r["n_nao"] >= MIN_GRUPO:
            linhas.append({"Indicador": nome, "Mediana com (anos)": r["mediana_sim"], "Mediana sem (anos)": r["mediana_nao"],
                           "Bisserial de postos": round(r["efeito"], 2), "_p": r["p"]})
    if linhas:
        tt = pd.DataFrame(linhas)
        tt["p ajustado (Holm)"] = [stats.formatar_p(p) for p in stats.holm(tt["_p"].tolist())]
        tempo.append(Tabela("tempo_mann_whitney", "Anos de formado, com e sem evidência (Mann-Whitney)", tt.drop(columns="_p")))
    per = []
    for ind, nome in INDICADORES.items():
        t = taxa_por_grupo(df, "Periodo_Conclusao", ind)
        for _, row in t.iterrows():
            per.append({"Indicador": nome, "Período": str(row["Periodo_Conclusao"]), "n (grupo)": row["n (grupo)"],
                        "Percentual (%)": row["Percentual"]})
    tempo.append(Tabela("tempo_por_periodo", "Indicadores por período de conclusão", pd.DataFrame(per)))
    secoes.append(Secao("Tempo de carreira", tabelas=tempo))

    # 6. Relações entre indicadores
    pares = []
    for a, b in combinations(INDICADORES, 2):
        r = stats.associacao(df, a, b)
        if r:
            pares.append({"Par": f"{INDICADORES[a]} × {INDICADORES[b]}",
                          "Com ambos": mascarar(int(((df[a] == 1) & (df[b] == 1)).sum())),
                          "Phi": round(r["efeito"], 3), "_p": r["p"]})
    if pares:
        tp = pd.DataFrame(pares)
        tp["p ajustado (Holm)"] = [stats.formatar_p(p) for p in stats.holm(tp["_p"].tolist())]
        secoes.append(Secao("Relações entre indicadores",
                            tabelas=[Tabela("relacoes_pares", "Associação entre pares", tp.drop(columns="_p"))]))

    # 7. Origem
    orig = []
    for col, nome in [("UF_Nascimento", "uf"), ("Regiao_Nascimento", "regiao")]:
        tab, nota = _freq(df, col)
        orig.append(Tabela(f"origem_{nome}", f"Egressos por {ROTULOS[col].lower()}", tab, nota))
    secoes.append(Secao("Origem geográfica", tabelas=orig))

    # 8. IA explicável (opcional; sempre sobre a base completa)
    if explicacoes:
        xs = []
        for alvo, exp in explicacoes.items():
            imp = exp.importancia.round(2).reset_index().rename(columns={"index": "Fator"})
            auc = "; ".join(f"AUC {m} = {a:.2f} ± {s:.2f}" for m, (a, s) in exp.auc.items())
            xs.append(Tabela(f"xai_importancia_{alvo.replace('Indicador_', '').lower()}",
                             f"Importância dos fatores: {INDICADORES[alvo].lower()} (pp)", imp, auc))
        secoes.append(Secao("IA explicável",
                            "Contribuição média (valores de Shapley) de cada fator, sobre a base completa. "
                            "Associações, não causas.", xs))

    return Relatorio(gerado_em=date.today().isoformat(), recorte=recorte, secoes=secoes, origem_dados=origem_dados)


# --------------------------------------------------------------------------- utilidades
def _nota_privacidade() -> str:
    return (f"Dados agregados. Grupos com menos de {MIN_GRUPO} egressos aparecem como \"<{MIN_GRUPO}\" ou são "
            "omitidos. Pesquisa aprovada pelo CEP (CAAE 87973525.8.0000.5323).")


def _descricao_recorte(rel: Relatorio) -> str:
    return "; ".join(f"{k}: {v}" for k, v in rel.recorte.items()) or "base completa, sem filtros"


def _celula(v) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, (float, np.floating)):
        return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",") if v % 1 else f"{int(v)}"
    return str(v)


def _slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


# --------------------------------------------------------------------------- formatos
def para_json(rel: Relatorio) -> bytes:
    doc = {
        "titulo": TITULO, "gerado_em": rel.gerado_em, "recorte": rel.recorte,
        "dados": "fictícios (demonstração)" if rel.origem_dados == "exemplo" else "base real preliminar",
        "privacidade": _nota_privacidade(),
        "secoes": [{
            "titulo": s.titulo, "texto": s.texto,
            "tabelas": [{"nome": t.nome, "titulo": t.titulo, "nota": t.nota,
                         "colunas": list(t.dados.columns),
                         "linhas": json.loads(t.dados.to_json(orient="records", force_ascii=False))}
                        for t in s.tabelas],
        } for s in rel.secoes],
    }
    return json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")


def para_csv_zip(rel: Relatorio) -> bytes:
    """Um CSV por tabela (separador ; e vírgula decimal, abre direto no Excel) + LEIAME."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        indice = []
        for i, t in enumerate(rel.tabelas(), 1):
            arq = f"{i:02d}_{t.nome}.csv"
            z.writestr(arq, t.dados.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"))
            indice.append(f"{arq}: {t.titulo}" + (f" ({t.nota})" if t.nota else ""))
        leia = [TITULO, f"Gerado em {rel.gerado_em}", f"Recorte: {_descricao_recorte(rel)}",
                _nota_privacidade(), "", "Arquivos:", *indice]
        z.writestr("LEIAME.txt", "\n".join(leia).encode("utf-8-sig"))
    return buf.getvalue()


def _md_tabela(df: pd.DataFrame) -> str:
    cab = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "| " + " | ".join("---" for _ in df.columns) + " |"
    linhas = ["| " + " | ".join(_celula(v).replace("|", "/") for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([cab, sep, *linhas])


def para_markdown(rel: Relatorio) -> bytes:
    partes = [f"# {TITULO}", "", f"Gerado em {rel.gerado_em} · Recorte: {_descricao_recorte(rel)}", "",
              f"> {_nota_privacidade()}", ""]
    for s in rel.secoes:
        partes += [f"## {s.titulo}", ""] + ([s.texto, ""] if s.texto else [])
        for t in s.tabelas:
            partes += [f"### {t.titulo}", "", _md_tabela(t.dados), ""] + ([f"*{t.nota}*", ""] if t.nota else [])
    return "\n".join(partes).encode("utf-8")


def para_html(rel: Relatorio) -> bytes:
    css = """
    :root{--tx:#1F2A2E;--mu:#5C6B67;--li:#DCE4E0;--ac:#1B6E6A;--bg:#fff;--bg2:#F5F8F6}
    @media (prefers-color-scheme:dark){:root{--tx:#E6ECEA;--mu:#9DB0AB;--li:#2C3A37;--ac:#5FB3A8;--bg:#141A19;--bg2:#1C2423}}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);
    font:16px/1.55 "Source Sans 3","Segoe UI",Helvetica,Arial,sans-serif}
    main{max-width:960px;margin:0 auto;padding:48px 24px 64px}
    h1{font:600 2.2rem/1.1 Georgia,"Times New Roman",serif;margin:0 0 .4rem}
    h2{font:500 1.5rem/1.2 Georgia,serif;margin:2.6rem 0 .4rem;padding-top:1rem;border-top:1px solid var(--li)}
    h3{font-size:1rem;margin:1.6rem 0 .5rem}.meta{color:var(--mu);margin:0}
    .priv{background:var(--bg2);border-left:3px solid var(--ac);padding:.6rem .9rem;color:var(--mu);font-size:.9rem;margin:1.2rem 0}
    .rolagem{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}
    th{text-align:left;color:var(--mu);font-weight:600;border-bottom:2px solid var(--li);padding:.4rem .6rem;white-space:nowrap}
    td{border-bottom:1px solid var(--li);padding:.4rem .6rem}.nota{color:var(--mu);font-size:.85rem;margin:.4rem 0 0}
    """
    corpo = [f"<h1>{escape(TITULO)}</h1>",
             f'<p class="meta">Gerado em {rel.gerado_em} · Recorte: {escape(_descricao_recorte(rel))}</p>',
             f'<p class="priv">{escape(_nota_privacidade())}</p>']
    for s in rel.secoes:
        corpo.append(f"<h2>{escape(s.titulo)}</h2>")
        if s.texto:
            corpo.append(f"<p>{escape(s.texto)}</p>")
        for t in s.tabelas:
            cab = "".join(f"<th>{escape(str(c))}</th>" for c in t.dados.columns)
            linhas = "".join("<tr>" + "".join(f"<td>{escape(_celula(v))}</td>" for v in row) + "</tr>"
                             for row in t.dados.itertuples(index=False))
            corpo.append(f"<h3>{escape(t.titulo)}</h3><div class='rolagem'><table><thead><tr>{cab}</tr></thead>"
                         f"<tbody>{linhas}</tbody></table></div>")
            if t.nota:
                corpo.append(f'<p class="nota">{escape(t.nota)}</p>')
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(TITULO)}</title>'
            f"<style>{css}</style></head><body><main>{''.join(corpo)}</main></body></html>")
    return html.encode("utf-8")


_SUBST = {"–": "-", "—": "-", "≥": ">=", "≤": "<=", "→": "->", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "..."}


def _latin1(texto: str) -> str:
    """As fontes padrão do PDF cobrem o português (latin-1); símbolos fora dele são trocados."""
    for a, b in _SUBST.items():
        texto = texto.replace(a, b)
    return texto.encode("latin-1", "replace").decode("latin-1")


def para_pdf(rel: Relatorio) -> bytes:
    from fpdf import FPDF
    from fpdf.fonts import FontFace

    verde = (27, 110, 106)
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=16)
    pdf.set_margins(16, 16, 16)
    pdf.add_page()
    pdf.set_font("Times", "B", 22)
    pdf.set_text_color(31, 42, 46)
    pdf.multi_cell(0, 10, _latin1(TITULO), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(92, 107, 103)
    pdf.multi_cell(0, 5, _latin1(f"Gerado em {rel.gerado_em} | Recorte: {_descricao_recorte(rel)}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _latin1(_nota_privacidade()), new_x="LMARGIN", new_y="NEXT")
    cab = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=verde)
    for s in rel.secoes:
        pdf.ln(4)
        pdf.set_font("Times", "B", 15)
        pdf.set_text_color(31, 42, 46)
        pdf.multi_cell(0, 8, _latin1(s.titulo), new_x="LMARGIN", new_y="NEXT")
        if s.texto:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(92, 107, 103)
            pdf.multi_cell(0, 5, _latin1(s.texto), new_x="LMARGIN", new_y="NEXT")
        for t in s.tabelas:
            pdf.ln(2)
            if pdf.will_page_break(12 + 5 * min(len(t.dados), 4)):
                pdf.add_page()  # evita título de tabela sozinho no pé da página
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(31, 42, 46)
            pdf.multi_cell(0, 6, _latin1(t.titulo), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8)
            with pdf.table(headings_style=cab, line_height=4.6, cell_fill_color=(245, 248, 246),
                           cell_fill_mode="ROWS", borders_layout="HORIZONTAL_LINES") as tabela:
                linha = tabela.row()
                for c in t.dados.columns:
                    linha.cell(_latin1(str(c)))
                for row in t.dados.itertuples(index=False):
                    linha = tabela.row()
                    for v in row:
                        linha.cell(_latin1(_celula(v)))
            if t.nota:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(92, 107, 103)
                pdf.multi_cell(0, 4.5, _latin1(t.nota), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


FORMATOS = {
    "PDF": ("pdf", "application/pdf", para_pdf, "Ler e imprimir"),
    "HTML": ("html", "text/html", para_html, "Abrir no navegador"),
    "Markdown": ("md", "text/markdown", para_markdown, "Documentação"),
    "CSV": ("zip", "application/zip", para_csv_zip, "Planilhas (.zip)"),
    "JSON": ("json", "application/json", para_json, "Sistemas e análises"),
}


def nome_arquivo(rel: Relatorio, ext: str) -> str:
    return f"alem_do_diploma_{_slug(_descricao_recorte(rel))[:40]}_{rel.gerado_em}.{ext}"
