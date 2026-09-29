"""Livro de códigos em forma de regras.

Implementa, de forma determinística, as regras de categorização do cargo atual
descritas no protocolo de coleta, validação e codificação (Etapa 6).

A classificação automática NÃO substitui a codificação manual. Ela serve para:
1. tornar as regras explícitas e reproduzíveis;
2. apontar registros em que a codificação manual diverge da regra, para revisão;
3. apoiar a codificação de novos egressos em atualizações futuras da base.
"""
from __future__ import annotations

import re
import unicodedata

SEM_INFORMACAO = "Sem Informação"

# Ordem importa: a primeira regra que casar define a categoria.
# Regra de precedência do protocolo: gestão de pessoas vence a área técnica;
# "tech lead" e "líder técnico" permanecem na categoria técnica.
REGRAS: list[tuple[str, list[str]]] = [
    (
        "Gestão/Liderança",
        [
            r"\bgerente\b", r"\bgestor(a)?\b", r"\bcoordenador(a)?\b", r"\bhead\b",
            r"\bdiretor(a)?\b", r"\bc[eimopt]o\b", r"\bcpio\b", r"\btribe\b", r"\bfundador(a)?\b",
            r"\bco-?fundador(a)?\b", r"\bsocio\b", r"\bproprietario\b", r"\bacionista\b",
            r"\bmanager\b", r"\bsupervisor(a)?\b", r"\blider de (?!.*tecnic)",
        ],
    ),
    (
        "Ensino/Pesquisa",
        [
            r"\bprofessor(a)?\b", r"\bpesquisador(a)?\b", r"\bpos-?doc\b", r"\bpostdoc\b",
            r"\bposdoc\b", r"\bdoutorad[oa]\b", r"\bmestrand[oa]\b", r"\bdoutorand[oa]\b",
            r"\bbolsista\b", r"\bdocente\b", r"\bresearch", r"\bphd\b",
        ],
    ),
    (
        "Dados/IA",
        [
            r"\bdados\b", r"\bdata\b", r"\bia\b", r"\bai\b", r"\bmachine learning\b",
            r"\bml\b", r"\bbi\b", r"business intelligence", r"\bvisao computacional\b",
            r"\banalytics\b", r"\bcientista\b",
        ],
    ),
    (
        "Infraestrutura/DevOps/Qualidade",
        [
            r"\bdevops\b", r"\bsre\b", r"\bcloud\b", r"\binfraestrutura\b", r"\bseguranca\b",
            r"\bciberseguranca\b", r"\bcibernetica\b", r"\bdba\b", r"\bbanco de dados\b",
            r"\bqa\b", r"\bquality\b", r"\bqualidade\b", r"\bsql\b", r"\btestes?\b", r"\bplataformas?\b", r"\bredes\b",
        ],
    ),
    (
        "Produto/UX/Agilidade",
        [
            r"\bproduct\b", r"\bproduto\b", r"\bux\b", r"\bui\b", r"\bdesigner\b",
            r"\bscrum\b", r"\bagil", r"\bagile\b", r"\bpo\b",
        ],
    ),
    (
        "Desenvolvimento de Software",
        [
            r"\bdesenvolvedor(a)?\b", r"\bdesevolvedor\b", r"\bdeveloper\b", r"\bprogramador(a)?\b",
            r"\bfull ?stack\b", r"\bback-?end\b", r"\bfront-?end\b", r"\bmobile\b",
            r"\bengenheir[oa] de software", r"\bengenharia de software\b", r"\bsoftware engineer",
            r"\bengenheir[oa] (python|java|flutter|android|ios)\b", r"\btech lead\b",
            r"\blider tecnic[oa]\b", r"\bdesenvolvimento\b", r"\bdesenvovimento\b", r"\bflutter\b", r"\bblockchain\b", r"\barquitet[oa]\b",
            r"\br&d\b", r"\bautomacao\b",
        ],
    ),
    (
        "Área não relacionada à Computação",
        [r"\bengenheir[oa] (civil|mecanic|eletric|agronom|quimic|ambiental|de producao)"],
    ),
    (
        "Outros em Computação/TI",
        [
            r"\bti\b", r"\banalista de sistemas\b", r"\bsuporte\b", r"\bhelpdesk\b", r"\binformatica\b",
            r"\btecnologia\b", r"\bsistemas\b", r"\bcomputacao\b", r"\bsoftware\b",
            r"\btecnico em (informatica|ti)\b", r"\bengenheir[oa]\b",
        ],
    ),
]

SEM_INFO_PADROES = [r"^sem informacao$", r"^nao (esta|está) trabalhando$", r"^$", r"^nan$"]


def normalizar(texto: str | None) -> str:
    """Minúsculas, sem acentos e com espaços simples."""
    if texto is None:
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower().replace("/", " ").replace("|", " ")
    return re.sub(r"\s+", " ", texto).strip()


def classificar_cargo(cargo: str | None) -> str:
    """Aplica as regras do livro de códigos e devolve a categoria do cargo."""
    t = normalizar(cargo)
    if any(re.search(p, t) for p in SEM_INFO_PADROES):
        return SEM_INFORMACAO
    for categoria, padroes in REGRAS:
        if any(re.search(p, t) for p in padroes):
            return categoria
    return "Área não relacionada à Computação"
