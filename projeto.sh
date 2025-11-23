# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Iniciando Configuração do Git para o Projeto PQC...${NC}"

# 1. Verifica se git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git não encontrado. Instalando...${NC}"
    if [ -f /etc/redhat-release ]; then
        sudo dnf install git -y
    else
        sudo apt-get install git -y
    fi
fi

# 2. Configuração de Usuário (se não existir)
if [ -z "$(git config --global user.email)" ]; then
    echo -e "${YELLOW}>>> Configuração Inicial do Git Necessária:${NC}"
    read -p "Digite seu Email para o GitHub: " git_email
    read -p "Digite seu Nome para o GitHub: " git_name
    git config --global user.email "$git_email"
    git config --global user.name "$git_name"
fi

# 3. Criar .gitignore (SEGURANÇA CRÍTICA)
echo -e "${GREEN}>>> Criando arquivo .gitignore blindado...${NC}"
cat <<EOF > .gitignore
# Python artifacts
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/

# PQC Keys (NUNCA SUBIR CHAVES PRIVADAS!)
keys/
*.pem
*.key
*.bin

# Logs e databases
*.log
*.sqlite3

# OS specific
.DS_Store
EOF

# 4. Inicializar Repositório
if [ ! -d ".git" ]; then
    echo -e "${GREEN}>>> Inicializando repositório Git...${NC}"
    git init
    git branch -M main
else
    echo -e "${YELLOW}>>> Repositório já inicializado.${NC}"
fi

# 5. Adicionar arquivos e Commit
echo -e "${GREEN}>>> Adicionando arquivos (respeitando o .gitignore)...${NC}"
git add .
git commit -m "Initial commit: PQC Hybrid Encryption Server (AlmaLinux + OpenSSL OQS)"

# 6. Configurar Remote e Push
echo -e "${YELLOW}>>> Atenção: Você precisa ter criado um repositório VAZIO no GitHub.${NC}"
read -p "Cole a URL do repositório (ex: https://github.com/usuario/pqc-server.git): " repo_url

if [ -n "$repo_url" ]; then
    # Remove origin se já existir para evitar erro
    git remote remove origin 2>/dev/null
    git remote add origin "$repo_url"
   
    echo -e "${GREEN}>>> Enviando para o GitHub...${NC}"
    echo -e "${YELLOW}Dica: Se pedir senha, use seu 'Personal Access Token' (PAT), não a senha da conta.${NC}"
   
    git push -u origin main
   
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}>>> SUCESSO! Código enviado para $repo_url 🚀${NC}"
    else
        echo -e "${RED}>>> Erro no push. Verifique suas credenciais ou a URL.${NC}"
    fi
else
    echo -e "${RED}>>> URL inválida. Processo abortado (mas o commit local foi feito).${NC}"
fi
```
