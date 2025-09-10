# LangExtract FastAPI

API REST para extração estruturada de dados de texto usando LLMs (Large Language Models).

## 🚀 Características

- **Autenticação JWT**: Sistema de autenticação seguro
- **Múltiplos Provedores**: Suporte para OpenAI, Google Gemini e Ollama
- **Processamento de Arquivos**: Suporte para TXT, MD, JSON (PDF e DOCX em desenvolvimento)
- **CORS Configurável**: Configuração flexível para diferentes origens
- **Documentação Automática**: Swagger UI e ReDoc integrados
- **Modelo Padrão**: Gemini-2.5-Flash como padrão

## 📋 Pré-requisitos

- Python 3.8+
- Chaves de API configuradas no arquivo `.env`
- Ollama instalado (opcional, para modelos locais)

## 🛠️ Instalação

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente:**
   - Copie as chaves de API do arquivo `.env` principal para `api/.env`
   - Ajuste as configurações conforme necessário

3. **Iniciar a API:**
   ```bash
   python start_api.py
   ```

## 🌐 Endpoints

### Autenticação
- `POST /auth/token` - Obter token JWT
  - Usuário padrão: `admin` / `admin`

### Extração
- `POST /extract` - Extrair dados de texto
- `POST /extract/file` - Extrair dados de arquivo

### Informações
- `GET /health` - Status da API e modelos disponíveis
- `GET /models` - Lista de modelos por provedor
- `GET /providers` - URLs dos provedores
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## 📝 Exemplo de Uso

### 1. Obter Token de Autenticação
```bash
curl -X POST "http://localhost:8001/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

### 2. Extrair Dados de Texto
```bash
curl -X POST "http://localhost:8001/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Maria estava feliz. João estudava medicina.",
    "prompt": "Extract people and their emotions",
    "model_id": "gemini-2.5-flash",
    "temperature": 0.3
  }'
```

### 3. Extrair de Arquivo
```bash
curl -X POST "http://localhost:8001/extract/file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@documento.txt" \
  -F "prompt=Extract key information" \
  -F "model_id=gemini-2.5-flash"
```

## 🔧 Configuração

### Arquivo `api/.env`
```env
# API Settings
API_SECRET_KEY=your-super-secret-jwt-key
API_HOST=0.0.0.0
API_PORT=8001

# Default Model
DEFAULT_MODEL=gemini-2.5-flash
DEFAULT_TEMPERATURE=0.3

# CORS
CORS_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS

# File Upload
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_EXTENSIONS=.txt,.pdf,.docx,.md,.json

# Provider URLs
OLLAMA_BASE_URL=http://localhost:11434
```

## 🤖 Modelos Suportados

### OpenAI
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

### Google Gemini
- gemini-2.5-flash (padrão)
- gemini-1.5-pro
- gemini-1.5-flash

### Ollama (Local)
- Qualquer modelo instalado localmente
- Detecção automática via API do Ollama

## 📊 Estrutura de Resposta

```json
{
  "success": true,
  "extractions": [
    {
      "class": "person",
      "text": "Maria",
      "attributes": {
        "emotion": "happy"
      }
    }
  ],
  "model_used": "gemini-2.5-flash",
  "provider": "gemini",
  "processing_time": 1.23,
  "error": null
}
```

## 🧪 Teste

Execute o script de teste:
```bash
python test_api.py
```

O teste verifica:
- ✅ Health check
- ✅ Autenticação
- ✅ Listagem de modelos
- ✅ Listagem de provedores
- ✅ Extração de texto

## 🐳 Deploy com Docker

### Usando Docker Compose

```bash
# Clone o repositório
git clone <repository-url>
cd langextract-api

# Configure as variáveis de ambiente
cp .env.sample .env
# Edite o .env com suas configurações

# Execute com Docker Compose
docker-compose up -d
```

### Deploy no Portainer

1. **Via GitHub Registry:**
   - Use o arquivo `portainer-stack.yml`
   - Configure as variáveis de ambiente no Portainer
   - Deploy como Stack

2. **Build Local:**
   ```bash
   docker build -t langextract-api .
   docker run -d -p 8001:8001 --env-file .env langextract-api
   ```

### GitHub Actions

O projeto inclui workflow automatizado que:
- Faz build da imagem Docker
- Executa testes automatizados
- Publica no GitHub Container Registry
- Executa scan de segurança

### Configuração de Produção

**Variáveis Essenciais:**
```env
API_SECRET_KEY=your-production-secret-key
API_ACCESS_TOKEN=your-production-api-token
CORS_ORIGINS=https://yourdomain.com
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
CLOUDFLARE_API_TOKEN=your-cloudflare-token
```

## 🚀 Próximos Passos

- [x] Containerização com Docker
- [x] Deploy automatizado via GitHub Actions
- [x] Suporte a Cloudflare Workers AI
- [x] Configuração de timeouts
- [ ] Monitoramento avançado
- [ ] Cache de respostas
- [ ] Rate limiting por usuário

## 🔒 Segurança

- Autenticação JWT obrigatória
- Validação de tipos de arquivo
- Limite de tamanho de upload
- Headers de segurança configuráveis
- Não exposição de chaves de API

## 📈 Monitoramento

- Endpoint `/health` para verificação de status
- Logs detalhados via Uvicorn
- Tempo de processamento nas respostas
- Detecção automática de modelos disponíveis

## 🚨 Troubleshooting

### Erro de Autenticação
- Verifique se o token JWT está válido
- Confirme usuário/senha (padrão: admin/admin)

### Modelo Não Encontrado
- Verifique se as chaves de API estão configuradas
- Para Ollama, confirme se o serviço está rodando

### Erro de CORS
- Ajuste `CORS_ORIGINS` no arquivo `.env`
- Verifique se os headers estão corretos

## 📞 URLs Importantes

- **API Base**: http://localhost:8001
- **Documentação**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health