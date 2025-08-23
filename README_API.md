# LangExtract API

Uma API REST baseada em FastAPI para o framework LangExtract do Google, fornecendo acesso programático às funcionalidades de extração de informações estruturadas de textos usando modelos de linguagem.

## 🚀 Características

- **API REST completa** com documentação automática (Swagger/OpenAPI)
- **Autenticação JWT** configurável
- **Suporte a múltiplos provedores LLM** (Gemini, OpenAI, Ollama)
- **Upload de arquivos** (TXT, MD, JSON, PDF, DOCX)
- **Processamento assíncrono** com status de jobs
- **Visualização HTML** dos resultados
- **Containerização Docker** completa
- **Configuração flexível** via variáveis de ambiente
- **Logs estruturados** para monitoramento

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose (recomendado)
- Chaves de API para provedores LLM (opcional)

## 🛠 Instalação Rápida

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/google/langextract
cd langextract

# Execute o script de setup
python setup_api.py
```

### 2. Configure as Variáveis de Ambiente

Edite o arquivo `.env` criado:

```env
# Configuração da API
API_SECRET_KEY=seu-secret-key-muito-seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Chaves dos Provedores LLM
GEMINI_API_KEY=sua-chave-gemini
OPENAI_API_KEY=sua-chave-openai
LANGEXTRACT_API_KEY=sua-chave-langextract

# Configuração Ollama
OLLAMA_HOST=http://ollama:11434
OLLAMA_BASE_URL=http://ollama:11434

# Modelo padrão
DEFAULT_MODEL_ID=gemma2:2b
DEFAULT_PROVIDER=ollama
```

### 3. Inicie os Serviços

```bash
# Com Docker (recomendado)
docker-compose up -d

# Ou com Python diretamente
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Documentação da API

Após iniciar os serviços, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Autenticação

### Obter Token de Acesso

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Resposta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token nas Requisições

```bash
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/models
```

## 🎯 Exemplos de Uso

### 1. Listar Modelos Disponíveis

```bash
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/models
```

### 2. Extração de Texto Simples

```bash
curl -X POST http://localhost:8000/extract/text \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "João Silva trabalha como engenheiro na empresa XYZ desde 2020.",
    "prompt_description": "Extrair informações sobre pessoas",
    "examples": [
      {
        "input": "Maria Santos é médica no Hospital ABC.",
        "output": {"nome": "Maria Santos", "profissao": "médica", "local": "Hospital ABC"}
      }
    ],
    "model_id": "gemma2:2b",
    "temperature": 0.1
  }'
```

### 3. Upload e Processamento de Arquivo

```bash
# Upload do arquivo
curl -X POST http://localhost:8000/extract/file \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@documento.pdf" \
  -F "prompt_description=Extrair informações de contato" \
  -F "model_id=gemma2:2b"
```

### 4. Verificar Status da Extração

```bash
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/extract/status/EXTRACTION_ID
```

### 5. Baixar Resultados

```bash
# Resultado JSON
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/extract/download/EXTRACTION_ID/json

# Visualização HTML
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/extract/download/EXTRACTION_ID/html
```

## 🔧 Configuração Avançada

### Parâmetros de Extração

A API suporta todos os parâmetros do LangExtract:

```json
{
  "text": "Texto para processar",
  "prompt_description": "Descrição da tarefa",
  "examples": [{"input": "exemplo", "output": {"resultado": "esperado"}}],
  "model_id": "gemma2:2b",
  "temperature": 0.1,
  "max_char_buffer": 10000,
  "max_workers": 4,
  "batch_length": 1000,
  "extraction_passes": 1,
  "format_type": "json",
  "additional_context": "Contexto adicional",
  "debug": false
}
```

### Configuração de Modelos

#### Gemini
```json
{
  "model_id": "gemini-2.0-flash-exp",
  "api_key": "sua-chave-gemini",
  "temperature": 0.1
}
```

#### OpenAI
```json
{
  "model_id": "gpt-4",
  "api_key": "sua-chave-openai",
  "temperature": 0.1
}
```

#### Ollama (Local)
```json
{
  "model_id": "gemma2:2b",
  "model_url": "http://localhost:11434",
  "temperature": 0.1
}
```

## 🐳 Docker

### Serviços Disponíveis

- **langextract-api**: API principal (porta 8000)
- **ollama**: Servidor Ollama local (porta 11434)

### Comandos Úteis

```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f langextract-api
docker-compose logs -f ollama

# Parar serviços
docker-compose down

# Rebuild
docker-compose up --build

# Executar comando na API
docker-compose exec langextract-api python -c "import langextract; print('OK')"
```

### Volumes

- `uploads/`: Arquivos enviados
- `outputs/`: Resultados das extrações
- `logs/`: Logs da aplicação
- `ollama_data/`: Dados do Ollama

## 📊 Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "langextract": "available",
    "ollama": "available"
  }
}
```

### Logs Estruturados

Os logs são estruturados em JSON para facilitar análise:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "event": "extraction_started",
  "extraction_id": "ext_123",
  "model_id": "gemma2:2b",
  "text_length": 1500
}
```

## 🔒 Segurança

### Produção

1. **Altere senhas padrão**:
   ```env
   API_SECRET_KEY=chave-muito-segura-e-aleatoria
   ```

2. **Configure CORS**:
   ```env
   CORS_ORIGINS=https://seu-dominio.com,https://app.seu-dominio.com
   ```

3. **Use HTTPS**:
   - Configure proxy reverso (nginx, traefik)
   - Certificados SSL/TLS

4. **Limite rate limiting**:
   ```env
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=3600
   ```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verifique se o token está válido
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/auth/verify
```

#### 2. Modelo Não Encontrado
```bash
# Liste modelos disponíveis
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/models
```

#### 3. Ollama Não Conecta
```bash
# Verifique se o Ollama está rodando
docker-compose logs ollama

# Teste conexão direta
curl http://localhost:11434/api/tags
```

#### 4. Erro de Upload
```bash
# Verifique tamanho do arquivo (limite: 50MB)
# Verifique formato suportado: .txt, .md, .json, .pdf, .docx
```

### Logs de Debug

Para debug detalhado, configure:

```env
LOG_LEVEL=DEBUG
DEBUG=true
```

## 📈 Performance

### Recomendações

1. **Para textos longos**:
   - Use `max_char_buffer` apropriado
   - Configure `max_workers` baseado no CPU
   - Use `batch_length` para dividir processamento

2. **Para alta concorrência**:
   - Aumente workers do uvicorn
   - Configure pool de conexões
   - Use cache Redis (opcional)

3. **Modelos locais (Ollama)**:
   - Requer GPU para melhor performance
   - Configure memória adequada
   - Use modelos menores para testes

## 🤝 Contribuição

1. Fork o repositório
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📄 Licença

Este projeto segue a mesma licença do LangExtract original.

## 🆘 Suporte

- **Issues**: https://github.com/google/langextract/issues
- **Documentação**: http://localhost:8000/docs
- **Logs**: `docker-compose logs -f langextract-api`

---

**Desenvolvido com ❤️ usando FastAPI e LangExtract**