# Alumni View — React, FastAPI e XAI

Versão de avaliação para o TCC de Camilla Borchhardt. A interface ativa usa React e a API usa Python/FastAPI; o produto não realiza busca de pessoas ou extração de perfis.

## Fonte da versão publicada

O código-fonte completo desta versão está em `alumni-view-source.tar.gz`, incluindo testes, documentação, formulário e interface compilada. O `Dockerfile` da raiz verifica `SHA256SUMS`, extrai esse código e compila a interface antes de iniciar a API. Os diretórios antigos mantidos neste repositório são da versão anterior e não são usados por esse Dockerfile.

Commit local de origem: `327addf86f5cd78869b217e56cca31ffc57e35d0`.

SHA-256 do arquivo-fonte: `d6678b2590b5eef696fb89ef37c95ff9f2a524b0f3871307100e03873c56acd2`.

Para trabalhar no código, extraia o arquivo-fonte em uma pasta nova. O README dentro do pacote contém instruções de execução e desenvolvimento. Os itens de avaliação estão em `avaliacao/`.

## Publicação

`render.yaml` define um único Web Service Docker no plano Free, sem banco ou disco pago. Porta 8000, saúde em `/api/health`, interface e API no mesmo endereço. A criação direta pelo conector usa os mesmos parâmetros e não depende de um Blueprint ativo.

As dependências Python diretas usam as versões verificadas do pacote. O plano gratuito suspende por inatividade; o desempenho do XAI precisa ser conferido no ambiente hospedado antes da avaliação principal.

## Dados e testes

O repositório e o pacote contêm somente a base fictícia de demonstração. O CSV da pesquisa deve ser importado pela interface e não enviado ao GitHub. Os dados importados ficam na memória da sessão; reiniciar o servidor encerra as sessões.

Verificação local: 80 testes Python aprovados, sete dependentes da base real omitidos; importação, filtros, cinco formatos de exportação, dois modelos XAI, exportação XAI e encerramento verificados por HTTP. O gerador do Google Forms passou em simulação; não foi executado na conta Google. Isso não equivale à avaliação com participantes.
