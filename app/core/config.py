"""Constantes compartilhadas pelo dashboard."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Base real sem identificadores: gerada pelo pipeline e NUNCA versionada
# (em produção, vem dos secrets do Streamlit Cloud).
DADOS_PUBLICOS = ROOT / "data" / "publico" / "dataset_publico.csv"
# Base fictícia de demonstração, versionada no repositório público.
DADOS_EXEMPLO = ROOT / "data" / "exemplo" / "dataset_exemplo.csv"
METADADOS = ROOT / "data" / "publico" / "metadados.json"
GEOJSON_UF = ROOT / "app" / "assets" / "brasil_estados.geojson"

# RNF01 — privacidade por agregação.
# Grupos com menos de MIN_GRUPO egressos não têm contagens nem percentuais exibidos.
# Se o recorte filtrado tiver menos de MIN_TOTAL egressos, nada é exibido.
MIN_GRUPO = 5
MIN_TOTAL = 10

SEM_INFORMACAO = ["Sem Informação", "Sem vínculo informado"]

CURSOS = ["Ciência da Computação", "Engenharia de Software"]
PERIODOS = ["2010–2014", "2015–2019", "2020–2025"]
FAIXAS = ["20–24", "25–29", "30–34", "35–39", "40 ou mais"]

INDICADORES = {
    "Indicador_Lideranca": "Liderança ou gerência",
    "Indicador_Progressao": "Progressão interna",
    "Indicador_Empreendedorismo": "Empreendedorismo",
    "Indicador_Mudanca_Area": "Mudança de área",
}

ROTULOS = {
    "Curso_de_Graduacao": "Curso",
    "Ano_de_Conclusao": "Ano de conclusão",
    "Periodo_Conclusao": "Período de conclusão",
    "Tempo_desde_Conclusao": "Anos desde a conclusão",
    "Genero": "Gênero",
    "Faixa_Etaria": "Faixa etária",
    "UF_Nascimento": "UF de nascimento",
    "Regiao_Nascimento": "Região de nascimento",
    "Categoria_Cargo": "Categoria do cargo atual",
    "Tipo_Instituicao": "Tipo de instituição",
    **INDICADORES,
}

# Paleta: verde-azulado do pampa para CC, ocre de campo para ES.
# O par tem contraste suficiente para daltonismo (deuteranopia e protanopia).
COR_CURSO = {"Ciência da Computação": "#1B6E6A", "Engenharia de Software": "#C8871E"}
COR_PRINCIPAL = "#1B6E6A"
COR_SECUNDARIA = "#C8871E"
COR_NEUTRA = "#8A9A94"
COR_TEXTO = "#1F2A2E"
ESCALA_SEQUENCIAL = ["#EEF4F1", "#B9D5CC", "#6FA89B", "#1B6E6A", "#0E3F3C"]
