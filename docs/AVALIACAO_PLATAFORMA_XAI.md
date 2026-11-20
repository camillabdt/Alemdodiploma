# Atualização do protocolo de avaliação para o novo escopo

O instrumento v2 anterior não avaliava compreensão de XAI. Não é suficiente aplicá-lo sem ajustes e concluir que o laboratório foi avaliado. O diagnóstico de acompanhamento e os itens adaptados de utilidade/facilidade continuam pertinentes; acrescentar tarefas do laboratório e perguntas de compreensão após revisão e pré-teste.

## Tarefas padronizadas propostas

O teste com participantes utiliza o CSV disponibilizado pela pesquisadora, na mesma versão para todos. A base fictícia é exclusiva da demonstração e dos testes técnicos. O instrumento atualizado está em `avaliacao/Questionario_Coordenadores_Plataforma_XAI_v3.md`.

1. Confirmar o carregamento da base da pesquisadora e informar total de egressos e cursos.
2. Filtrar Engenharia de Software e conclusão de 2020 a 2025, registrando o total no recorte. Conferir previamente se esses valores existem no CSV definitivo.
3. Identificar a categoria profissional mais frequente no recorte.
4. Consultar o indicador de liderança em Trajetórias e ler sua definição na Metodologia.
5. No Laboratório XAI, calcular liderança e comparar a AUC dos modelos com a referência. AUC 0,5 da referência não significa 50% de acurácia.
6. Selecionar Random forest, identificar o fator com maior importância global e consultar as contribuições de Anos de formado. Distinguir magnitude e direção, sem atribuir causalidade.
7. Baixar o relatório do recorte e a análise XAI; identificar uma limitação. Reconhecer que o laboratório usa a base completa, mesmo após aplicar filtros no painel.

O gabarito deve ser conferido no CSV definitivo antes de recrutar participantes; não há resultados dessa base confirmados nesta entrega. Os resultados dependem da base, do modelo e da versão de bibliotecas. A pesquisadora registra hash, parâmetros e resultados da execução congelada antes de aplicar, sem selecionar o resultado após observar as respostas. Usar o mesmo pacote e base para todos.

## Perguntas abertas de compreensão, autorais

- Um fator com maior importância significa que ele causou o resultado? Explique.
- O que uma contribuição negativa em pontos percentuais descreve?
- O que você concluiria se um modelo tiver desempenho próximo da referência?
- Você usaria essa análise para qual decisão da coordenação? Que informação adicional precisaria?

Rubrica prévia: reconhece limite e interpreta corretamente / parcialmente / interpretação incorreta / não respondeu. Preservar falas antes de codificar. Cruzar compreensão, sucesso de tarefa, ajuda necessária e percepção de utilidade. Um escore TAM favorável não substitui evidência de compreensão. Não chamar esses itens autorais de escala validada. Adaptar o tempo estimado e executar entrevistas cognitivas e piloto antes da aplicação principal.

## O que foi retirado

Não há tarefa de localizar pessoas, configurar chave de API ou coletar vínculo profissional. A contribuição tecnológica agora avaliada é análise e explicabilidade. A origem histórica dos dados continua exigindo rastreabilidade própria, mas não é uma função de busca do produto.
