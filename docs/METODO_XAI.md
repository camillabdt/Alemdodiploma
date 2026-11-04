# Protocolo XAI da versão 3

## Pergunta de análise

Quais fatores contribuem para as estimativas dos modelos de associação com liderança, progressão interna ou empreendedorismo, e como essas contribuições variam entre os dois modelos? O alvo é evidência observada na base. Não se estima efeito causal nem se aconselha o egresso individualmente.

## Validação e referência

Usar validação cruzada estratificada com cinco partições e três repetições. Avaliar regressão logística, random forest e um classificador de referência que sempre retorna a prevalência de treino. Usar AUC ROC, average precision (AP) e Brier para comparar discriminação e erro probabilístico. A AUC não é acurácia; AP tem como referência a prevalência; menor Brier é melhor. O desvio entre partições descreve variabilidade do procedimento, não confiança estatística com observações independentes.

O vocabulário de curso, UF e instituição e o agrupamento de categorias com menos de cinco registros são construídos no treino. No teste, categorias não conhecidas ficam no grupo residual ou na representação sem indicador conhecido. A padronização é ajustada no treino, dentro do pipeline da regressão. Esses cuidados seguem a documentação de prevenção de vazamento do scikit-learn.

## Explicações fora da amostra

Na primeira repetição, cada registro é explicado uma vez pelo modelo treinado nos outros quatro blocos. Cada fator é um jogador do jogo de Shapley: todas as colunas dummy de um fator categórico mudam juntas, preservando sua representação interna.

Para cada registro de teste x e conjunto S de fatores, v(S) é a média das probabilidades ao combinar x nos fatores presentes com linhas de referência do treino nos demais. Usamos até 24 referências de treino por partição, selecionadas com semente fixada. Enumeramos as 16 coalizões de quatro fatores; portanto o cálculo é exato para esse jogo e esse fundo finito, não para uma distribuição populacional desconhecida. Não usamos aproximação TreeSHAP nem a biblioteca shap.

A soma das contribuições mais a média-base da partição deve reproduzir a probabilidade do modelo; a implementação exige erro máximo inferior a 1e-7. A importância global é a média do valor absoluto das contribuições fora da amostra, em pontos percentuais. A contribuição média por grupo preserva direção e pode cancelar sinais opostos. A exportação também registra a variação da importância entre as cinco partições, como descrição de estabilidade, sem chamar esse desvio de intervalo de confiança.

Como cada partição tem seu modelo e sua referência, a agregação descreve o procedimento com validação cruzada. Não equivale à explicação de um único modelo final ajustado a toda a base. Fatores correlacionados podem gerar combinações pouco plausíveis no jogo interventional: declarar essa limitação. Valores maiores não comprovam importância causal.

## Escopo e interpretação

O módulo sempre utiliza a base completa da sessão. Filtrar um alvo antes de treinar pode eliminar uma classe e produzir estimativas sem sentido; por isso os filtros analíticos não se aplicam aqui. Novo CSV cria nova sessão, sem reutilizar cache de outra instituição. O resultado exportado registra versão do procedimento, alvo, fonte fictícia/importada, biblioteca, semente, limites e SHA-256 da base.

Mudança de área não é modelada nesta versão, por sua baixa ocorrência no estudo original. As regras de liderança e empreendedorismo podem compartilhar definições, e dados de instituição atual podem ser contemporâneos ao alvo; não usar o modelo como prognóstico temporal. Presença digital, ausência de informação e codificação condicionam tanto desempenho quanto explicações.

Fatores sem informação ou sem variação são sinalizados no laboratório e na exportação. Uma contribuição zero de um campo ausente ou constante não demonstra irrelevância desse fator na população. Quando a preparação seleciona casos completos, documentar as perdas e o possível viés antes de interpretar métricas ou contribuições.

O teste de aditividade e os testes automatizados verificam implementação. Não demonstram a validade da base real nem a compreensão pelos coordenadores; ambas exigem avaliação empírica.

## Referências

LUNDBERG, S. M.; LEE, S.-I. A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems 30, 2017. https://papers.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html

SCIKIT-LEARN. Common pitfalls and recommended practices. https://scikit-learn.org/stable/common_pitfalls.html

SCIKIT-LEARN. Metrics and scoring: quantifying the quality of predictions. https://scikit-learn.org/stable/modules/model_evaluation.html
