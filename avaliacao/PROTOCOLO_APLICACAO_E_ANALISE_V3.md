# Protocolo da avaliação — revisão de 13/11/2026

## Instrumento aplicado

A versão atual é representada por `instrumento_v3.json` e `criar_formulario_v3.gs`. O formulário tem 26 perguntas visíveis no total, incluindo quadros com várias afirmações. Universidade/instituição e curso são opcionais; não é solicitado nome. Instituição, curso e comentários podem permitir identificação indireta e exigem revisão antes de divulgar citações.

O diagnóstico aborda atuação, área, experiência, acompanhamento atual, fontes, periodicidade, ferramentas, informações, usos, dificuldades e necessidades. A parte posterior ao uso inclui o registro das sete tarefas, motivos de dificuldade, utilidade (UP1–UP6), facilidade (FUP1–FUP6), visualização de XAI, percepção das explicações (XP1–XP3), intenção de uso (IU1–IU2), contribuição percebida para currículo/PPC, pontos positivos e pontos de melhora.

## Aplicação e desvios

1. Apresentar BIO e TCLE antes do consentimento. Confirmar os campos de guarda, assistência e enquadramento ético antes da aplicação.
2. Congelar versão da plataforma, base do estudo e questionário. A mesma base de 289 registros será carregada automaticamente pelo servidor. Não pedir envio de CSV ao participante nem misturar bases fictícias e empíricas. Registrar o hash da base utilizada.
3. D1 = Não/Não sei informar desvia das perguntas de práticas para dificuldades e necessidades.
4. Após as instruções, quem não experimentou a plataforma responde N1 e encerra. Quem experimentou parcialmente pode avaliar o uso realizado.
5. Somente quem visualizou resultados de XAI responde XP. As outras respostas de X0 seguem diretamente para Uso futuro e sugestões.
6. Registrar ajuda e dificuldades quando houver observação. O quadro de tarefas é autorrelato. A versão atual não coleta os antigos campos T1R–T7R, XC1–XC3 ou XN1; não alegar que tais evidências foram medidas.
7. O tempo de 15 a 20 minutos é estimativa, a conferir no pré-teste. O formulário não cronometra a sessão.

## Tarefas e conferência

- T1: total de egressos e cursos da base carregada.
- T2: Engenharia de Software, conclusão 2020–2025, total do recorte.
- T3: categoria de cargo mais frequente nesse recorte.
- T4: definição de liderança/gerência na Metodologia.
- T5: cálculo de liderança no Laboratório XAI, comparação da AUC com a referência e seleção de Random Forest no campo Modelo.
- T6: somente download do relatório PDF, sem interpretação adicional exigida.
- T7: exportar análise XAI, abrir o JSON baixado e verificar se contém os resultados, sem pedir descrição de uma limitação.

A API foi verificada com a base do estudo: 289 registros, dois cursos e 82 registros de ES em 2020–2025. O JSON de liderança contém `n=289`, 86 positivos, as métricas dos modelos, quatro fatores e verificação de aditividade. Não contém registros individuais. O XAI usa a base completa, mesmo após aplicação de filtros nos painéis descritivos. Esses valores são referência de conferência da equipe, sem serem inseridos como respostas no formulário.

## Escala e análise planejada

Escala: 1 Discordo; 2 Discordo parcialmente; 3 Nem discordo nem concordo; 4 Concordo parcialmente; 5 Concordo. São apenas cinco opções, sem categoria Não pude avaliar. Os quadros são opcionais. Resposta vazia é ausente, nunca zero nem ponto neutro. Não combinar esta versão com respostas de uma versão de sete pontos sem tratar explicitamente a diferença de instrumento.

Diagnóstico: frequências, percentuais, n e denominador por questão. Em múltiplas escolhas, a soma pode superar 100%. Separar ausência, desconhecimento, não resposta e ausência estrutural por desvio. Preservar os originais ao marcar inconsistências em opções exclusivas.

Tarefas: apresentar os quatro estados autorrelatados por tarefa. Sem observação ou produto conferível, não converter autorrelato em acerto objetivamente verificado. Não transformar Não realizei automaticamente em falha. Separar impedimento técnico e dificuldade de interpretação quando isso estiver documentado.

UP e FUP: distribuições, mediana e intervalo interquartil por item. Sínteses exploratórias separadas por dimensão exigem pelo menos cinco dos seis itens válidos; registrar n efetivo. Análise de sensibilidade com seis completos. Não somar dimensões, intenção ou XP em um índice TAM. A adaptação de itens e âncoras não demonstra validação psicométrica ou confirmação causal do TAM.

IU1/IU2: intenção declarada, não adoção real. XP1–XP3: percepção das explicações, analisada por item apenas entre quem visualizou resultados. Não alegar avaliação objetiva de compreensão ou de modelos mentais: os antigos itens XC não estão nesta versão.

PPC1, A1 e A2: codificação temática da contribuição percebida ao currículo/PPC, pontos positivos e pontos de melhora. Uma resposta favorável não demonstra mudança curricular efetivamente realizada. Analisar também D8, o campo de motivos e N1 quando respondidos. Remover elementos identificáveis de citações.

Relatar recrutamento por conveniência, convidados, respondentes, usuários da plataforma e participantes que visualizaram XAI, com perdas e n por análise. Não generalizar para todas as coordenações. Separar pré-teste e estudo principal quando houver mudanças no instrumento.
