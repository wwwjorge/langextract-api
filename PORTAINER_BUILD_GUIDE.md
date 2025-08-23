## 🎯 Opções de Deploy no Portainer

### Opção 1: Repositório Git (Recomendado)
**Mais fácil e automático**

### Opção 2: Upload de Arquivos
**Para desenvolvimento local**

### Opção 3: Imagem Pré-construída
**Para produção**

---

## 🔧 Opção 1: Repositório Git (Recomendado)

### 1.1 Preparar Repositório
```bash
# No WSL2, navegue até a pasta do projeto
cd /mnt/f/Secondbrain/BrainServer/CodeServer/lagexstract

# Inicializar git (se não existir)
git init

# Adicionar arquivos
git add .
git commit -m "Initial commit - LangExtract API"

# Adicionar remote (GitHub, GitLab, etc.)
git remote add origin https://github.com/seu-usuario/langextract-api.git
git push -u origin main
```

### 1.2 Deploy no Portainer
1. **Stacks** → **Add stack**
2. **Name:** `langextract-api`
3. **Build method:** `Repository**
4. **Repository URL:** `https://github.com/seu-usuario/langextract-api.git`
5. **Reference:** `refs/heads/main`
6. **Compose path:** `docker-compose.portainer-lite.yml`
7. **Environment variables:** Cole conteúdo de `.env.portainer-lite`
8. **Deploy the stack**

---

## 📁 Opção 2: Upload de Arquivos

### 2.1 Criar Arquivo ZIP
```bash
# No WSL2
cd /mnt/f/Secondbrain/BrainServer/CodeServer/lagexstract

# Criar ZIP com arquivos necessários
zip -r langextract-api.zip . \
  -x "*.git*" \
  -x "__pycache__/*" \
  -x ".venv/*" \
  -x "*.pyc" \
  -x "uploads/*" \
  -x "outputs/*" \
  -x "logs/*"
```

### 2.2 Upload no Portainer
1. **Stacks** → **Add stack**
2. **Name:** `langextract-api`
3. **Build method:** **Upload**
4. **Select file:** `langextract-api.zip`
5. **Compose path:** `docker-compose.portainer-lite.yml`
6. **Environment variables:** Cole conteúdo de `.env.portainer-lite`
7. **Deploy the stack**

### 2.3 Script Automatizado para ZIP
```bash
#!/bin/bash
# create_deploy_zip.sh

echo "Criando ZIP para deploy no Portainer..."

# Limpar arquivos temporários
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Criar ZIP
zip -r "langextract-api-$(date +%Y%m%d-%H%M%S).zip" . \
  -x "*.git*" \
  -x "__pycache__/*" \
  -x ".venv/*" \
  -x "*.pyc" \
  -x "uploads/*" \
  -x "outputs/*" \
  -x "logs/*" \
  -x "*.log" \
  -x "node_modules/*" \
  -x ".DS_Store" \
  -x "Thumbs.db"

echo "ZIP criado com sucesso!"
ls -la *.zip
```

---

## 🐳 Opção 3: Imagem Pré-construída

### 3.1 Build Local da Imagem
```bash
# No WSL2
cd /mnt/f/Secondbrain/BrainServer/CodeServer/lagexstract

# Build da imagem
docker build -f Dockerfile.api -t langextract-api:latest .

# Tag para registry
docker tag langextract-api:latest seu-registry/langextract-api:latest

# Push para registry
docker push seu-registry/langextract-api:latest
```

### 3.2 Docker Compose para Imagem Pré-construída
```yaml
# docker-compose.portainer-prebuilt.yml
version: '3.8'

services:
  langextract-api:
    image: seu-registry/langextract-api:latest
    ports:
      - "${LANGEXTRACT_API_PORT:-8000}:8000"
    environment:
      - PYTHONPATH=/app
      - LANGEXTRACT_API_KEY=${LANGEXTRACT_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_SECRET_KEY=${API_SECRET_KEY}
      - API_ALGORITHM=${API_ALGORITHM:-HS256}
      - API_ACCESS_TOKEN_EXPIRE_MINUTES=${API_ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      - DEFAULT_MODEL=${DEFAULT_MODEL:-gemini-1.5-flash}
      - DEFAULT_PROVIDER=${DEFAULT_PROVIDER:-gemini}
      - MAX_FILE_SIZE_MB=${MAX_FILE_SIZE_MB:-50}
      - MAX_WORKERS=${MAX_WORKERS:-4}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - CORS_ORIGINS=${CORS_ORIGINS:-*}
    volumes:
      - langextract-uploads:/app/uploads
      - langextract-outputs:/app/outputs
      - langextract-logs:/app/logs
    networks:
      - langextract-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  langextract-uploads:
    driver: local
  langextract-outputs:
    driver: local
  langextract-logs:
    driver: local

networks:
  langextract-network:
    driver: bridge
```

---

## 🔄 Workflow Recomendado

### Para Desenvolvimento
1. **Upload de ZIP** - Rápido para testes
2. Usar `docker-compose.portainer-lite.yml`
3. Validar com `validate_portainer_deploy.py`

### Para Produção
1. **Repositório Git** - Versionamento e CI/CD
2. **Imagem pré-construída** - Deploy mais rápido
3. Monitoramento e backup automático

---

## 📋 Checklist de Arquivos Necessários

### Arquivos Obrigatórios
- [ ] `Dockerfile.api`
- [ ] `docker-compose.portainer-lite.yml`
- [ ] `.env.portainer-lite`
- [ ] `api/` (pasta com código da API)
- [ ] `requirements.api.txt`

### Arquivos Opcionais
- [ ] `README_PORTAINER.md`
- [ ] `validate_portainer_deploy.py`
- [ ] `setup_api.py`

### Arquivos a Excluir do ZIP
- [ ] `.git/`
- [ ] `__pycache__/`
- [ ] `.venv/`
- [ ] `uploads/`
- [ ] `outputs/`
- [ ] `logs/`
- [ ] `*.pyc`
- [ ] `*.log`

---

## 🚨 Troubleshooting

### Erro: "Build context is empty"
**Causa:** ZIP não contém os arquivos necessários
**Solução:** Verificar se o ZIP contém `Dockerfile.api` e pasta `api/`

### Erro: "No such file or directory: requirements.api.txt"
**Causa:** Arquivo de dependências não encontrado
**Solução:** Verificar se `requirements.api.txt` está no ZIP

### Erro: "Cannot connect to Docker daemon"
**Causa:** Docker não está rodando no host do Portainer
**Solução:** Verificar status do Docker no host

### Build muito lento
**Causa:** Muitos arquivos desnecessários no contexto
**Solução:** Usar `.dockerignore` ou excluir arquivos do ZIP

---

## 💡 Dicas de Performance

### Otimizar Build Context
```bash
# .dockerignore
.git
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
Thumbs.db
uploads/*
outputs/*
logs/*
```

### Multi-stage Build
```dockerfile
# Dockerfile.api otimizado
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.api.txt .
RUN pip install --no-cache-dir -r requirements.api.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 Resumo das Opções

| Método | Facilidade | Velocidade | Produção | Recomendado |
|--------|------------|------------|----------|-------------|
| **Git Repo** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ✅ Sim |
| **Upload ZIP** | ⭐⭐ | ⭐⭐⭐ | ⭐ | 🔧 Dev |
| **Imagem Pré-construída** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 🚀 Prod |

**Recomendação:** Comece com **Upload ZIP** para testes, migre para **Git Repo** para desenvolvimento contínuo.