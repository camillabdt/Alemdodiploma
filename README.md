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

1. Abra a demonstração ou importe um CSV preparado em **Base de dados**.
2. No **Laboratório XAI**, escolha o indicador e clique em **Calcular e comparar**.
3. Compare as métricas com a referência; escolha o modelo e consulte os fatores e grupos.
4. Registre limitações e exporte a análise XAI. Os relatórios do painel são exportados separadamente.

O laboratório usa a **base completa da sessão**. Os filtros das páginas descritivas não alteram o treinamento. Limites operacionais: 30 a 1.000 registros e pelo menos dez em cada classe; são escolhas desta implementação, não suficiência estatística universal.

## Preparar uma coleta para teste restrito

O modelo CSV disponível na plataforma exige indicadores 0/1 e campos padronizados. Para uma coleta com as colunas do formulário original:

```bash
.venv/bin/python -m scripts.preparar_csv_coleta --entrada /caminho/coleta.csv --ano-referencia 2026
```

A preparação preserva o original, retira identificadores diretos e separa casos incompletos em um registro de revisão. “Não informado” não vira zero; anos ausentes não são estimados. Campos não disponíveis recebem **Sem Informação**, e a categoria do cargo é apenas uma sugestão por regras que requer revisão manual. O subconjunto de casos completos é para teste exploratório e pode introduzir viés.

CSV preparado e auditoria ficam em `data/privado/`, ignorado pelo Git. O CSV importado continua sendo dado individual, mesmo sem nomes. Só a base fictícia integra o repositório. No servidor, as sessões ficam em memória e expiram após quatro horas ou reinício.

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
