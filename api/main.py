"""React + API Python. Iniciar com: python -m uvicorn api.main:app --port 8000."""
from __future__ import annotations

import io
import json
import math
import os
import secrets
import threading
import time
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.core import privacy, relatorio, stats
from app.core.config import DADOS_EXEMPLO, INDICADORES, MIN_GRUPO, MIN_TOTAL, ROOT, ROTULOS
from app.core.data import COLUNAS_ESPERADAS, ler_dados

app = FastAPI(title="Alumni View", version="3.0.0")
# Sem configuração, o uso continua no mesmo endereço da API.
# Em hospedagem separada, liberar somente as origens da interface.
ALLOWED_ORIGINS = [origin.strip().rstrip("/") for origin in
                   os.environ.get("ALUMNI_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
if ALLOWED_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                       allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["Authorization", "Content-Type"],
                       expose_headers=["Content-Disposition"])
MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 10000
SESSION_TTL = 4 * 60 * 60
MAX_SESSIONS = 20
FILTERS = ["Curso_de_Graduacao", "Periodo_Conclusao", "Genero", "Faixa_Etaria", "Categoria_Cargo", "Tipo_Instituicao"]


@dataclass
class Session:
    df: pd.DataFrame
    source: str
    institution: str
    population: dict
    created: float = field(default_factory=time.monotonic)
    xai_cache: dict = field(default_factory=dict)
    xai_lock: threading.Lock = field(default_factory=threading.Lock)


sessions: dict[str, Session] = {}
lock = threading.Lock()


class Query(BaseModel):
    filters: dict[str, list[str]] = Field(default_factory=dict)
    years: list[int] | None = None
    indicators: list[str] = Field(default_factory=list)


def clean(value):
    """Converte tipos numpy e não finitos para JSON estrito."""
    return json.loads(json.dumps(value, default=lambda x: x.item() if hasattr(x, 'item') else str(x)),
                      parse_constant=lambda _: None)


def records(df):
    return json.loads(df.to_json(orient="records", force_ascii=False))


def validate(df):
    if df.empty or len(df) > MAX_ROWS:
        raise ValueError(f"A base deve conter entre 1 e {MAX_ROWS} registros.")
    if df[COLUNAS_ESPERADAS].isna().any().any():
        raise ValueError("Há campos vazios. Preencha os campos obrigatórios; use uma categoria explícita para informação ausente.")
    if (df["Ano_de_Conclusao"] + df["Tempo_desde_Conclusao"]).nunique() != 1:
        raise ValueError("Ano de conclusão + tempo desde a conclusão devem apontar o mesmo ano de referência em toda a base.")
    if df["ID_Egresso"].duplicated().any():
        raise ValueError("ID_Egresso deve ser único por egresso.")
    for column in ["Ano_de_Conclusao", "Tempo_desde_Conclusao"]:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any() or not values.map(lambda x: math.isfinite(x) and x == int(x)).all():
            raise ValueError(f"{column} deve conter números inteiros.")
        if column == "Ano_de_Conclusao" and not values.between(1900, 2100).all():
            raise ValueError("Ano_de_Conclusao deve estar entre 1900 e 2100.")
        if column == "Tempo_desde_Conclusao" and not values.between(0, 150).all():
            raise ValueError("Tempo_desde_Conclusao deve estar entre 0 e 150.")
        df[column] = values.astype(int)
    for column in INDICADORES:
        if not df[column].isin([0, 1]).all():
            raise ValueError(f"{column} deve conter apenas 0 ou 1.")
        df[column] = df[column].astype(int)
    return df


def population_for(df, population):
    if not isinstance(population, dict):
        raise ValueError("Os totais devem ser um objeto JSON com um total por curso.")
    for course, total in population.items():
        if isinstance(total, bool) or not isinstance(total, int) or total <= 0:
            raise ValueError(f"Informe um total inteiro positivo para {course}.")
        if course not in set(df["Curso_de_Graduacao"]):
            raise ValueError(f"O curso {course} não está presente na base.")
        if int((df["Curso_de_Graduacao"] == course).sum()) > total:
            raise ValueError(f"O total institucional de {course} é menor que a base analítica.")
    return population


def remember(session):
    with lock:
        now = time.monotonic()
        for key in list(sessions):
            if now - sessions[key].created > SESSION_TTL:
                del sessions[key]
        if len(sessions) >= MAX_SESSIONS:
            raise HTTPException(503, "Limite de sessões atingido. Tente novamente mais tarde.")
        token = secrets.token_urlsafe(32)
        sessions[token] = session
    options = {column: sorted(str(x) for x in session.df[column].dropna().unique()) for column in FILTERS}
    return {"reference_year": int((session.df.Ano_de_Conclusao + session.df.Tempo_desde_Conclusao).iloc[0]),
            "token": token, "source": session.source, "institution": session.institution,
            "total": len(session.df), "options": options,
            "years": [int(session.df.Ano_de_Conclusao.min()), int(session.df.Ano_de_Conclusao.max())],
            "population": session.population, "minimum": MIN_TOTAL}


def get_session(authorization):
    token = authorization.removeprefix("Bearer ") if authorization else ""
    with lock:
        session = sessions.get(token)
        if session and time.monotonic() - session.created > SESSION_TTL:
            del sessions[token]
            session = None
    if session is None:
        raise HTTPException(401, "Sessão encerrada. Importe o CSV novamente ou abra a demonstração.")
    return session


def filtered(session, query):
    df = session.df
    for column, values in query.filters.items():
        if column not in FILTERS:
            raise HTTPException(422, f"Filtro desconhecido: {column}.")
        if not set(values) <= set(df[column].astype(str).unique()):
            raise HTTPException(422, f"Valor inválido no filtro {column}.")
    for column, values in query.filters.items():
        df = df[df[column].isin(values)]
    if query.years is not None:
        if len(query.years) != 2 or query.years[0] > query.years[1]:
            raise HTTPException(422, "Informe um intervalo de anos válido.")
        df = df[df.Ano_de_Conclusao.between(*query.years)]
    for indicator in query.indicators:
        if indicator not in INDICADORES:
            raise HTTPException(422, "Indicador desconhecido.")
        df = df[df[indicator] == 1]
    return df


def safe_rate(df, indicator):
    positive = int(df[indicator].sum())
    negative = len(df) - positive
    if len(df) < MIN_TOTAL or 0 < min(positive, negative) < MIN_GRUPO:
        return {"value": None, "count": None}
    return {"value": round(positive / len(df) * 100, 1), "count": positive}


def frequency(df, column, exclude=False):
    base = privacy.sem_informacao(df, column) if exclude else df
    tab, omitted = privacy.frequencias(base, column)
    if omitted == 1 and len(tab):
        tab = tab.iloc[1:]
        omitted += 1
    return {"rows": [{"label": str(row[column]), "count": int(row.Quantidade), "value": float(row.Percentual)}
                      for _, row in tab.iterrows()], "omitted": omitted,
            "denominator": len(base)}


def group_rates(df, group, indicator):
    out = []
    for name, part in df.groupby(group, observed=True):
        # A taxa não revela grupos menores que 5 nem células complementares pequenas.
        positive = int(part[indicator].sum())
        negative = len(part) - positive
        if len(part) < MIN_GRUPO or 0 < min(positive, negative) < MIN_GRUPO:
            continue
        out.append({"label": str(name), "value": round(positive / len(part) * 100, 1),
                    "count": positive, "total": len(part)})
    return out


@app.get("/api/health")
def health():
    return {"status": "ok", "application": "Alumni View", "version": app.version}


@app.post("/api/demo")
def demo():
    return remember(Session(validate(ler_dados(DADOS_EXEMPLO)), "exemplo", "Base de demonstração", {}))


@app.delete("/api/session")
def forget(authorization: str | None = Header(default=None)):
    get_session(authorization)
    with lock:
        sessions.pop(authorization.removeprefix("Bearer "), None)
    return {"removed": True}


@app.post("/api/import")
async def import_csv(file: UploadFile = File(...), institution: str = Form("Minha instituição"),
                     population: str = Form("{}")):
    raw = await file.read(MAX_BYTES + 1)
    await file.close()
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "O CSV excede o limite de 5 MB.")
    if len(institution.strip()) > 120:
        raise HTTPException(422, "O nome da instituição deve ter até 120 caracteres.")
    try:
        text = raw.decode("utf-8-sig")
        # Detecta separador; o leitor existente continua responsável pelas colunas proibidas.
        table = pd.read_csv(io.StringIO(text), sep=None, engine="python")
        extras = sorted(set(table.columns) - set(COLUNAS_ESPERADAS))
        if extras:
            raise ValueError(f"Remova as colunas extras antes de importar: {', '.join(extras)}. Use o modelo CSV.")
        df = validate(ler_dados(io.StringIO(table.to_csv(index=False))))
        totals = population_for(df, json.loads(population))
    except (ValueError, UnicodeError, TypeError, pd.errors.ParserError) as error:
        raise HTTPException(422, str(error)) from error
    return remember(Session(df, "importado", institution.strip() or "Minha instituição", totals))


@app.get("/api/template")
def template():
    return Response(pd.DataFrame(columns=COLUNAS_ESPERADAS).to_csv(index=False).encode("utf-8-sig"),
                    media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="modelo-alumni-view.csv"'})


@app.post("/api/dashboard")
def dashboard(query: Query, authorization: str | None = Header(default=None)):
    session = get_session(authorization)
    df = filtered(session, query)
    if len(df) < MIN_TOTAL:
        return {"blocked": True, "minimum": MIN_TOTAL,
                "message": "Recorte insuficiente para exibição. Amplie os filtros para proteger a privacidade."}
    indicators = [{"key": key, "label": label, **safe_rate(df, key),
                   "by_course": group_rates(df, "Curso_de_Graduacao", key),
                   "by_period": group_rates(df, "Periodo_Conclusao", key)} for key, label in INDICADORES.items()]
    time_rows = []
    for indicator, label in INDICADORES.items():
        result = stats.comparar_tempo(df, indicator)
        if result and min(result["n_sim"], result["n_nao"]) >= MIN_GRUPO:
            time_rows.append({"label": label, **result})
    adjusted = stats.holm([r["p"] for r in time_rows])
    for row, p in zip(time_rows, adjusted):
        row["p_holm"] = p
    associations = []
    for a, b in combinations(INDICADORES, 2):
        tab = pd.crosstab(df[a], df[b])
        if ((tab > 0) & (tab < MIN_GRUPO)).any().any():
            continue
        result = stats.associacao(df, a, b)
        if result:
            associations.append({"a": INDICADORES[a], "b": INDICADORES[b], **result})
    for row, p in zip(associations, stats.holm([r["p"] for r in associations])):
        row["p_holm"] = p
    # Cobertura só é exibida na base completa, para não confundir filtro com cobertura.
    coverage = []
    if len(df) == len(session.df):
        for course, total in session.population.items():
            count = int((session.df.Curso_de_Graduacao == course).sum())
            if count >= MIN_GRUPO:
                coverage.append({"label": course, "value": round(count / total * 100, 1), "total": total})
    return clean({"blocked": False, "total": len(df), "base_total": len(session.df),
                  "median_years": float(df.Tempo_desde_Conclusao.median()), "indicators": indicators,
                  "distributions": {column: frequency(df, column, column in ["Categoria_Cargo", "Tipo_Instituicao"])
                                    for column in [*FILTERS, "Ano_de_Conclusao", "UF_Nascimento", "Regiao_Nascimento"]},
                  "time": time_rows, "associations": associations, "coverage": coverage})


@app.post("/api/export/{fmt}")
def export(fmt: str, query: Query, authorization: str | None = Header(default=None)):
    session = get_session(authorization)
    df = filtered(session, query)
    if len(df) < MIN_TOTAL:
        raise HTTPException(422, "Amplie os filtros antes de exportar.")
    formats = {"json": (relatorio.para_json, "application/json", "json"),
               "csv": (relatorio.para_csv_zip, "application/zip", "zip"),
               "html": (relatorio.para_html, "text/html", "html"),
               "md": (relatorio.para_markdown, "text/markdown", "md"),
               "pdf": (relatorio.para_pdf, "application/pdf", "pdf")}
    if fmt not in formats:
        raise HTTPException(404, "Formato não disponível.")
    generate, mime, suffix = formats[fmt]
    # O relatório usa exatamente os agregados já protegidos na API.
    from datetime import date
    payload = dashboard(query, authorization)
    sections = []
    summary = pd.DataFrame([{"Indicador": "Egressos no recorte", "Valor": payload["total"]},
        *[{"Indicador": i["label"], "Valor": "Suprimido" if i["value"] is None else str(i["value"]) + "%"}
          for i in payload["indicators"]]])
    sections.append(relatorio.Secao("Resumo", tabelas=[relatorio.Tabela("resumo", "Indicadores", summary)]))
    for column, distribution in payload["distributions"].items():
        frame = pd.DataFrame(distribution["rows"], columns=["label", "count", "value"]).rename(columns={"label": "Categoria", "count": "Quantidade", "value": "Percentual (%)"})
        sections.append(relatorio.Secao(ROTULOS.get(column, column), tabelas=[relatorio.Tabela(column.lower(), ROTULOS.get(column, column), frame,
            f"Denominador: {distribution['denominator']}. Categorias omitidas: {distribution['omitted']}.")]))
    sections.append(relatorio.Secao("Limites de interpretação", "Dados autodeclarados podem estar incompletos ou desatualizados. Ausência de evidência não é ausência do fenômeno. Associação não demonstra causa. A origem geográfica representa nascimento. O relatório do recorte não inclui resultados XAI; exporte o laboratório separadamente."))
    report = relatorio.Relatorio(date.today().isoformat(), query.model_dump(), sections,
                                 "importada" if session.source == "importado" else session.source)
    return Response(generate(report), media_type=mime,
                    headers={"Content-Disposition": f'attachment; filename="alumni-view-relatorio.{suffix}"'})


@app.post("/api/explanations/{indicator}")
def explanations(indicator: str, authorization: str | None = Header(default=None)):
    from app.core import xai
    session = get_session(authorization)
    if indicator not in xai.ALVOS:
        raise HTTPException(422, "Indicador indisponível para o laboratório XAI.")
    if not session.xai_lock.acquire(blocking=False):
        raise HTTPException(409, "Já há uma análise XAI em andamento nesta sessão.")
    try:
        if indicator not in session.xai_cache:
            try:
                result = xai.explicar_validado(session.df, indicator)
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            result.update({"source": session.source, "institution": session.institution,
                           "target": indicator, "target_label": xai.ALVOS[indicator]})
            session.xai_cache[indicator] = clean(result)
        return session.xai_cache[indicator]
    finally:
        session.xai_lock.release()


@app.get("/api/explanations/{indicator}/export")
def export_explanations(indicator: str, authorization: str | None = Header(default=None)):
    session = get_session(authorization)
    if indicator not in session.xai_cache:
        raise HTTPException(409, "Calcule o indicador antes de exportar.")
    data = json.dumps(session.xai_cache[indicator], ensure_ascii=False, allow_nan=False, indent=2)
    return Response(data, media_type="application/json", headers={
        "Content-Disposition": 'attachment; filename="alumni-view-xai.json"'})


DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
