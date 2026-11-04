# Verificação da plataforma e do laboratório XAI

A suíte de testes cobre API, preparação de CSV, privacidade, estatística, exportação e propriedades das contribuições. O gerador do formulário tem uma simulação própria de navegação e idempotência. Os comandos estão no README e no workflow de verificação.

## Verificação realizada

- Interface React compilada para produção.
- Teste HTTP com Uvicorn real: importação fictícia, filtros, relatórios PDF/HTML/Markdown/CSV/JSON, cálculo dos dois modelos, aditividade, exportação XAI, encerramento e CORS.
- Publicação inicial no Render: filtros, troca de modelo, cálculo XAI e downloads XAI/PDF conferidos no navegador com base fictícia.
- Propriedades verificadas: solução de Shapley para modelo linear conhecido, eficiência, fator ignorado, aditividade fora da amostra e proteção de grupos pequenos.
- Campos ausentes não são convertidos em respostas negativas na preparação. Fatores ausentes ou constantes recebem aviso próprio no laboratório.
- A implementação anterior de explicação na própria amostra foi removida. A API usa `explicar_validado`, documentado em METODO_XAI.md.

## O que esses testes não demonstram

Os testes não validam a coleta, o codebook manual, a representatividade da amostra ou a compreensão das explicações pelos coordenadores. Nenhuma aplicação com participantes é alegada. Dados e resultados de testes locais com a coleta da pesquisadora são mantidos fora do Git público.

As versões Python diretas usadas no ambiente verificado estão em `requirements-verificado.txt`. Para reprodução científica, congelar também o ambiente efetivo, a base e os parâmetros antes da aplicação principal.
