# Protocolo de aplicação e análise - v3.0

Versão para apreciação e pré-teste. Este protocolo não afirma que houve aplicação, validação psicométrica ou avaliação com coordenadores. O instrumento do participante está em arquivo separado; não apresentar o gabarito antes ou durante a sessão principal.

## Questões de avaliação

- QA1: Quais práticas, dificuldades e necessidades caracterizam o acompanhamento de egressos no contexto dos participantes? D1-D8.
- QA2: Os participantes conseguem explorar os indicadores e obter os resultados das tarefas? UT, T1R-T7R e observação quando disponível.
- QA3: Como percebem utilidade, facilidade de uso e possibilidade de uso da plataforma? UP, FUP, IU e A1-A3.
- QA4: Como percebem e interpretam as explicações dos modelos? X0, XP1-XP3, XC1-XC3 e tarefas T5-T6.

Satisfação, compreensão demonstrada, desempenho do modelo e sucesso nas tarefas são evidências distintas. Não somar tudo em um índice de validação do XAI. Nenhuma dessas medidas, isoladamente, demonstra adoção institucional ou melhoria de decisões curriculares.

## Público e recrutamento

Coordenações atuais ou anteriores, vice-coordenações, NDE/colegiado e pessoas com experiência pertinente em gestão acadêmica. O convite por conveniência é inicialmente dirigido à UFU e à UNIPAMPA, com registro de atuação. Manter Outra atuação em P1, conforme o texto enviado; descrever os respondentes dessa categoria e não presumir que todos sejam coordenadores atuais.

Registrar convidados, elegíveis segundo o protocolo definitivo, participantes do piloto, respondentes principais, uso da plataforma e visualização do XAI. Não excluir silenciosamente respostas de Outra atuação ou participantes que tiveram dificuldades. A amostra é de conveniência e não permite generalizar para todas as instituições. Evitar comparações inferenciais entre subgrupos pequenos.

## Desenvolvimento e pré-teste

O diagnóstico é uma operacionalização autoral com apoio em Leopoldo (2019) e Simon e Pacheco (2017). UP/FUP usam adaptação de Davis (1989). O planejamento do painel considera Kaliisa et al. (2023), com adaptação do contexto docente. XP/XC são itens autorais, orientados pela distinção entre satisfação e modelos mentais de Hoffman et al. (2023). Artino et al. (2014) orienta a revisão de pertinência e compreensão.

Proposta de viabilidade: apreciação de duas pessoas, cobrindo acompanhamento de egressos e avaliação de sistemas/XAI; entrevistas cognitivas com dois representantes do público; piloto técnico com duas ou três pessoas. Esses números são escolhas operacionais do TCC, não recomendações universais de validação. Podem ser ajustados e devem ser relatados como efetivamente realizados. Antes do estudo principal, revisar termos como AUC ROC, referência, contribuição e pontos percentuais sem exigir formação prévia em aprendizado de máquina.

Pedir que as pessoas expliquem o que entenderam da pergunta, como localizaram a informação e por que escolheram uma resposta. Registrar revisões por item, versão, motivo e decisão. Conferir carga de leitura e duração real; o intervalo de 30-40 minutos é apenas estimativa inicial. Se o piloto indicar fadiga, revisar o desenho antes de aplicar, sem cortar itens de uma dimensão com base em resultados favoráveis.

## Acesso e sessão

1. A pesquisadora disponibiliza uma instância acessível da plataforma React v3 ou prepara a execução local no computador da sessão. Um link localhost não dá acesso remoto ao computador da pesquisadora. A disponibilização da ferramenta deve ocorrer antes de enviar o formulário para avaliação.
2. Congelar pacote, dependências, base fornecida pela pesquisadora, versão do formulário e instruções. Todos os participantes devem usar a mesma versão do CSV da pesquisadora; registrar seu hash e ano de referência. Não misturar bases distintas na aplicação principal.
3. Conferir antes da sessão que o cálculo de liderança no laboratório retorna resultados. Se a infraestrutura impedir o uso, registrar como impedimento técnico, sem atribuir ao participante falta de compreensão.
4. Aplicar diagnóstico antes da ferramenta. Oferecer instruções de navegação, sem antecipar respostas do gabarito. Permitir as informações de ajuda disponíveis na plataforma; isso integra a avaliação de uso do produto.
5. Solicitar T1-T7 na ordem. Registrar ajuda e pausas. Proposta de limite: três minutos de tempo ativo por tarefa; a espera computacional do XAI é registrada separadamente. O limite é operacional e deve ser conferido no piloto.
6. Aplicar UP/FUP após uso parcial ou completo. X0 controla o acesso às questões de XAI: apenas quem efetivamente visualizou resultados responde XP/XC. Quem não usou a plataforma responde N1 e encerra. Quem não visualizou XAI responde XN1, depois IU/A.
7. Conferir condições de participação, acesso, guarda, retenção e contato antes do recrutamento principal, conforme o procedimento institucional aplicável. Não registrar nomes de egressos ou enviar dados identificáveis em relatórios de teste.

As tarefas podem ser acompanhadas, sem gravação obrigatória. Não é solicitado código de sessão ao participante. Sem observação, T1R-T7R são as evidências verificáveis enviadas pelo participante; UT continua sendo autorrelato. Se não houver resposta nem observação, não classificar a tarefa como confirmadamente correta.

## Gabarito reservado e rubrica das tarefas

Os resultados numéricos devem ser extraídos do CSV escolhido e da execução congelada, usando GABARITO_BASE_AVALIACAO.md. Não há total numérico confirmado nesta revisão do formulário.

T1: conferir total de registros e cursos na base importada; apenas um dos números correto é parcial.

T2: conferir o filtro Engenharia de Software, 2020-2025, e o total efetivamente retornado. Validar previamente a existência dessas categorias.

T3: conferir a categoria mais frequente no recorte de T2; o nome basta.

T4: reconhecer função explícita de liderança/gestão conforme a Metodologia; senioridade isolada não basta.

T5: comparar a AUC dos modelos com a referência da execução na base escolhida, sem interpretá-la como acurácia e sem pressupor que os modelos terão desempenho superior à referência.

T6: conferir fator mais importante e sinal da contribuição de um grupo de Anos de formado usando a exportação XAI da base escolhida. Não exigir que a resposta siga a intuição de que tempo maior sempre aumenta a estimativa.

T7: conferir os dois downloads e uma limitação pertinente. O relatório utiliza o recorte; o laboratório usa a base completa.

Estados por tarefa: correta sem ajuda / correta com ajuda / parcial / incorreta / não realizada / impedimento técnico / sem evidência suficiente para conferir. Preservar UT como informado, mesmo se divergir da conferência da pesquisadora. Ajuda de instalação e acesso é distinta de ajuda de interpretação; registrar o tipo.

## Rubrica reservada de compreensão do XAI

XC1: adequada quando reconhece que importância no modelo não permite concluir causalidade; parcial quando manifesta cautela sem explicar a diferença; inadequada quando atribui causa a partir da importância; sem resposta quando ausente ou explicitamente não interpretável.

XC2: adequada quando descreve uma contribuição que reduz a probabilidade estimada pelo modelo em relação à referência do procedimento, em média no grupo; parcial quando apenas indica redução da estimativa sem o referencial; inadequada quando interpreta como número negativo de pessoas, deterioração da carreira ou efeito causal demonstrado; sem resposta quando ausente. Aceitar linguagem cotidiana que expresse o sentido, sem exigir a fórmula de Shapley.

XC3: adequada quando reconhece que explicações de um modelo com discriminação próxima à referência oferecem evidência limitada para uso e exigem cautela, revisão dos dados/modelo ou validação adicional; parcial quando só afirma conferir melhor, sem ligar o cuidado ao desempenho; inadequada quando diz que o modelo é confiável apenas porque possui explicações; sem resposta quando ausente. Não exigir um limiar universal de AUC.

Essas rubricas são autorais e específicas desta avaliação. Idealmente, uma segunda pessoa codifica as respostas de compreensão de modo independente; registrar divergências e arbitragem, se essa etapa for executada. Se houver apenas uma codificadora, relatar a limitação. Não afirmar que três perguntas capturam integralmente o modelo mental do participante.

## Análise planejada

Diagnóstico: frequências e percentuais por pergunta, com n e denominador. Em múltiplas escolhas, a soma pode exceder 100%. Separar ausência real, desconhecimento e não resposta. Manter a resposta original quando houver combinação contraditória de opção exclusiva; marcar a inconsistência e documentar sua utilização. D2-D6 ausentes por desvio de D1 são ausências estruturais, não falta de resposta.

Tarefas: por T1-T7, relatar todos os estados e a quantidade de resultados que puderam ser conferidos. Taxa de sucesso autônomo = corretas sem ajuda / tarefas efetivamente tentadas e conferíveis; apresentar também esse resultado sobre todos os participantes que usaram a plataforma, identificando não tentativa e ausência de evidência. Correta com ajuda e parcial ficam separadas. Não converter impedimento técnico em erro de interpretação nem omitir a quantidade de não tentativas. O formulário não cronometra o uso automaticamente.

UP/FUP: distribuição, mediana e intervalo interquartil por item. Não pude avaliar e vazio não são zero nem neutro. Sínteses exploratórias separadas por dimensão exigem pelo menos cinco dos seis itens válidos por pessoa, com n efetivo; análise de sensibilidade apenas com seis completos. Não somar UP, FUP, IU ou XP. Não alegar confirmação causal do TAM ou validação psicométrica ampla. Estatísticas de consistência interna, se cabíveis pela quantidade/variação das respostas, não substituem as demais evidências de validade.

IU1/IU2: distribuições separadas; intenção declarada não comprova adoção real. Os itens são autorais, não pertencem às duas escalas finais de Davis utilizadas como referência.

XP1-XP3: analisar individualmente, apenas em quem visualizou resultados. Não criar escore de satisfação validado ou reutilizar limiares de outra escala. O ponto neutro não equivale a não ter usado o laboratório.

XC1-XC3: relatar categorias da rubrica e n elegível em cada questão. Registrar não resposta entre quem visualizou e distinguir das ausências por desvio. Não misturar a compreensão do XAI com UP/FUP em um índice geral. Cruzar descritivamente XP com XC para localizar casos de percepção favorável e interpretação incorreta; não inferir causalidade.

A1-A3, D8, N1 e XN1: codificação temática com registro de categorias iniciais e emergentes. Exemplos iniciais: utilidade, navegação, interpretação, dados, atualização, importação, infraestrutura, tempo de cálculo e privacidade. Preservar casos negativos. Retirar identificação indireta antes de citar comentários e evitar combinações de perfil que individualizem respondentes.

Relato da amostra: convidados, respondentes, pessoas que usaram a plataforma e pessoas que visualizaram XAI, com perdas e n por análise. O piloto não deve ser agregado ao estudo principal se o instrumento ou a versão da ferramenta mudar.

## Revisão visual e periodicidade

A pergunta D3 passa a usar atualização a cada ano, a cada três anos, a cada cinco anos, sem periodicidade definida, não sei informar e outra periodicidade em campo livre. Não há periodicidade definida é diferente de desconhecimento. Essas categorias foram definidas na revisão da pesquisadora, não prescritas por uma escala da literatura. O texto de Outro é preservado e posteriormente codificado com justificativa, sem converter automaticamente uma resposta livre em categoria predefinida.

A apresentação das escalas foi agrupada em quatro matrizes, mantendo as 12 afirmações UP/FUP, três XP e duas IU. São mantidas as mesmas regras de análise por item e dimensão; não somar os quatro quadros. O arquivo mapa_itens_forms.csv liga cada linha dos quadros aos códigos de pesquisa. Os códigos deixaram de aparecer nos títulos voltados ao participante. O piloto deve verificar o formato das matrizes e seu funcionamento em telas menores. A estimativa de duração não foi reduzida sem evidência de piloto.

A revisão 3.2 remove o campo de código da sessão. D4 passa a identificar ferramentas de acompanhamento (Google Forms, Microsoft Forms, LimeSurvey, sistema/portal institucional ou outra), sem perguntar como os dados são organizados. A alternativa livre é preservada literalmente e codificada com justificativa.

## Base da avaliação - revisão 3.3

A pesquisadora disponibilizará seu CSV preparado para a plataforma. O participante utiliza essa base, importando-a caso ainda não esteja carregada. O conjunto fictício e seus gabaritos foram retirados do pacote de avaliação. O formulário não possui campo de código de sessão. Os resultados esperados só serão preenchidos após conferência do CSV definitivo; nenhum número da demonstração constitui gabarito deste teste.
