# Além do Diploma: painel de acompanhamento de egressos de Computação

Painel interativo sobre as trajetórias profissionais dos egressos de **Ciência da Computação** e **Engenharia de Software** da UNIPAMPA, Campus Alegrete (2010–2025). Desenvolvido como artefato do Trabalho de Conclusão de Curso II em Engenharia de Software.

O painel integra registros institucionais e perfis profissionais públicos e apoia coordenações de curso, NDEs e docentes no acompanhamento de egressos e na reflexão curricular. Todos os resultados são agregados; nenhum egresso é identificável.

> A primeira versão do painel surgiu como projeto em grupo na disciplina Introdução à Ciência de Dados. O que mudou no TCC II está em [`docs/MUDANCAS_TCC2.md`](docs/MUDANCAS_TCC2.md).

## Como executar

Com Docker:

```bash
docker compose up --build
# abrir http://localhost:8501
```

Sem Docker (Python 3.12):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app/app.py
```

Testes:

```bash
pytest
```

## Páginas

| Página | O que mostra | Requisitos |
| --- | --- | --- |
| Visão geral | Tamanho da base, cobertura, distribuição por período, ano, faixa etária e gênero | RF01 |
| Inserção profissional | Categoria do cargo atual e tipo de instituição, total e por curso, com teste de associação | RF03, RF04 |
| Trajetória por curso | Liderança, progressão interna, empreendedorismo e mudança de área por curso; regressão logística controlando o tempo de formado | RF04, RF05 |
| Tempo de carreira | Tempo desde a conclusão com e sem cada indicador; indicadores por período | RF07 |
| Relações entre indicadores | Matriz Phi e coocorrência entre os quatro indicadores | RF05 |
| Origem geográfica | Mapa por UF de nascimento e distribuição por região | RF06 |
| Metodologia | Fontes, cobertura, definições dos indicadores, categorias, privacidade, testes e limitações | RF08, RNF06 |

Filtros na barra lateral (RF02): curso, período e ano de conclusão, gênero, faixa etária, categoria do cargo, tipo de instituição e presença de indicadores. Cada tabela tem download em CSV e cada gráfico, em PNG (RF09).

## Privacidade (RNF01)

- A base do painel (`data/publico/`) não tem nome, cargo por extenso, empresa nem município.
- Grupos com menos de **5** egressos não têm contagens nem percentuais exibidos.
- Recortes com menos de **10** egressos não são exibidos.
- A base completa fica em `data/privado/`, ignorada pelo Git e pelo Docker.

Os limites ficam em `app/core/config.py` (`MIN_GRUPO`, `MIN_TOTAL`).

## Dados: o que fica no repositório e o que não fica

Este repositório é público e **não contém dados de egressos reais**.

| Arquivo | Conteúdo | No Git? |
| --- | --- | --- |
| `data/exemplo/dataset_exemplo.csv` | Base **fictícia**, sorteada, com o mesmo formato da real | Sim |
| `data/publico/metadados.json` | Apenas agregados (totais, cobertura) | Sim |
| `data/publico/dataset_publico.csv` | Base real sem nomes, uma linha por egresso | **Não** |
| `.streamlit/secrets.toml` | A mesma base real, no formato de secrets | **Não** |
| `data/privado/` | Base completa, com cargos e empresas | **Não** |

A base real "sem nomes" continua tendo uma linha por pessoa, e combinações de curso, ano, gênero e faixa etária identificam egressos específicos. Por isso ela nunca vai para o Git.

O painel escolhe a fonte automaticamente: primeiro os *secrets* do Streamlit (produção), depois o arquivo local `data/publico/dataset_publico.csv` e, se nenhum existir, a base fictícia, exibindo um aviso de **dados fictícios**.

## Publicação no Streamlit Community Cloud

1. Rode `python -m pipeline.preparar_dados` localmente; ele gera `.streamlit/secrets.toml` com a base real.
2. Em share.streamlit.io, crie o app a partir deste repositório, branch `main`, arquivo `app/app.py`, Python 3.12.
3. Em **Settings → Secrets** do app, cole o conteúdo inteiro de `.streamlit/secrets.toml` e salve.
4. O app reinicia com os dados reais. Sem o passo 3, ele mostra a base fictícia.

Para atualizar os dados, rode o pipeline de novo e substitua o conteúdo dos secrets. Nenhum commit é necessário.

## Fluxo de dados

```text
data/privado/dataset_gold.csv          base completa (não versionada)
        │
        │  python -m pipeline.preparar_dados
        ▼
data/publico/dataset_publico.csv       base sem identificadores (fora do Git) ──► painel local
.streamlit/secrets.toml                a mesma base, para os secrets do Streamlit Cloud
data/publico/metadados.json            cobertura, ano de referência, contagens
data/privado/divergencias_codebook.csv cargos em que a codificação manual difere da regra
```

Para atualizar a base: substitua `data/privado/dataset_gold.csv`, rode o pipeline e reinicie o painel (RNF04). A mudança do ano de referência do tempo desde a conclusão é feita com `--ano-referencia`.

## Auditoria da base (protocolo de coleta e codificação)

O pacote `auditoria/` aplica o protocolo à base já coletada, respondendo aos itens 2 e 3 do parecer da banca:

```bash
python -m auditoria.auditoria preparar   # planilha com critérios C1–C6, status e evidências
python -m auditoria.auditoria pontuar    # calcula pontos e sugere status (A / AMB)
python -m auditoria.auditoria amostra    # sorteia 72 perfis estratificados para a 2ª codificadora
python -m auditoria.auditoria kappa      # concordância, kappa de Cohen, PABAK e divergências
python -m auditoria.auditoria fluxo --excluidos data/privado/excluidos.csv   # fluxograma 329 → 289
```

O arquivo de excluídos precisa das colunas `Curso_de_Graduacao` e `Codigo_Exclusao` (NL, HOM, AMB, INS ou PRIV).

## Estrutura

```text
app/
├── app.py              entrada: carga, filtros, navegação, trava de privacidade
├── core/               config, dados, filtros, privacidade, estatística, gráficos, exportação
├── views/              uma página por arquivo
└── assets/             geometria das UFs (offline)
pipeline/
├── codebook.py         livro de códigos em forma de regras
├── gerar_exemplo.py    base fictícia para o repositório público
└── preparar_dados.py   base privada → base pública + secrets
auditoria/auditoria.py  ferramentas do protocolo
data/exemplo/           base fictícia (versionada)
data/publico/           metadados (versionados) e base real (NÃO versionada)
data/privado/           base completa (NÃO versionada)
tests/                  testes de dados, privacidade, estatística, regras e páginas
```

## Métodos estatísticos

| Pergunta | Teste | Efeito |
| --- | --- | --- |
| Curso × indicador; indicador × indicador (2×2) | Exato de Fisher | Phi |
| Curso × categoria ou tipo de instituição | Qui-quadrado, com checagem de frequência esperada | V de Cramér |
| Tempo desde a conclusão, com × sem evidência | Mann-Whitney U | Bisserial de postos |
| Indicador ~ curso + tempo desde a conclusão | Regressão logística | Razão de chances (IC 95%) |

Famílias de testes usam correção de Holm; significância de 5%.

## Fontes

- Registros institucionais da UNIPAMPA e perfis públicos do LinkedIn. Pesquisa aprovada pelo CEP (CAAE 87973525.8.0000.5323).
- Geometria das UFs: projeto *click_that_hood* (Code for America), simplificada.
