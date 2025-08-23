#!/bin/bash

# =============================================================================
# Script para criar ZIP de deploy do LangExtract API para Portainer
# =============================================================================

set -e  # Exit on any error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Função para verificar se arquivo existe
check_file() {
    if [ ! -f "$1" ]; then
        print_status $RED "❌ Arquivo obrigatório não encontrado: $1"
        exit 1
    fi
}

# Função para verificar se diretório existe
check_dir() {
    if [ ! -d "$1" ]; then
        print_status $RED "❌ Diretório obrigatório não encontrado: $1"
        exit 1
    fi
}

print_status $BLUE "🚀 Criando ZIP para deploy do LangExtract API no Portainer"
print_status $BLUE "=========================================================="

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.portainer-lite.yml" ]; then
    print_status $RED "❌ Execute este script na pasta raiz do projeto LangExtract"
    print_status $YELLOW "💡 Navegue até a pasta que contém docker-compose.portainer-lite.yml"
    exit 1
fi

# Verificar arquivos obrigatórios
print_status $YELLOW "🔍 Verificando arquivos obrigatórios..."
check_file "Dockerfile.api"
check_file "docker-compose.portainer-lite.yml"
check_file ".env.portainer-lite"
check_file "requirements.api.txt"
check_dir "api"

print_status $GREEN "✅ Todos os arquivos obrigatórios encontrados"

# Limpar arquivos temporários
print_status $YELLOW "🧹 Limpando arquivos temporários..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Criar nome do arquivo ZIP com timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ZIP_NAME="langextract-api-${TIMESTAMP}.zip"

print_status $YELLOW "📦 Criando arquivo ZIP: $ZIP_NAME"

# Criar ZIP excluindo arquivos desnecessários
zip -r "$ZIP_NAME" . \
    -x "*.git*" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*/*/__pycache__/*" \
    -x ".venv/*" \
    -x "venv/*" \
    -x "env/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*.pyd" \
    -x "uploads/*" \
    -x "outputs/*" \
    -x "logs/*" \
    -x "*.log" \
    -x "node_modules/*" \
    -x ".DS_Store" \
    -x "Thumbs.db" \
    -x "*.tmp" \
    -x "*.temp" \
    -x ".pytest_cache/*" \
    -x ".coverage" \
    -x "htmlcov/*" \
    -x ".tox/*" \
    -x "dist/*" \
    -x "build/*" \
    -x "*.egg-info/*" \
    -x "create_deploy_zip.sh" \
    > /dev/null

if [ $? -eq 0 ]; then
    print_status $GREEN "✅ ZIP criado com sucesso!"
else
    print_status $RED "❌ Erro ao criar ZIP"
    exit 1
fi

# Mostrar informações do arquivo
ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
print_status $BLUE "📊 Informações do arquivo:"
print_status $NC "   📁 Nome: $ZIP_NAME"
print_status $NC "   📏 Tamanho: $ZIP_SIZE"
print_status $NC "   📍 Local: $(pwd)/$ZIP_NAME"

# Listar conteúdo do ZIP (primeiros 20 arquivos)
print_status $BLUE "\n📋 Conteúdo do ZIP (primeiros 20 arquivos):"
zip -l "$ZIP_NAME" | head -n 25 | tail -n +4

# Verificar arquivos críticos no ZIP
print_status $YELLOW "\n🔍 Verificando arquivos críticos no ZIP..."
CRITICAL_FILES=(
    "Dockerfile.api"
    "docker-compose.portainer-lite.yml"
    ".env.portainer-lite"
    "requirements.api.txt"
    "api/main.py"
    "api/__init__.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if zip -l "$ZIP_NAME" | grep -q "$file"; then
        print_status $GREEN "   ✅ $file"
    else
        print_status $RED "   ❌ $file (FALTANDO!)"
    fi
done

print_status $BLUE "\n🎯 Próximos passos:"
print_status $NC "1. Acesse seu Portainer"
print_status $NC "2. Vá em Stacks > Add stack"
print_status $NC "3. Escolha 'Upload' como build method"
print_status $NC "4. Faça upload do arquivo: $ZIP_NAME"
print_status $NC "5. Configure as variáveis de ambiente"
print_status $NC "6. Deploy da stack"

print_status $YELLOW "\n💡 Dicas:"
print_status $NC "• Use docker-compose.portainer-lite.yml como compose path"
print_status $NC "• Copie as variáveis do arquivo .env.portainer-lite"
print_status $NC "• Não esqueça de configurar GEMINI_API_KEY e API_SECRET_KEY"

print_status $GREEN "\n🎉 Deploy ZIP criado com sucesso!"
print_status $BLUE "=========================================================="