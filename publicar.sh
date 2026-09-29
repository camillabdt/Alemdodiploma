#!/usr/bin/env bash
# Publica o painel no GitHub (repositório público, SEM dados reais).
#
# Uso, dentro da pasta do projeto:
#     bash publicar.sh
#
# O que o script faz:
#   1. confere se o GitHub CLI (gh) está instalado e logado na sua conta;
#   2. cria um histórico Git novo e verifica que nenhum arquivo com dados reais entra no commit;
#   3. se o repositório já existir, pede confirmação, APAGA e recria (remove o commit antigo com a base);
#   4. envia o código e mostra os próximos passos no Streamlit Cloud.
set -euo pipefail

REPO="camillabdt/Alemdodiploma"
PROIBIDOS='dataset_publico\.csv|secrets\.toml|dataset_gold\.csv|divergencias|planilha_auditoria|amostra_'

cd "$(dirname "$0")"
[ -f app/app.py ] || { echo "Rode este script dentro da pasta do projeto."; exit 1; }

echo "== 1/4 Verificando ferramentas"
command -v git >/dev/null || { echo "Instale o git: sudo apt install git"; exit 1; }
if ! command -v gh >/dev/null; then
  echo "Instale o GitHub CLI e rode de novo:  sudo apt install gh"
  exit 1
fi
if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Vamos entrar na sua conta do GitHub (abre o navegador)."
  gh auth login -h github.com -p https -w
fi

echo "== 2/4 Preparando o commit"
rm -rf .git
git init -q
git branch -M main
if [ -z "$(git config user.email || true)" ]; then
  git config user.name  "$(gh api user --jq '.name // .login')"
  git config user.email "$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"
fi
git add .
if git ls-files | grep -Eq "$PROIBIDOS"; then
  echo "ERRO: um arquivo com dados reais entraria no commit:"
  git ls-files | grep -E "$PROIBIDOS"
  echo "Nada foi enviado. Verifique o .gitignore."
  rm -rf .git
  exit 1
fi
echo "   Nenhum dado real no commit. Arquivos de dados versionados:"
git ls-files | grep -E '^data/' | sed 's/^/     /'
git commit -q -m "Versão inicial do painel do TCC II"

echo "== 3/4 Repositório no GitHub"
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "   O repositório $REPO já existe e tem no histórico a base que foi enviada antes."
  echo "   Ele será APAGADO e recriado vazio, com este código."
  read -r -p "   Digite APAGAR para confirmar: " ok
  [ "$ok" = "APAGAR" ] || { echo "Cancelado. Nada foi alterado no GitHub."; exit 1; }
  gh auth refresh -h github.com -s delete_repo
  gh repo delete "$REPO" --yes
  sleep 3
fi
gh repo create "$REPO" --public --source=. --remote=origin --push \
  --description "Painel de trajetórias profissionais de egressos de Computação da UNIPAMPA (TCC II)"

echo "== 4/4 Pronto: https://github.com/$REPO"
cat <<'EOF'

Agora, no navegador, em https://share.streamlit.io :
  1. Entre com a conta do GitHub e clique em "Create app".
  2. Repositório camillabdt/Alemdodiploma, branch main, arquivo app/app.py.
  3. Em "Advanced settings": Python 3.12 e, no campo "Secrets",
     cole o conteúdo inteiro do arquivo secrets.toml (fica FORA desta pasta).
  4. Clique em "Deploy".
EOF
