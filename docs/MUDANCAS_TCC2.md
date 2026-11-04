# Versão 3: plataforma e XAI

- Interface React e API FastAPI substituem a interface anterior.
- Busca nominal, integrações de buscadores, campos de chave e coleta de perfis retirados do produto.
- Laboratório XAI centraliza comparação de modelos, referência por prevalência, contribuições fora da amostra e exportação reprodutível.
- Importação recebe base preparada, reconhece cursos e permite totais opcionais por curso sem exigir JSON do usuário.
- A API valida consistência do ano de referência, protege recortes pequenos e mantém sessão em memória.
- Relatórios usam os mesmos agregados protegidos da API; análise XAI tem exportação própria.

A base fictícia continua sendo demonstração. Não houve aplicação com coordenadores nem auditoria da base real nesta migração. Ver protocolo de avaliação atualizado e método XAI.
