# 🚀 Deploy LangExtract API via GitHub no Portainer

## 📋 Pré-requisitos
- Portainer instalado e configurado
- Acesso ao repositório: `https://github.com/wwwjorge/langextract-api.git`
- Docker funcionando no host do Portainer

---

## 🎯 Passos para Deploy

### 1. Acessar Portainer
1. Abra o Portainer no seu navegador
2. Faça login com suas credenciais
3. Selecione o environment Docker desejado

### 2. Criar Nova Stack
1. No menu lateral, clique em **"Stacks"**
2. Clique no botão **"Add stack"**
3. Preencha os campos:

#### Configurações Básicas
- **Name:** `langextract-api`
- **Build method:** Selecione **"Repository"**

#### Configurações do Repositório
- **Repository URL:** `https://github.com/wwwjorge/langextract-api.git`
- **Reference:** `refs/heads/main`
- **Compose path:** `docker-compose.portainer-simple.yml` (recomendado) ou `docker-compose.portainer-lite.yml`
- **Additional paths:** (deixe vazio)

### 3. Configurar Variáveis de Ambiente
Na seção **"Environment variables"**, adicione:

```env
# API Configuration
LANGEXTRACT_API_PORT=8000
LANGEXTRACT_API_KEY=sua-api-key-aqui

# AI Provider Keys
GEMINI_API_KEY=sua-gemini-key
OPENAI_API_KEY=sua-openai-key

# Security
API_SECRET_KEY=sua-secret-key-jwt
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Settings
DEFAULT_MODEL=gemini-1.5-flash
DEFAULT_PROVIDER=gemini
MAX_FILE_SIZE_MB=50
MAX_WORKERS=4
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### 4. Deploy da Stack
1. Revise todas as configurações
2. Clique em **"Deploy the stack"**
3. Aguarde o build e deploy (pode levar alguns minutos)

---

## 🔍 Verificar Deploy

### 1. Status da Stack
- Vá para **Stacks** → **langextract-api**
- Verifique se o status está **"Running"**
- Todos os containers devem estar **"healthy"**

### 2. Logs dos Containers
- Clique no container **langextract-api**
- Vá para a aba **"Logs"**
- Procure por mensagens como:
  ```
  INFO: Uvicorn running on http://0.0.0.0:8000
  INFO: Application startup complete
  ```

### 3. Testar API
Acesse no navegador:
- **Health Check:** `http://seu-host:8000/health`
- **Documentação:** `http://seu-host:8000/docs`
- **Redoc:** `http://seu-host:8000/redoc`

---

## 🔧 Configurações Avançadas

### Personalizar Porta
Para usar uma porta diferente:
1. Altere `LANGEXTRACT_API_PORT=8080` nas variáveis de ambiente
2. Redeploy a stack

### Adicionar Domínio Personalizado
1. Configure um reverse proxy (Nginx, Traefik)
2. Aponte para `http://langextract-api:8000`
3. Configure SSL se necessário

### Backup e Persistência
Os volumes são automaticamente criados:
- `langextract-uploads`: Arquivos enviados
- `langextract-outputs`: Resultados processados
- `langextract-logs`: Logs da aplicação

---

## 🚨 Troubleshooting

### ❌ Erro de Rede: "Pool overlaps with other one"
**Solução Rápida:** Use `docker-compose.portainer-simple.yml` como Compose path.

### Outros Problemas Comuns
- **Erro de Build:** Verificar se o repositório é público e `Dockerfile.api` existe
- **Container não Inicia:** Verificar logs e variáveis obrigatórias
- **API não Responde:** Testar `http://SEU_HOST:8000/health`

### 📋 Guia Completo de Troubleshooting
Para problemas detalhados e soluções específicas, consulte:
**[TROUBLESHOOTING_PORTAINER.md](./TROUBLESHOOTING_PORTAINER.md)**

---

## 🔄 Atualizações

### Atualizar Código
1. Faça push das alterações para o repositório GitHub
2. No Portainer, vá para **Stacks** → **langextract-api**
3. Clique em **"Update the stack"**
4. Selecione **"Re-pull image and redeploy"**
5. Clique em **"Update"**

### Rollback
1. No GitHub, reverta o commit problemático
2. Siga os passos de atualização acima

---

## 📊 Monitoramento

### Métricas Importantes
- **CPU Usage:** < 80%
- **Memory Usage:** < 2GB
- **Response Time:** < 2s
- **Error Rate:** < 1%

### Logs para Monitorar
```bash
# Acessar logs via Portainer CLI
docker logs langextract-api_langextract-api_1 -f

# Ou via Portainer Web UI
# Stacks → langextract-api → Containers → langextract-api → Logs
```

---

## 🎯 Próximos Passos

1. **Configurar Monitoramento:** Prometheus + Grafana
2. **Implementar CI/CD:** GitHub Actions
3. **Configurar Backup:** Volumes automáticos
4. **SSL/TLS:** Certificados Let's Encrypt
5. **Scaling:** Multiple replicas se necessário

---

## 📞 Suporte

- **Repositório:** https://github.com/wwwjorge/langextract-api
- **Issues:** https://github.com/wwwjorge/langextract-api/issues
- **Documentação API:** `http://seu-host:8000/docs`