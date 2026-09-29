# O que mudou em relação ao protótipo da disciplina

O protótipo inicial foi desenvolvido em grupo na disciplina Introdução à Ciência de Dados (2026/1), por André Medeiros, Camilla, Erik Ricarde e Matheus Ciocca. Este documento registra o que foi reaproveitado e o que foi desenvolvido no TCC II, para apoiar a declaração de autoria no texto.

## Reaproveitado do protótipo

- A escolha de Streamlit e Plotly como tecnologia.
- A base analítica de 289 egressos (camada gold) e as variáveis derivadas.
- A ideia geral de páginas temáticas com filtros globais na barra lateral.
- A remoção de `Ano_Sabatico` e o tratamento de "Sem Informação" como categoria não substantiva.

## Desenvolvido no TCC II

### Arquitetura e engenharia

- Reestruturação do `app.py` monolítico (644 linhas) em módulos: `core/` (configuração, dados, filtros, privacidade, estatística, gráficos, exportação) e `views/` (uma página por arquivo).
- Funções de dados, privacidade e estatística sem dependência do Streamlit, para permitir testes unitários.
- Suíte de testes cobrindo base pública, privacidade, estatística, livro de códigos, pipeline, auditoria e carregamento de todas as páginas.
- Imagem Docker contendo apenas código e base pública.

### Dados e reprodutibilidade

- Pipeline real de preparação (`pipeline/preparar_dados.py`), gerando a base pública e os metadados a partir da base privada. No protótipo, as camadas bronze, silver e gold eram arquivos idênticos.
- Livro de códigos implementado como regras (`pipeline/codebook.py`), com relatório de divergências entre regra e codificação manual.
- Períodos de conclusão alinhados ao texto do TCC (2010–2014, 2015–2019, 2020–2025), no lugar de 2010–2017 / 2018–2025.
- Metadados de cobertura (base analítica × população institucional).

### Privacidade (RNF01)

- Separação entre base privada (não versionada) e base pública sem cargo por extenso, empresa ou município.
- Supressão de grupos com menos de 5 egressos em frequências, tabelas cruzadas e taxas.
- Bloqueio de recortes com menos de 10 egressos, impedindo que filtros combinados isolem uma pessoa.
- Recusa automática de bases públicas que contenham colunas identificáveis.

### Requisitos do TCC I implementados

- RF02: filtros por categoria do cargo, tipo de instituição e indicadores.
- RF06: mapa por UF de nascimento, desenhado sem dependência de internet, e distribuição por região.
- RF08/RNF06: página de metodologia com definições dos indicadores, categorias, testes e limitações.
- RF09: download de tabelas em CSV e gráficos em PNG.

### Estatística (item 4 do parecer)

- Exato de Fisher nas tabelas 2×2, em vez de qui-quadrado.
- Verificação do pressuposto de frequência esperada no qui-quadrado, com aviso na interface.
- Mann-Whitney U para o tempo desde a conclusão, com bisserial de postos como efeito.
- Correção de Holm nas famílias de testes.
- Regressão logística controlando o tempo desde a conclusão, que separa o efeito do curso do tempo de formado.

### Comunicação

- Textos de leitura calculados a partir dos dados filtrados, substituindo conclusões e hipóteses fixas que ficavam incorretas quando o usuário aplicava filtros.
- Tema visual próprio, com cor fixa por curso e paleta segura para daltonismo.

### Auditoria (itens 2 e 3 do parecer)

- `auditoria/auditoria.py`: planilha do protocolo, pontuação de validação, amostra estratificada para dupla codificação, kappa de Cohen com PABAK e fluxograma de exclusões.
