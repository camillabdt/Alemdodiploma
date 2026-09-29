"""Ferramentas para aplicar o protocolo de coleta, validação e codificação à base existente.

Todos os arquivos lidos e gerados ficam em data/privado/ (fora do controle de versão).

Comandos, na ordem de uso:

    python -m auditoria.auditoria preparar
        Cria data/privado/planilha_auditoria.xlsx: a base privada + colunas do protocolo
        (critérios C1–C6, status, evidências dos indicadores, codificadores).
        As colunas de evidência só precisam ser preenchidas nas linhas com "Sim".

    python -m auditoria.auditoria pontuar
        Lê a planilha preenchida, calcula Pontos_Validacao e sugere o Status_Validacao
        (A, AMB) pelas regras do protocolo. Lista os casos que precisam reabrir o perfil.

    python -m auditoria.auditoria amostra [--n 72] [--semente 2026]
        Sorteia a amostra estratificada (curso × período) para a dupla codificação e gera:
          amostra_codificador2.xlsx  para a segunda codificadora (sem os códigos originais)
          amostra_gabarito.csv       códigos originais (NÃO entregar à segunda codificadora)

    python -m auditoria.auditoria kappa
        Compara amostra_gabarito.csv com amostra_codificador2.xlsx preenchida e calcula,
        por variável: concordância percentual, kappa de Cohen e PABAK (binárias).
        Gera divergencias_dupla_codificacao.csv para a arbitragem.

    python -m auditoria.auditoria fluxo --excluidos data/privado/excluidos.csv
        Conta os códigos de exclusão (NL, HOM, AMB, INS, PRIV) e imprime o fluxograma
        329 → 289 em Mermaid, pronto para o texto do TCC.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRIV = ROOT / "data" / "privado"
BASE = PRIV / "dataset_gold.csv"
PLANILHA = PRIV / "planilha_auditoria.xlsx"
AMOSTRA_C2 = PRIV / "amostra_codificador2.xlsx"
GABARITO = PRIV / "amostra_gabarito.csv"
DIVERGENCIAS = PRIV / "divergencias_dupla_codificacao.csv"

CRITERIOS = {"C1_Nome": 0, "C2_UNIPAMPA": 0, "C3_Periodo": 2, "C4_Curso": 2, "C5_Contexto": 1, "C6_Vinculo": 1}
PONTOS_MINIMOS = 3
BINARIAS = {
    "Lideranca_ou_Gerencia": "Evidencia_Lideranca",
    "Progressao_Interna": "Evidencia_Progressao",
    "Empreendeu": "Evidencia_Empreendedorismo",
    "Mudanca_de_Area": "Evidencia_Mudanca_Area",
}
CATEGORICAS = ["Categoria_Cargo", "Tipo_Instituicao"]
VARIAVEIS_CODIFICADAS = CATEGORICAS + list(BINARIAS)
CODIGOS_EXCLUSAO = ["NL", "HOM", "AMB", "INS", "PRIV"]


def _periodo(ano: int) -> str:
    return "2010–2014" if ano <= 2014 else "2015–2019" if ano <= 2019 else "2020–2025"


# --------------------------------------------------------------------------- preparar
def preparar(_args) -> None:
    df = pd.read_csv(BASE)
    extra = {
        "Busca_Tentativa": "", "N_Candidatos": "", **{c: "" for c in CRITERIOS},
        "Pontos_Validacao": "", "Status_Validacao": "", "Data_Coleta": "",
        **{v: "" for v in BINARIAS.values()}, "Codificador_1": "", "Codificador_2": "", "Obs": "",
    }
    for col, valor in extra.items():
        if col not in df.columns:
            df[col] = valor
    # Marca onde a evidência é obrigatória.
    for bin_col, ev_col in BINARIAS.items():
        df.loc[df[bin_col] == "Sim", ev_col] = df.loc[df[bin_col] == "Sim", ev_col].replace("", "PREENCHER")
    if PLANILHA.exists():
        sys.exit(f"{PLANILHA.relative_to(ROOT)} já existe. Apague ou renomeie antes de gerar outra.")
    with pd.ExcelWriter(PLANILHA, engine="openpyxl") as xl:
        df.to_excel(xl, sheet_name="auditoria", index=False)
        pd.DataFrame({
            "Coluna": ["C1_Nome, C2_UNIPAMPA", "C3_Periodo, C4_Curso", "C5_Contexto, C6_Vinculo",
                       "Status_Validacao", "Evidencia_*", "Busca_Tentativa"],
            "Como preencher": [
                "1 se atende, 0 se não (obrigatórios)",
                "1 se atende, 0 se não (valem 2 pontos cada)",
                "1 se atende, 0 se não (valem 1 ponto cada)",
                "Deixe vazio: o comando `pontuar` sugere A ou AMB",
                "Cargo e período que justificam o Sim, ex.: Tech Lead, 2021–atual",
                "B1, B2, B3 ou B4 (se lembrar); vazio se não souber",
            ],
        }).to_excel(xl, sheet_name="instrucoes", index=False)
    n_ev = int(sum((df[b] == "Sim").sum() for b in BINARIAS))
    print(f"Planilha criada: {PLANILHA.relative_to(ROOT)} ({len(df)} linhas).")
    print(f"Evidências a preencher: {n_ev} células marcadas com PREENCHER.")


# --------------------------------------------------------------------------- pontuar
def calcular_pontos(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    crit = out[list(CRITERIOS)].apply(pd.to_numeric, errors="coerce")
    pesos = pd.Series({c: p for c, p in CRITERIOS.items() if p})
    out["Pontos_Validacao"] = crit[pesos.index].fillna(0).mul(pesos).sum(axis=1).astype(int)
    obrig_ok = (crit["C1_Nome"] == 1) & (crit["C2_UNIPAMPA"] == 1)
    preenchido = crit.notna().all(axis=1)
    sugestao = np.where(~preenchido, "", np.where(~obrig_ok, "REJEITAR",
                        np.where(out["Pontos_Validacao"] >= PONTOS_MINIMOS, "A", "AMB")))
    out["Status_Sugerido"] = sugestao
    return out


def pontuar(_args) -> None:
    df = calcular_pontos(pd.read_excel(PLANILHA, sheet_name="auditoria"))
    with pd.ExcelWriter(PLANILHA, engine="openpyxl", mode="a", if_sheet_exists="replace") as xl:
        df.to_excel(xl, sheet_name="auditoria", index=False)
    cont = df["Status_Sugerido"].replace("", "não preenchido").value_counts()
    print("Status sugerido:\n" + cont.to_string())
    rever = df[df["Status_Sugerido"].isin(["AMB", "REJEITAR"])]
    if len(rever):
        print(f"\n{len(rever)} egresso(s) precisam reabrir o perfil ou passar pela segunda revisão:")
        print(", ".join(rever["ID_Egresso"]))
    faltam = int((df[list(BINARIAS.values())] == "PREENCHER").sum().sum())
    print(f"\nEvidências ainda não preenchidas: {faltam}")


# --------------------------------------------------------------------------- amostra
def sortear(df: pd.DataFrame, n: int, semente: int) -> pd.DataFrame:
    """Amostra estratificada proporcional por curso × período (método de maiores restos)."""
    d = df.assign(_estrato=df["Curso_de_Graduacao"] + " | " + df["Ano_de_Conclusao"].map(_periodo))
    tam = d["_estrato"].value_counts()
    cota = tam / tam.sum() * n
    base = np.floor(cota).astype(int)
    resto = (cota - base).sort_values(ascending=False)
    base[resto.index[: n - base.sum()]] += 1
    partes = [d[d["_estrato"] == e].sample(k, random_state=semente) for e, k in base.items() if k]
    return pd.concat(partes).drop(columns="_estrato").sort_values("ID_Egresso")


def amostra(args) -> None:
    df = pd.read_csv(BASE)
    s = sortear(df, args.n, args.semente)
    contexto = ["ID_Egresso", "Curso_de_Graduacao", "Ano_de_Conclusao", "Cargo_Atual", "Local_de_Trabalho"]
    c2 = s[contexto].copy()
    c2["Historico_de_Cargos"] = ""  # preencher a partir da planilha de controle antes de entregar
    for v in VARIAVEIS_CODIFICADAS:
        c2[v] = ""
    c2["Obs_Codificador2"] = ""
    c2.to_excel(AMOSTRA_C2, index=False)
    s[["ID_Egresso", *VARIAVEIS_CODIFICADAS]].to_csv(GABARITO, index=False, encoding="utf-8-sig")
    print(f"Amostra de {len(s)} egressos (semente {args.semente}).")
    print(s.groupby(["Curso_de_Graduacao", s["Ano_de_Conclusao"].map(_periodo)]).size().to_string())
    print(f"\nPara a segunda codificadora: {AMOSTRA_C2.relative_to(ROOT)}")
    print("  -> preencha Historico_de_Cargos (cargos e datas) antes de entregar.")
    print(f"Gabarito (não entregar): {GABARITO.relative_to(ROOT)}")


# --------------------------------------------------------------------------- kappa
def kappa_cohen(a: pd.Series, b: pd.Series) -> float:
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = float((a.values == b.values).mean())
    pe = sum((a == c).sum() / n * (b == c).sum() / n for c in cats)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def concordancia(gab: pd.DataFrame, c2: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    m = gab.merge(c2, on="ID_Egresso", suffixes=("_c1", "_c2"))
    linhas, divs = [], []
    for v in VARIAVEIS_CODIFICADAS:
        a = m[f"{v}_c1"].astype(str).str.strip()
        b = m[f"{v}_c2"].astype(str).str.strip()
        validos = (b != "") & (b != "nan")
        a, b = a[validos], b[validos]
        po = float((a == b).mean()) if len(a) else float("nan")
        linha = {"Variável": v, "n": int(len(a)), "Concordância (%)": round(po * 100, 1),
                 "Kappa de Cohen": round(kappa_cohen(a, b), 3) if len(a) else np.nan}
        if v in BINARIAS:
            linha["PABAK"] = round(2 * po - 1, 3)
        linhas.append(linha)
        dif = m.loc[a.index[a != b], ["ID_Egresso"]].assign(
            Variavel=v, Codificador_1=a[a != b].values, Codificador_2=b[a != b].values,
            Decisao_Final="", Motivo_Divergencia="")
        divs.append(dif)
    return pd.DataFrame(linhas), pd.concat(divs, ignore_index=True)


def kappa(_args) -> None:
    res, div = concordancia(pd.read_csv(GABARITO), pd.read_excel(AMOSTRA_C2))
    print(res.to_string(index=False))
    div.to_csv(DIVERGENCIAS, index=False, encoding="utf-8-sig")
    print(f"\n{len(div)} divergência(s) para arbitragem em {DIVERGENCIAS.relative_to(ROOT)}")
    abaixo = res[res["Kappa de Cohen"] < 0.70]["Variável"].tolist()
    if abaixo:
        print(f"Kappa abaixo de 0,70 em: {', '.join(abaixo)}. Revise as regras dessas variáveis no livro de códigos.")


# --------------------------------------------------------------------------- fluxo
def fluxo(args) -> None:
    exc = pd.read_csv(args.excluidos)
    if not {"Curso_de_Graduacao", "Codigo_Exclusao"} <= set(exc.columns):
        sys.exit("O arquivo precisa das colunas Curso_de_Graduacao e Codigo_Exclusao.")
    invalidos = sorted(set(exc["Codigo_Exclusao"]) - set(CODIGOS_EXCLUSAO))
    if invalidos:
        sys.exit(f"Códigos inválidos: {invalidos}. Use {CODIGOS_EXCLUSAO}.")
    base = pd.read_csv(BASE)
    n_base = base["Curso_de_Graduacao"].value_counts()
    n_exc = exc["Curso_de_Graduacao"].value_counts()
    pop = n_base.add(n_exc, fill_value=0).astype(int)
    c = exc["Codigo_Exclusao"].value_counts().reindex(CODIGOS_EXCLUSAO, fill_value=0)
    cc, es = "Ciência da Computação", "Engenharia de Software"
    print(f"""```mermaid
flowchart TD
    A["População institucional<br/>n = {pop.sum()} (CC {pop.get(cc, 0)} · ES {pop.get(es, 0)})"] --> B{{"Perfil localizado?"}}
    B -- "Não" --> X1["NL: n = {c['NL']}"]
    B -- "Sim" --> C{{"Identidade confirmada?"}}
    C -- "Não" --> X2["HOM: n = {c['HOM']}<br/>AMB: n = {c['AMB']}"]
    C -- "Sim" --> D{{"Informação suficiente?"}}
    D -- "Não" --> X3["INS: n = {c['INS']}<br/>PRIV: n = {c['PRIV']}"]
    D -- "Sim" --> E["Base analítica<br/>n = {n_base.sum()} (CC {n_base.get(cc, 0)} · ES {n_base.get(es, 0)})"]
```""")
    print("\nExclusões por curso e código:")
    print(pd.crosstab(exc["Codigo_Exclusao"], exc["Curso_de_Graduacao"], margins=True, margins_name="Total").to_string())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("preparar").set_defaults(func=preparar)
    sub.add_parser("pontuar").set_defaults(func=pontuar)
    a = sub.add_parser("amostra")
    a.add_argument("--n", type=int, default=72)
    a.add_argument("--semente", type=int, default=2026)
    a.set_defaults(func=amostra)
    sub.add_parser("kappa").set_defaults(func=kappa)
    f = sub.add_parser("fluxo")
    f.add_argument("--excluidos", type=Path, required=True)
    f.set_defaults(func=fluxo)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
