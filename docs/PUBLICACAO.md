# Publicação no Render

A interface React e a API FastAPI são executadas no mesmo Web Service Docker. O Dockerfile usa diretamente o código das pastas do repositório e as versões diretas de `requirements-verificado.txt`; não extrai código de um pacote compactado.

## Configuração

- Serviço: `alumni-view`; plano de execução: **Free**.
- Dockerfile: `./Dockerfile`; contexto: raiz; porta: 8000; um worker.
- Origem: repositório `camillabdt/Alemdodiploma`, branch `main`.
- Deploy automático: desativado para preservar a versão avaliada.
- Endereço: https://alumni-view.onrender.com/
- Verificação da API: `/api/health`. A criação direta pelo conector usa TCP como health check padrão; `render.yaml` define `/api/health` se aplicado como Blueprint.

`render.yaml` descreve um único serviço gratuito. Não provisiona banco ou disco pago. A configuração por Blueprint é uma alternativa à criação direta, não deve criar uma segunda cópia do serviço existente.

## Atualizar a plataforma

1. Execute os testes do README e confira o build React.
2. Envie as mudanças ao repositório e confira o commit de destino.
3. No serviço existente do Render, dispare o deploy manual desse código.
4. Aguarde `live`; confira carregamento, importação autorizada, filtros, cálculo XAI e exportações no endereço publicado.
5. Antes da avaliação principal, registre versão, base, hash, ano de referência e gabarito reservado. Use a mesma configuração para todos os participantes.

## Limites relevantes

O Free tem memória/CPU limitadas e suspensão por inatividade. Os dados importados ficam em memória; reiniciar perde as sessões. O desempenho com o CSV definitivo deve ser conferido antes do estudo. A aplicação não tem autenticação institucional nem persistência compartilhada entre workers.

A guarda, o acesso e o uso de dados reais no servidor devem estar definidos no protocolo. O CSV original, o preparado e os gabaritos da avaliação ficam fora do repositório público.

Documentação técnica: https://render.com/docs/free e https://render.com/docs/docker
