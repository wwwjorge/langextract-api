# 🚨 Troubleshooting: Problemas Comuns no Portainer

## ❌ Erro: "Pool overlaps with other one on this address space"

### 🔍 Problema
```
failed to create network langextract-api_langextract-network: 
Error response from daemon: invalid pool request: 
Pool overlaps with other one on this address space
```

### 💡 Causa
O subnet `172.20.0.0/16` já está sendo usado por outra rede Docker no sistema.

### ✅ Soluções

#### Solução 1: Usar Compose Simples (Recomendado)
1. No Portainer, altere o **Compose path** para:
   ```
   docker-compose.portainer-simple.yml
   ```
2. Este arquivo não define rede customizada, evitando conflitos
3. Redeploy a stack

#### Solução 2: Alterar Subnet
1. Use o arquivo original: `docker-compose.portainer-lite.yml`
2. O subnet foi alterado para `172.25.0.0/16`
3. Se ainda houver conflito, tente outros ranges:
   - `172.30.0.0/16`
   - `172.35.0.0/16`
   - `10.10.0.0/16`

#### Solução 3: Remover Redes Conflitantes
```bash
# Listar redes Docker
docker network ls

# Remover rede específica (se não estiver em uso)
docker network rm nome-da-rede

# Limpar redes não utilizadas
docker network prune
```

---

## ❌ Erro: "Build context is empty"

### 🔍 Problema
```
failed to build: build context is empty
```

### 💡 Causa
O repositório não foi clonado corretamente ou está vazio.

### ✅ Soluções
1. Verificar se a URL do repositório está correta:
   ```
   https://github.com/wwwjorge/langextract-api.git
   ```
2. Confirmar que o repositório é público
3. Verificar se o branch `main` existe
4. Tentar usar `refs/heads/main` como referência

---

## ❌ Erro: "No such file: Dockerfile.api"

### 🔍 Problema
```
failed to build: unable to prepare context: unable to evaluate symlinks in Dockerfile path: 
lstat Dockerfile.api: no such file or directory
```

### 💡 Causa
O arquivo `Dockerfile.api` não foi encontrado no repositório.

### ✅ Soluções
1. Verificar se o arquivo existe no repositório GitHub
2. Confirmar que está na raiz do projeto
3. Verificar se o nome está correto (case-sensitive)

---

## ❌ Erro: "Cannot connect to Docker daemon"

### 🔍 Problema
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

### 💡 Causa
O Docker não está rodando no host do Portainer.

### ✅ Soluções
1. Verificar status do Docker:
   ```bash
   sudo systemctl status docker
   ```
2. Iniciar Docker se necessário:
   ```bash
   sudo systemctl start docker
   ```
3. Verificar permissões do usuário

---

## ❌ Container não Inicia

### 🔍 Sintomas
- Container fica em estado "Exited"
- Status "Unhealthy"
- Restart contínuo

### ✅ Diagnóstico
1. Verificar logs do container:
   - Portainer → Stacks → langextract-api → Containers → Logs

2. Verificar variáveis de ambiente obrigatórias:
   ```env
   LANGEXTRACT_API_KEY=sua-chave
   API_SECRET_KEY=sua-chave-jwt
   GEMINI_API_KEY=sua-gemini-key  # ou OPENAI_API_KEY
   ```

3. Testar chaves de API:
   ```bash
   # Teste Gemini
   curl -H "Authorization: Bearer SUA_GEMINI_KEY" \
        https://generativelanguage.googleapis.com/v1/models
   
   # Teste OpenAI
   curl -H "Authorization: Bearer SUA_OPENAI_KEY" \
        https://api.openai.com/v1/models
   ```

---

## ❌ API não Responde

### 🔍 Sintomas
- Timeout ao acessar endpoints
- Erro 502 Bad Gateway
- Conexão recusada

### ✅ Soluções
1. Verificar se o container está "Running" e "Healthy"
2. Testar conectividade interna:
   ```bash
   # Dentro do container
   curl http://localhost:8000/health
   ```
3. Verificar mapeamento de portas:
   - Container: porta 8000
   - Host: porta definida em `LANGEXTRACT_API_PORT`
4. Verificar firewall do host

---

## ❌ Erro de Permissões

### 🔍 Problema
```
Permission denied: '/app/uploads'
Permission denied: '/app/logs'
```

### ✅ Soluções
1. Verificar permissões dos volumes:
   ```bash
   docker volume inspect langextract-api_langextract-uploads
   ```
2. Ajustar permissões se necessário:
   ```bash
   sudo chown -R 1000:1000 /var/lib/docker/volumes/langextract-api_*
   ```

---

## 🔧 Comandos Úteis para Diagnóstico

### Verificar Redes Docker
```bash
# Listar todas as redes
docker network ls

# Inspecionar rede específica
docker network inspect bridge

# Ver conflitos de subnet
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
```

### Verificar Volumes
```bash
# Listar volumes
docker volume ls

# Inspecionar volume
docker volume inspect langextract-api_langextract-uploads
```

### Logs Detalhados
```bash
# Logs do container
docker logs langextract-api_langextract-api_1 -f

# Logs com timestamp
docker logs langextract-api_langextract-api_1 -t
```

---

## 📋 Checklist de Verificação

### Antes do Deploy
- [ ] Repositório GitHub é público e acessível
- [ ] Arquivo `Dockerfile.api` existe na raiz
- [ ] Arquivo `docker-compose.portainer-*.yml` existe
- [ ] Todas as variáveis obrigatórias estão definidas
- [ ] Chaves de API são válidas

### Durante o Deploy
- [ ] Build logs não mostram erros
- [ ] Container inicia sem erros
- [ ] Health check passa
- [ ] Volumes são criados corretamente

### Após o Deploy
- [ ] `/health` retorna status 200
- [ ] `/docs` carrega a documentação
- [ ] API responde a requisições de teste
- [ ] Logs não mostram erros críticos

---

## 🆘 Suporte Adicional

### Arquivos de Configuração Alternativos
- `docker-compose.portainer-simple.yml` - Sem rede customizada
- `docker-compose.portainer-lite.yml` - Com rede customizada
- `.env.github-portainer` - Template de variáveis

### Links Úteis
- **Repositório:** https://github.com/wwwjorge/langextract-api
- **Issues:** https://github.com/wwwjorge/langextract-api/issues
- **Docker Networks:** https://docs.docker.com/network/
- **Portainer Docs:** https://docs.portainer.io/

### Contato
Se o problema persistir, abra uma issue no repositório com:
1. Logs completos do erro
2. Configuração utilizada
3. Versão do Docker e Portainer
4. Sistema operacional do host