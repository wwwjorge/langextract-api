# LangExtract API

Uma API FastAPI para extração de texto de documentos PDF, Word e PowerPoint usando LangChain.

## 🚀 Deploy Rápido com Portainer

### Opção 1: Deploy via Git (Recomendado)

1. **No Portainer**, vá em **Stacks** → **Add Stack**
2. **Nome**: `langextract-api`
3. **Build method**: Repository
4. **Repository URL**: `https://github.com/wwwjorge/langextract-api`
5. **Compose path**: `docker-compose.portainer.yml`
6. **Environment variables**:
   ```
   API_KEY=seu_api_key_aqui
   UPLOAD_DIR=/app/uploads
   MAX_FILE_SIZE=50
   ```
7. Clique em **Deploy the stack**

### Opção 2: Deploy via Upload de Arquivo

Siga as instruções detalhadas em [PORTAINER_ZIP_DEPLOY.md](PORTAINER_ZIP_DEPLOY.md)

## 📋 Funcionalidades

- ✅ Extração de texto de PDF, DOCX, PPTX
- ✅ API REST com FastAPI
- ✅ Autenticação via API Key
- ✅ Upload de arquivos com validação
- ✅ Containerização com Docker
- ✅ Deploy otimizado para Portainer

## 🔧 Configuração Local

```bash
# Clone o repositório
git clone https://github.com/wwwjorge/langextract-api.git
cd langextract-api

# Configure o ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Execute com Docker
docker-compose up -d
```

## 📚 Documentação

- [README_API.md](README_API.md) - Documentação da API
- [README_PORTAINER.md](README_PORTAINER.md) - Guia completo do Portainer
- [DEPLOY_PORTAINER.md](DEPLOY_PORTAINER.md) - Instruções de deploy
- [PORTAINER_BUILD_GUIDE.md](PORTAINER_BUILD_GUIDE.md) - Guia de build

## 🌐 Acesso

Após o deploy:
- **API**: `http://seu-servidor:8000`
- **Documentação**: `http://seu-servidor:8000/docs`
- **Health Check**: `http://seu-servidor:8000/health`

## 🔑 Autenticação

Todas as rotas (exceto `/health` e `/docs`) requerem o header:
```
X-API-Key: seu_api_key_aqui
```

## 📝 Exemplo de Uso

```bash
# Upload e extração de texto
curl -X POST "http://localhost:8000/extract" \
  -H "X-API-Key: seu_api_key_aqui" \
  -F "file=@documento.pdf"
```

## 🛠️ Tecnologias

- **FastAPI** - Framework web
- **LangChain** - Processamento de documentos
- **Docker** - Containerização
- **Portainer** - Orquestração

---

**Desenvolvido para deploy fácil e rápido com Portainer** 🐳
