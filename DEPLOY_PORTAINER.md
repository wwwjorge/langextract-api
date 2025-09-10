# Deploy LangExtract API no Portainer

Guia completo para fazer deploy da LangExtract API no Portainer com exposição via Cloudflare Tunnels.

## 📋 Pré-requisitos

- Portainer instalado e funcionando
- Docker e Docker Compose disponíveis no host
- Chave de API do Google Gemini
- Cloudflare Tunnel configurado (opcional)

## 🚀 Opções de Deploy

### Opção 1: Stack Completa (com Ollama)
**Arquivo:** `docker-compose.portainer.yml`
- Inclui Ollama para modelos locais
- Maior consumo de recursos (~2GB RAM + modelos)
- Flexibilidade total de provedores LLM

### Opção 2: Stack Lite (apenas API)
**Arquivo:** `docker-compose.portainer-lite.yml`
- Apenas a API LangExtract
- Menor consumo de recursos (~500MB RAM)
- Usa apenas provedores externos (Gemini, OpenAI)

## 📝 Passo a Passo

### 1. Preparar Variáveis de Ambiente

1. Abra o arquivo `.env.portainer`
2. **OBRIGATÓRIO:** Substitua os seguintes valores:
   ```env
   GEMINI_API_KEY=sua_chave_gemini_aqui
   API_SECRET_KEY=uma_chave_secreta_forte_minimo_32_caracteres
   ```
3. Ajuste outras configurações conforme necessário:
   - `LANGEXTRACT_API_PORT`: Porta da API (padrão: 8000)
   - `MAX_FILE_SIZE_MB`: Tamanho máximo de arquivo
   - `MAX_WORKERS`: Workers para processamento paralelo

### 2. Deploy no Portainer

#### 2.1 Acessar Portainer
1. Acesse sua instância do Portainer
2. Vá para **Stacks** → **Add stack**

#### 2.2 Configurar Stack
1. **Name:** `langextract-api`
2. **Build method:** `Web editor`
3. **Web editor:** Cole o conteúdo de um dos arquivos:
   - `docker-compose.portainer.yml` (stack completa)
   - `docker-compose.portainer-lite.yml` (stack lite)

#### 2.3 Configurar Variáveis de Ambiente
1. Na seção **Environment variables**
2. Cole todo o conteúdo do arquivo `.env.portainer`
3. **IMPORTANTE:** Ajuste os valores das chaves de API

#### 2.4 Deploy
1. Clique em **Deploy the stack**
2. Aguarde o build e inicialização dos containers

### 3. Verificar Deploy

#### 3.1 Status dos Containers
1. Vá para **Containers**
2. Verifique se os containers estão **running**:
   - `langextract-api_langextract-api_1`
   - `langextract-api_ollama_1` (se usar stack completa)

#### 3.2 Health Check
1. Acesse: `http://localhost:8000/health`
2. Deve retornar: `{"status": "healthy"}`

#### 3.3 API Documentation
1. Swagger UI: `http://localhost:8000/docs`
2. ReDoc: `http://localhost:8000/redoc`

## 🌐 Configurar Cloudflare Tunnel

### 1. Instalar cloudflared
```bash
# Windows
winget install --id Cloudflare.cloudflared

# Linux/Mac
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

### 2. Autenticar
```bash
cloudflared tunnel login
```

### 3. Criar Tunnel
```bash
# Criar tunnel
cloudflared tunnel create langextract-api

# Criar arquivo de configuração
echo "tunnel: <TUNNEL-ID>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: langextract.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404" > config.yml

# Configurar DNS
cloudflared tunnel route dns <TUNNEL-ID> langextract.yourdomain.com

# Executar tunnel
cloudflared tunnel run langextract-api
```

## 🔧 Configurações Avançadas

### Volumes Persistentes
Os seguintes volumes são criados automaticamente:
- `langextract-uploads`: Arquivos enviados
- `langextract-outputs`: Resultados de extração
- `langextract-logs`: Logs da aplicação
- `ollama-data`: Modelos Ollama (apenas stack completa)

### Backup dos Volumes
```bash
# Backup uploads
docker run --rm -v langextract-api_langextract-uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# Backup outputs
docker run --rm -v langextract-api_langextract-outputs:/data -v $(pwd):/backup alpine tar czf /backup/outputs-backup.tar.gz -C /data .
```

### Monitoramento
```bash
# Logs da API
docker logs -f langextract-api_langextract-api_1

# Logs do Ollama (se aplicável)
docker logs -f langextract-api_ollama_1

# Status dos containers
docker ps
```

## 🔐 Segurança

### Produção
1. **Gere uma chave JWT forte:**
   ```bash
   openssl rand -hex 32
   ```

2. **Configure CORS adequadamente:**
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

3. **Use HTTPS sempre em produção**

4. **Monitore logs regularmente**

## 🚨 Troubleshooting

### Container não inicia
1. Verifique logs: `docker logs <container-name>`
2. Verifique variáveis de ambiente
3. Verifique se as portas não estão em uso

### API não responde
1. Verifique health check: `/health`
2. Verifique logs da aplicação
3. Verifique conectividade de rede

### Erro de autenticação
1. Verifique `API_SECRET_KEY`
2. Verifique se o token não expirou
3. Gere novo token via `/auth/token`

### Erro com Gemini
1. Verifique `GEMINI_API_KEY`
2. Verifique cotas da API
3. Teste conectividade com a API do Google

## 📊 Recursos Recomendados

### Stack Lite
- **CPU:** 2 cores
- **RAM:** 1GB mínimo, 2GB recomendado
- **Disco:** 10GB para volumes

### Stack Completa
- **CPU:** 4 cores
- **RAM:** 4GB mínimo, 8GB recomendado
- **Disco:** 50GB para volumes e modelos

## 🔄 Atualizações

### Atualizar Stack
1. No Portainer, vá para a stack
2. Clique em **Editor**
3. Atualize o docker-compose se necessário
4. Clique em **Update the stack**

### Rebuild Containers
```bash
# Via Portainer: Recreate containers
# Via CLI:
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs dos containers
2. Consulte a documentação da API
3. Verifique as configurações de rede
4. Teste as chaves de API externamente