# Alumni View · Laboratório XAI para trajetórias de egressos

Plataforma de pesquisa para comparar modelos e interpretar contribuições de fatores associados a liderança, progressão interna e empreendedorismo. A contribuição central é o **laboratório de inteligência artificial explicável (XAI)**, acompanhado de painéis para contextualizar a base.

**[Abrir a plataforma](https://alumni-view.onrender.com/)** · [Método XAI](docs/METODO_XAI.md) · [Avaliação com coordenadores](avaliacao/COMO_CRIAR_FORMS_V3.md)

## O que o laboratório entrega

1. Compara regressão logística e random forest com uma referência baseada na prevalência.
2. Apresenta AUC ROC, precisão média (AP) e Brier em validação estratificada de cinco partições e três repetições.
3. Calcula contribuições de Shapley fora da amostra por curso, anos desde a conclusão, origem e tipo de instituição.
4. Separa importância global (magnitude) de contribuição média por grupo (direção).
5. Sinaliza fatores sem informação ou sem variação. Contribuição zero nesses casos não demonstra irrelevância.
6. Exporta explicações agregadas, parâmetros, versões, semente e hash da base para rastreabilidade.

Aditividade é verificada numericamente. As explicações descrevem associações aprendidas pelos modelos: não demonstram causas, não validam a coleta e não comprovam a compreensão pelos usuários. A qualidade preditiva deve ser examinada antes das contribuições. Consulte o [protocolo e as referências](docs/METODO_XAI.md).

## Executar

Requisitos para clonar o código: Python 3.12, Node 22 ou superior e Git.

```bash
git clone https://github.com/camillabdt/Alemdodiploma.git
cd Alemdodiploma
bash iniciar.sh
```

Abra http://localhost:8000. O script compila a interface na primeira execução e instala as versões Python verificadas. No Windows, execute `iniciar.bat`. Com Docker: `docker compose up --build`.

## Explorar o XAI

1. Abra a plataforma: a base do estudo é carregada automaticamente, sem envio de CSV pelo participante.
2. No **Laboratório XAI**, escolha o indicador e clique em **Calcular e comparar**.
3. Compare as métricas com a referência; no campo **Modelo**, escolha **Regressão logística** ou **Random Forest** e consulte os fatores e grupos.
4. Registre limitações e exporte a análise XAI. Os relatórios do painel são exportados separadamente.

O laboratório usa a **base completa da sessão**. Os filtros das páginas descritivas não alteram o treinamento. Limites operacionais: 30 a 1.000 registros e pelo menos dez em cada classe; são escolhas desta implementação, não suficiência estatística universal.

## Preparar uma coleta para teste restrito

A preparação da base é responsabilidade da pesquisadora; não é uma etapa do participante da avaliação. O leitor exige indicadores 0/1 e campos padronizados. Para uma coleta com as colunas do formulário original:

```bash
.venv/bin/python -m scripts.preparar_csv_coleta --entrada /caminho/coleta.csv --ano-referencia 2026
```

A preparação preserva o original, retira identificadores diretos e separa casos incompletos em um registro de revisão. “Não informado” não vira zero; anos ausentes não são estimados. Campos não disponíveis recebem **Sem Informação**, e a categoria do cargo é apenas uma sugestão por regras que requer revisão manual. O subconjunto de casos completos é para teste exploratório e pode introduzir viés.

CSV preparado e auditoria ficam fora do repositório público. A base do estudo continua sendo dado individual, mesmo sem nomes. Só a base fictícia integra o Git. No servidor, as sessões ficam em memória e expiram após quatro horas ou reinício. A configuração da base permanece no ambiente do serviço e é recarregada para uma nova sessão.

### Configurar a base automática

O servidor lê `ALUMNI_STUDY_CSV_BASE64` (conteúdo UTF-8 em Base64) ou `ALUMNI_STUDY_CSV_PATH` (caminho privado, por exemplo `/etc/secrets/alumni-study.csv`). `ALUMNI_STUDY_INSTITUTION` define o nome exibido. Sem configuração válida, `/api/study` retorna indisponibilidade e não substitui silenciosamente a base por uma demonstração. Não use variáveis com prefixo `VITE_` para armazenar a base: elas podem integrar o bundle público. A interface e as exportações recebem somente resultados agregados. As APIs de importação e demonstração permanecem para compatibilidade e testes, sem controles na interface da avaliação.

## Organização

| Pasta | Responsabilidade |
|---|---|
| `app/core/xai.py` | Modelos, validação, contribuições e verificações do método |
| `api/` | Importação, sessões, agregação e exportações |
| `frontend/` | Interface React e laboratório XAI |
| `tests/` | Contratos HTTP, propriedades do XAI, privacidade e preparação |
| `avaliacao/` | Instrumento, gerador Google Forms, análise planejada e referências |
| `docs/` | Método, uso, publicação e verificação |
| `pipeline/` e `auditoria/` | Regras e apoio à preparação e auditoria da pesquisa |
| `data/exemplo/` | Demonstração fictícia |

## Verificar e publicar

```bash
.venv/bin/python -m pip install -r requirements-verificado.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
node avaliacao/testar_formulario_v3.cjs
.venv/bin/python scripts/testar_fluxo_http.py
```

O Dockerfile compila diretamente `frontend/` e executa a API; a publicação dispensa pacotes-fonte compactados. O Render usa um único serviço Docker Free. Veja [publicação e limitações](docs/PUBLICACAO.md). Não há autenticação institucional nesta versão; definir acesso e guarda antes da pesquisa com dados reais.

O estudo empírico utiliza registros institucionais e fontes profissionais públicas. A plataforma atual não localiza pessoas nem coleta perfis. Resultados de testes de software e demonstração não equivalem à avaliação científica com coordenadores.
