// Questionário limpo v3.3. Cria um NOVO rascunho, sem publicar ou alterar anteriores.
const URL_FERRAMENTA = "";
const INFORMACOES_GUARDA = ""; // Completar conforme protocolo antes da aplicação.
const SPEC = {
  "version": "3.3",
  "title": "Acompanhamento de egressos e avaliação da Alumni View",
  "items": [
    {
      "id": "P1",
      "title": "Qual é sua atuação em relação à coordenação de curso?",
      "kind": "choice",
      "options": [
        "Coordenador(a) atual",
        "Vice-coordenador(a) atual",
        "Já atuei na coordenação",
        "Integrante de NDE ou colegiado",
        "Outra atuação"
      ],
      "required": true,
      "section": "perfil",
      "help": "",
      "source": "Autoral: caracterização ou operação do estudo",
      "display_title": "Qual é a sua atuação na gestão do curso?"
    },
    {
      "id": "P2",
      "title": "Em que grande área se situa o curso com o qual você tem maior vínculo?",
      "kind": "choice",
      "options": [
        "Ciências Exatas e da Terra",
        "Engenharias",
        "Ciências Biológicas",
        "Ciências da Saúde",
        "Ciências Agrárias",
        "Ciências Sociais Aplicadas",
        "Ciências Humanas",
        "Linguística, Letras e Artes",
        "Multidisciplinar",
        "Prefiro não informar"
      ],
      "required": false,
      "section": "perfil",
      "help": "",
      "source": "Autoral: caracterização ou operação do estudo",
      "display_title": "Qual é a grande área do curso?"
    },
    {
      "id": "P3",
      "title": "Há quanto tempo você atua ou atuou na coordenação ou gestão acadêmica de curso?",
      "kind": "choice",
      "options": [
        "Menos de 1 ano",
        "De 1 a menos de 3 anos",
        "De 3 a menos de 5 anos",
        "5 anos ou mais",
        "Não se aplica",
        "Prefiro não informar"
      ],
      "required": false,
      "section": "perfil",
      "help": "",
      "source": "Autoral: caracterização ou operação do estudo",
      "display_title": "Há quanto tempo atua ou atuou na gestão de curso?"
    },
    {
      "id": "D1",
      "title": "Como ocorre o acompanhamento dos egressos do curso atualmente?",
      "kind": "choice",
      "options": [
        "Sim, com rotina definida",
        "Sim, de forma eventual",
        "Não",
        "Não sei informar"
      ],
      "required": true,
      "section": "situacao",
      "help": "",
      "source": "Autoral contextual: Simon e Pacheco (2017), Leopoldo (2019) e requisitos do estudo; não é escala validada desses trabalhos",
      "display_title": "O curso acompanha seus egressos?"
    },
    {
      "id": "D2",
      "title": "Quais fontes são utilizadas nesse acompanhamento?",
      "kind": "checks",
      "options": [
        "Questionários para egressos",
        "Registros institucionais",
        "LinkedIn ou outras plataformas profissionais",
        "Contato direto com egressos",
        "Eventos e redes de ex-alunos",
        "Outras fontes",
        "Nenhuma fonte definida",
        "Não sei informar"
      ],
      "required": false,
      "section": "praticas",
      "help": "Marque todas as opções aplicáveis. Use uma opção de ausência ou desconhecimento sozinha.",
      "source": "Autoral com fundamentação temática em Leopoldo (2019), Quadro 8 e Apêndice A, e Simon e Pacheco (2017); sem reprodução literal de itens",
      "display_title": "Quais fontes são utilizadas?"
    },
    {
      "id": "D3",
      "title": "Com que periodicidade as informações sobre os egressos são atualizadas?",
      "kind": "choice",
      "options": [
        "A cada ano",
        "A cada três anos",
        "A cada cinco anos",
        "Sem periodicidade definida",
        "Não sei informar",
        "Outra periodicidade"
      ],
      "required": false,
      "section": "praticas",
      "help": "",
      "source": "Autoral: intervalos de um, três e cinco anos, ausência de periodicidade, desconhecimento e outro intervalo, definidos após revisão da pesquisadora.",
      "display_title": "Com que periodicidade as informações sobre os egressos são atualizadas?",
      "native_other": true
    },
    {
      "id": "D4",
      "title": "Quais ferramentas o curso utiliza no acompanhamento de egressos?",
      "kind": "checks",
      "options": [
        "Google Forms",
        "Microsoft Forms",
        "LimeSurvey",
        "Sistema ou portal institucional de egressos",
        "Não utiliza ferramentas específicas",
        "Não sei informar",
        "Outra ferramenta"
      ],
      "required": false,
      "section": "praticas",
      "help": "Marque todas as opções aplicáveis. Use uma opção de ausência ou desconhecimento sozinha.",
      "source": "Autoral: ferramentas de acompanhamento, com fundamentação temática em Leopoldo (2019) e Simon e Pacheco (2017). Exemplos de produtos definidos para o diagnóstico do contexto; sem escala validada.",
      "display_title": "Quais ferramentas o curso utiliza no acompanhamento de egressos?",
      "native_other": true
    },
    {
      "id": "D5",
      "title": "Quais informações estão disponíveis sobre os egressos?",
      "kind": "checks",
      "options": [
        "Situação de trabalho",
        "Cargo e organização de atuação",
        "Área de atuação",
        "Continuidade dos estudos",
        "Localização profissional",
        "Mudanças e progressão na carreira",
        "Percepções sobre a formação recebida",
        "Outras informações",
        "Não há informações disponíveis",
        "Não sei informar"
      ],
      "required": false,
      "section": "praticas",
      "help": "Marque todas as opções aplicáveis. Use uma opção de ausência ou desconhecimento sozinha.",
      "source": "Autoral contextual: Simon e Pacheco (2017), Leopoldo (2019) e requisitos do estudo; não é escala validada desses trabalhos",
      "display_title": "Quais informações sobre os egressos estão disponíveis?"
    },
    {
      "id": "D6",
      "title": "Para quais atividades as informações são efetivamente utilizadas?",
      "kind": "checks",
      "options": [
        "Revisão de currículo ou PPC",
        "Avaliação institucional ou do curso",
        "Planejamento de ações para estudantes",
        "Aproximação com egressos e organizações",
        "Elaboração de relatórios",
        "Outras atividades",
        "Ainda não são utilizadas",
        "Não sei informar"
      ],
      "required": false,
      "section": "praticas",
      "help": "Marque todas as opções aplicáveis. Use uma opção de ausência ou desconhecimento sozinha.",
      "source": "Autoral com fundamentação temática em Leopoldo (2019), Quadro 8 e Apêndice A, e Simon e Pacheco (2017); sem reprodução literal de itens",
      "display_title": "Para que essas informações são utilizadas?"
    },
    {
      "id": "D7",
      "title": "Quais dificuldades existem para acompanhar os egressos?",
      "kind": "checks",
      "options": [
        "Localizar ou manter contato com egressos",
        "Obter respostas aos questionários",
        "Atualizar os dados",
        "Integrar dados de fontes diferentes",
        "Dispor de tempo ou equipe",
        "Analisar e interpretar os dados",
        "Dispor de ferramentas adequadas",
        "Tratar os dados com privacidade",
        "Outra dificuldade",
        "Não percebo dificuldades",
        "Não sei informar"
      ],
      "required": false,
      "section": "necessidades",
      "help": "Marque todas as opções aplicáveis. Use uma opção de ausência ou desconhecimento sozinha.",
      "source": "Autoral contextual: Simon e Pacheco (2017), Leopoldo (2019) e requisitos do estudo; não é escala validada desses trabalhos",
      "display_title": "Quais dificuldades existem nesse acompanhamento?"
    },
    {
      "id": "D8",
      "title": "Que informação sobre egressos mais faz falta para as decisões da coordenação?",
      "kind": "paragraph",
      "options": [],
      "required": false,
      "section": "necessidades",
      "help": "",
      "source": "Autoral contextual: Simon e Pacheco (2017), Leopoldo (2019) e requisitos do estudo; não é escala validada desses trabalhos",
      "display_title": "Que informação faz falta para as decisões da coordenação?"
    },
    {
      "id": "UP1",
      "title": "A Alumni View ajudaria a realizar o acompanhamento de egressos com mais agilidade.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A Alumni View ajudaria a realizar o acompanhamento de egressos com mais agilidade."
    },
    {
      "id": "UP2",
      "title": "A Alumni View contribuiria para melhorar meu desempenho nas atividades de acompanhamento.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A Alumni View contribuiria para melhorar meu desempenho nas atividades de acompanhamento."
    },
    {
      "id": "UP3",
      "title": "A Alumni View permitiria produzir mais análises úteis no tempo disponível.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A Alumni View permitiria produzir mais análises úteis no tempo disponível."
    },
    {
      "id": "UP4",
      "title": "A Alumni View ajudaria a realizar o acompanhamento de forma mais eficaz.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A Alumni View ajudaria a realizar o acompanhamento de forma mais eficaz."
    },
    {
      "id": "UP5",
      "title": "A Alumni View facilitaria o trabalho de acompanhamento de egressos.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A Alumni View facilitaria o trabalho de acompanhamento de egressos."
    },
    {
      "id": "UP6",
      "title": "Considero a Alumni View útil para as atividades da coordenação.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Considero a Alumni View útil para as atividades da coordenação."
    },
    {
      "id": "FUP1",
      "title": "Foi fácil aprender a usar a Alumni View.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Foi fácil aprender a usar a Alumni View."
    },
    {
      "id": "FUP2",
      "title": "Consegui fazer a Alumni View apresentar as análises que eu buscava.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Consegui fazer a Alumni View apresentar as análises que eu buscava."
    },
    {
      "id": "FUP3",
      "title": "A interação com a Alumni View foi clara e compreensível.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "A interação com a Alumni View foi clara e compreensível."
    },
    {
      "id": "FUP4",
      "title": "Consegui ajustar a exploração dos dados às minhas necessidades.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Consegui ajustar a exploração dos dados às minhas necessidades."
    },
    {
      "id": "FUP5",
      "title": "Acredito que seria fácil adquirir habilidade no uso da Alumni View.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Acredito que seria fácil adquirir habilidade no uso da Alumni View."
    },
    {
      "id": "FUP6",
      "title": "Considero a Alumni View fácil de usar.",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "required": false,
      "section": "tam",
      "help": "",
      "source": "Adaptação contextual de Davis (1989), apêndice, p. 340; tradução livre e alteração dos referentes e das âncoras de resposta; requer pré-teste",
      "display_title": "Considero a Alumni View fácil de usar."
    },
    {
      "id": "A1",
      "title": "Que partes da ferramenta ajudaram nas tarefas realizadas, se alguma?",
      "kind": "paragraph",
      "options": [],
      "required": false,
      "section": "complementares",
      "help": "",
      "source": "Autoral: necessidades, dificuldades e adequação institucional; orientação de avaliação contextual em Kaliisa et al. (2023)",
      "display_title": "O que ajudou no uso da plataforma?"
    },
    {
      "id": "A2",
      "title": "Que dificuldades você encontrou durante o uso?",
      "kind": "paragraph",
      "options": [],
      "required": false,
      "section": "complementares",
      "help": "",
      "source": "Autoral: necessidades, dificuldades e adequação institucional; orientação de avaliação contextual em Kaliisa et al. (2023)",
      "display_title": "O que dificultou o uso?"
    },
    {
      "id": "A3",
      "title": "O que precisaria mudar para a ferramenta ser utilizada no seu curso?",
      "kind": "paragraph",
      "options": [],
      "required": false,
      "section": "complementares",
      "help": "",
      "source": "Autoral: necessidades, dificuldades e adequação institucional; orientação de avaliação contextual em Kaliisa et al. (2023)",
      "display_title": "O que precisa mudar para usar a plataforma no seu curso?"
    },
    {
      "id": "N1",
      "title": "Qual foi o principal motivo para não experimentar a ferramenta nesta avaliação?",
      "kind": "paragraph",
      "options": [],
      "required": false,
      "section": "sem_uso",
      "help": "",
      "source": "Autoral: caracterização ou operação do estudo",
      "display_title": "O que impediu você de experimentar a plataforma?"
    },
    {
      "id": "IU1",
      "title": "Se tivesse acesso contínuo à ferramenta, eu teria intenção de utilizá-la no acompanhamento de egressos.",
      "section": "intencao",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "source": "Autoral: intenção declarada de uso; não atribuída às escalas finais de Davis (1989)",
      "help": "",
      "required": false,
      "display_title": "Se tivesse acesso contínuo à ferramenta, eu teria intenção de utilizá-la no acompanhamento de egressos."
    },
    {
      "id": "IU2",
      "title": "Eu consideraria incorporar a ferramenta à rotina da coordenação.",
      "section": "intencao",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "source": "Autoral: intenção declarada de uso; não atribuída às escalas finais de Davis (1989)",
      "help": "",
      "required": false,
      "display_title": "Eu consideraria incorporar a ferramenta à rotina da coordenação."
    },
    {
      "id": "XP1",
      "title": "As explicações ajudaram a entender quais fatores contribuíram para as estimativas dos modelos.",
      "section": "xai",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "source": "Autoral com fundamentação conceitual em Hoffman et al. (2023), seções 2 e 3; não é reprodução da Explanation Satisfaction Scale",
      "help": "",
      "required": false,
      "display_title": "As explicações ajudaram a entender quais fatores contribuíram para as estimativas dos modelos."
    },
    {
      "id": "XP2",
      "title": "A apresentação das contribuições por grupo foi clara para mim.",
      "section": "xai",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "source": "Autoral com fundamentação conceitual em Hoffman et al. (2023), seções 2 e 3; não é reprodução da Explanation Satisfaction Scale",
      "help": "",
      "required": false,
      "display_title": "A apresentação das contribuições por grupo foi clara para mim."
    },
    {
      "id": "XP3",
      "title": "As informações sobre os limites dos modelos foram compreensíveis para mim.",
      "section": "xai",
      "kind": "choice",
      "options": [
        "1 — Discordo totalmente",
        "2 — Discordo",
        "3 — Discordo parcialmente",
        "4 — Nem concordo nem discordo",
        "5 — Concordo parcialmente",
        "6 — Concordo",
        "7 — Concordo totalmente",
        "Não pude avaliar"
      ],
      "source": "Autoral com fundamentação conceitual em Hoffman et al. (2023), seções 2 e 3; não é reprodução da Explanation Satisfaction Scale",
      "help": "",
      "required": false,
      "display_title": "As informações sobre os limites dos modelos foram compreensíveis para mim."
    },
    {
      "id": "XC1",
      "title": "Um fator com maior importância no laboratório permite concluir que ele causou o resultado profissional? Justifique brevemente.",
      "section": "xai",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: compreensão e limites de interpretação; estratégia de avaliação de modelos mentais em Hoffman et al. (2023); conteúdo técnico do protocolo XAI da plataforma",
      "help": "",
      "required": false,
      "display_title": "Um fator com maior importância no laboratório permite concluir que ele causou o resultado profissional? Justifique brevemente."
    },
    {
      "id": "XC2",
      "title": "O que uma contribuição média negativa de um grupo representa no resultado do modelo?",
      "section": "xai",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: compreensão e limites de interpretação; estratégia de avaliação de modelos mentais em Hoffman et al. (2023); conteúdo técnico do protocolo XAI da plataforma",
      "help": "",
      "required": false,
      "display_title": "O que uma contribuição média negativa de um grupo representa no resultado do modelo?"
    },
    {
      "id": "XC3",
      "title": "Se um modelo apresentar desempenho próximo ao modelo de referência, que cuidado você teria ao utilizar suas explicações?",
      "section": "xai",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: compreensão e limites de interpretação; estratégia de avaliação de modelos mentais em Hoffman et al. (2023); conteúdo técnico do protocolo XAI da plataforma",
      "help": "",
      "required": false,
      "display_title": "Se um modelo apresentar desempenho próximo ao modelo de referência, que cuidado você teria ao utilizar suas explicações?"
    },
    {
      "id": "XN1",
      "title": "Qual foi o principal motivo para não conseguir visualizar os resultados do Laboratório XAI?",
      "section": "sem_xai",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: operação do estudo",
      "help": "",
      "required": false,
      "display_title": "O que impediu você de visualizar os resultados do XAI?"
    },
    {
      "id": "T1R",
      "title": "T1: qual é o total de egressos e quantos cursos há na base?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 1 - Total de egressos e cursos"
    },
    {
      "id": "T2R",
      "title": "T2: quantos registros ficaram no recorte?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 2 - Total de registros no recorte"
    },
    {
      "id": "T3R",
      "title": "T3: qual foi a categoria de cargo mais frequente?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 3 - Categoria mais frequente"
    },
    {
      "id": "T4R",
      "title": "T4: o que conta como evidência de liderança ou gerência?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 4 - Evidência de liderança ou gerência"
    },
    {
      "id": "T5R",
      "title": "T5: como a AUC ROC de cada modelo se compara à referência?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 5 - Comparação da AUC com a referência"
    },
    {
      "id": "T6R",
      "title": "T6: qual fator teve maior importância no Random forest? Escolha um grupo de Anos de formado e informe o sinal da contribuição exibida.",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 6 - Fator mais importante e contribuição de um grupo"
    },
    {
      "id": "T7R",
      "title": "T7: conseguiu baixar os dois arquivos? Qual limitação identificou?",
      "section": "tarefas",
      "kind": "paragraph",
      "options": [],
      "source": "Autoral: produto verificável da tarefa na versão React v3",
      "help": "",
      "required": false,
      "display_title": "Tarefa 7 - Downloads e limitação identificada"
    }
  ],
  "tasks": [
    [
      "T1",
      "Confirme que está usando a base fornecida pela pesquisadora. Na Visão geral, sem filtros, identifique o total de egressos e o número de cursos."
    ],
    [
      "T2",
      "Aplique o filtro de Engenharia de Software e o intervalo de conclusão de 2020 a 2025, inclusive. Identifique o total do recorte."
    ],
    [
      "T3",
      "Mantendo os filtros da T2, encontre na Inserção profissional a categoria de cargo mais frequente."
    ],
    [
      "T4",
      "Na página Trajetórias, consulte liderança ou gerência e leia a definição na Metodologia. Identifique o que conta como evidência desse indicador."
    ],
    [
      "T5",
      "Abra o Laboratório XAI, selecione liderança ou gerência e clique em Calcular e comparar. Compare a AUC ROC dos dois modelos com a referência."
    ],
    [
      "T6",
      "No Laboratório XAI, selecione Random forest. Identifique o fator de maior importância global e consulte uma contribuição média por grupo, escolhendo o fator Anos de formado."
    ],
    [
      "T7",
      "Use o botão Exportar para baixar um relatório do recorte. No Laboratório XAI, use Exportar análise XAI. Identifique uma limitação dos dados ou do método."
    ]
  ],
  "task_options": [
    "Concluí sem ajuda",
    "Concluí com ajuda",
    "Não consegui concluir",
    "Não realizei"
  ],
  "scale": [
    "1 — Discordo totalmente",
    "2 — Discordo",
    "3 — Discordo parcialmente",
    "4 — Nem concordo nem discordo",
    "5 — Concordo parcialmente",
    "6 — Concordo",
    "7 — Concordo totalmente",
    "Não pude avaliar"
  ],
  "description": "Pesquisa de TCC de Camilla Borchhardt sobre acompanhamento de egressos e a Alumni View. Primeiro, responda sobre o curso; depois, experimente a plataforma e avalie sua experiência. Tempo estimado: 30 a 40 minutos, a conferir no pré-teste.\n\nA participação é voluntária. Você pode pular perguntas opcionais ou encerrar antes de enviar. Não informe dados individuais de egressos. Não solicitamos nome nem coletamos e-mail automaticamente. Resultados serão apresentados em síntese; atuação e comentários podem permitir identificação indireta, e as citações serão revisadas. Contato: camillaborchhardt.aluno@unipampa.edu.br.",
  "grid_columns": [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "Não pude avaliar"
  ],
  "scale_help": "1 = Discordo totalmente · 2 = Discordo · 3 = Discordo parcialmente · 4 = Nem concordo nem discordo · 5 = Concordo parcialmente · 6 = Concordo · 7 = Concordo totalmente. Marque uma opção por linha; use Não pude avaliar quando necessário."
};
function criarFormularioAlumniViewLimpo() {
  const lock=LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const props=PropertiesService.getScriptProperties();
    const id=props.getProperty('ALUMNI_FORM_LIMPO_33_ID');
    if(id){
      const old=FormApp.openById(id);
      Logger.log('Rascunho limpo existente: '+old.getEditUrl());
      if(props.getProperty('ALUMNI_FORM_LIMPO_33_COMPLETE')!=='true') Logger.log('A criação anterior ficou parcial. Revise manualmente; este script não apaga nem duplica o formulário.');
      return old.getEditUrl();
    }
    const form=FormApp.create(SPEC.title+' - v3.3',false);
    props.setProperty('ALUMNI_FORM_LIMPO_33_ID',form.getId());
    form.setCollectEmail(false).setProgressBar(true).setShuffleQuestions(false).setPublishingSummary(false)
      .setDescription(SPEC.description+(INFORMACOES_GUARDA.trim()?'\n\n'+INFORMACOES_GUARDA:''))
      .setConfirmationMessage('Agradecemos sua participação.');
    const consent=form.addMultipleChoiceItem().setTitle('Você concorda em participar voluntariamente?').setRequired(true);
    const diagnostic=form.addPageBreakItem().setTitle('1. Sobre o curso')
      .setHelpText('Responda sobre o curso com o qual tem maior vínculo. Apenas as questões indicadas com asterisco são obrigatórias.');
    ['P1','P2','P3'].forEach(id=>addQuestion(form,SPEC.items.find(q=>q.id===id)));
    const situation=addQuestion(form,SPEC.items.find(q=>q.id==='D1'));
    const practices=form.addPageBreakItem().setTitle('2. Acompanhamento dos egressos');
    SPEC.items.filter(q=>q.section==='praticas').forEach(q=>addQuestion(form,q));
    const needs=form.addPageBreakItem().setTitle('3. Dificuldades e necessidades');
    SPEC.items.filter(q=>q.section==='necessidades').forEach(q=>addQuestion(form,q));
    form.addPageBreakItem().setTitle('4. Experimente a Alumni View')
      .setHelpText('Abra a plataforma '+(URL_FERRAMENTA.trim()?'em '+URL_FERRAMENTA:'no endereço fornecido pela pesquisadora')+'. Use somente o CSV fornecido pela pesquisadora. Se a base não estiver carregada, importe-o em Base de dados. Confira que a plataforma indica uma base importada antes das tarefas. Faça as tarefas na ordem; se não conseguir, registre e prossiga. Consulte as orientações disponíveis na plataforma. A origem geográfica representa nascimento.\n\n'+SPEC.tasks.map(t=>t[0]+': '+t[1]).join('\n\n'));
    const used=form.addMultipleChoiceItem().setTitle('Você conseguiu experimentar a Alumni View?').setRequired(true);
    const assessment=form.addPageBreakItem().setTitle('5. Sua experiência com a plataforma');
    form.addGridItem().setTitle('Como foi a realização das tarefas?')
      .setRows(SPEC.tasks.map(t=>t[0]+': '+t[1])).setColumns(SPEC.task_options).setRequired(false);
    SPEC.items.filter(q=>q.section==='tarefas').forEach(q=>addQuestion(form,q));
    addScale(form, 'Utilidade percebida', SPEC.items.filter(q=>q.id.startsWith('UP')));
    addScale(form, 'Facilidade de uso percebida', SPEC.items.filter(q=>q.id.startsWith('FUP')));
    const viewed=form.addMultipleChoiceItem().setTitle('Você conseguiu visualizar resultados no Laboratório XAI?').setRequired(true);
    const xai=form.addPageBreakItem().setTitle('6. Explicações do XAI')
      .setHelpText('Avalie os resultados que conseguiu visualizar. Nas perguntas abertas, use suas palavras; se não conseguiu interpretar, pode informar isso.');
    addScale(form, 'Avaliação das explicações', SPEC.items.filter(q=>q.id.startsWith('XP')));
    SPEC.items.filter(q=>q.id.startsWith('XC')).forEach(q=>addQuestion(form,q));
    const noXai=form.addPageBreakItem().setTitle('Laboratório XAI não visualizado');
    SPEC.items.filter(q=>q.section==='sem_xai').forEach(q=>addQuestion(form,q));
    const common=form.addPageBreakItem().setTitle('7. Uso futuro e sugestões');
    addScale(form, 'Intenção de uso', SPEC.items.filter(q=>q.section==='intencao'));
    SPEC.items.filter(q=>q.section==='complementares').forEach(q=>addQuestion(form,q));
    const noUse=form.addPageBreakItem().setTitle('Ferramenta não experimentada');
    SPEC.items.filter(q=>q.section==='sem_uso').forEach(q=>addQuestion(form,q));
    consent.setChoices([consent.createChoice('Sim, concordo',diagnostic),consent.createChoice('Não concordo',FormApp.PageNavigationType.SUBMIT)]);
    situation.setChoices(SPEC.items.find(q=>q.id==='D1').options.map((v,i)=>situation.createChoice(v,i<2?practices:needs)));
    used.setChoices([used.createChoice('Sim, mesmo que parcialmente',assessment),used.createChoice('Não',noUse)]);
    viewed.setChoices([viewed.createChoice('Sim, visualizei resultados',xai),viewed.createChoice('Acessei, mas não consegui visualizar resultados',noXai),viewed.createChoice('Não acessei o laboratório',noXai)]);
    // A navegação da quebra controla a seção ANTERIOR. A chegada direta a
    // noXai por X0 não aplica esta ação ao destino.
    noXai.setGoToPage(common);
    noUse.setGoToPage(FormApp.PageNavigationType.SUBMIT);
    props.setProperty('ALUMNI_FORM_LIMPO_33_COMPLETE','true');
    Logger.log('Rascunho limpo criado, não publicado: '+form.getEditUrl());
    if(!URL_FERRAMENTA.trim()) Logger.log('Antes de aplicar, forneça acesso efetivo à plataforma e confira as instruções da etapa 2.');
    if(!INFORMACOES_GUARDA.trim()) Logger.log('Antes de aplicar, complete as informações de guarda, acesso e retenção conforme o protocolo da pesquisa.');
    return form.getEditUrl();
  } finally {lock.releaseLock();}
}
function addQuestion(form,q){
  let item;
  if(q.kind==='paragraph')item=form.addParagraphTextItem();
  else if(q.kind==='checks')item=form.addCheckboxItem().setChoiceValues(q.native_other ? q.options.slice(0,-1) : q.options);
  else item=form.addMultipleChoiceItem().setChoiceValues(q.native_other ? q.options.slice(0,-1) : q.options);
  if(q.native_other)item.showOtherOption(true);
  item.setTitle(q.display_title || q.title).setRequired(q.required);
  if(q.help)item.setHelpText(q.help);
  return item;
}

function addScale(form,title,rows){
  return form.addGridItem().setTitle(title).setHelpText(SPEC.scale_help)
    .setRows(rows.map(q=>q.display_title || q.title)).setColumns(SPEC.grid_columns).setRequired(false);
}
