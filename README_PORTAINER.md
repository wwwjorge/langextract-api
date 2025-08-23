# 🐳 LangExtract API - Deploy no Portainer

Guia rápido para deploy da LangExtract API no Portainer com exposição via Cloudflare Tunnels.

## 📁 Arquivos para Deploy

### Stack Completa (com Ollama)
- `docker-compose.portainer.yml` - Compose com API + Ollama
- `.env.portainer` - Variáveis de ambiente completas
- **Recursos:** ~4GB RAM, 50GB disco

### Stack Lite (apenas API) ⭐ **Recomendado**
- `docker-compose.portainer-lite.yml` - Compose apenas com API
- `.env.portainer-lite` - Variáveis de ambiente simplificadas
- **Recursos:** ~1GB RAM, 10GB disco

## 🚀 Deploy Rápido (Stack Lite)

### 1. Configurar Variáveis
Edite `.env.portainer-lite` e substitua:
```env
GEMINI_API_KEY=sua_chave_gemini_aqui
API_SECRET_KEY=uma_chave_secreta_forte_32_chars
LANGEXTRACT_API_PORT=8000
```

### 2. Deploy no Portainer
1. **Stacks** → **Add stack**
2. **Name:** `langextract-api`
3. **Web editor:** Cole conteúdo de `docker-compose.portainer-lite.yml`
4. **Environment variables:** Cole conteúdo de `.env.portainer-lite`
5. **Deploy the stack**

### 3. Verificar
- Health: `http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`
- Validação: `python validate_portainer_deploy.py`

## 🌐 Cloudflare Tunnel

```bash
# Criar tunnel
cloudflared tunnel create langextract

# Configurar DNS
cloudflared tunnel route dns <TUNNEL-ID> api.seudominio.com

# Executar
cloudflared tunnel run --url http://localhost:8000 langextract
```

## 📊 Volumes Criados

- `langextract-uploads` - Arquivos enviados
- `langextract-outputs` - Resultados processados
- `langextract-logs` - Logs da aplicação
- `ollama-data` - Modelos Ollama (apenas stack completa)

## 🔧 Configurações Importantes

### Portas
- `LANGEXTRACT_API_PORT=8000` - API principal
- `OLLAMA_PORT=11434` - Ollama (apenas stack completa)

### Segurança
- Gere `API_SECRET_KEY` forte: `openssl rand -hex 32`
- Configure `CORS_ORIGINS` para produção
- Use HTTPS em produção

### Performance
- `MAX_WORKERS=4` - Workers paralelos
- `MAX_FILE_SIZE_MB=100` - Tamanho máximo de arquivo

## 🚨 Troubleshooting

### Container não inicia
```bash
docker logs langextract-api_langextract-api_1
```

### API não responde
1. Verificar health: `/health`
2. Verificar logs
3. Verificar variáveis de ambiente

### Erro Gemini
1. Verificar `GEMINI_API_KEY`
2. Testar chave: `curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models`

## 📝 Uso da API

### 1. Autenticar
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -d "username=admin&password=admin"
```

### 2. Extrair Texto
```bash
curl -X POST "http://localhost:8000/extract/text" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "João Silva trabalha na empresa XYZ",
    "schema": {
      "type": "object",
      "properties": {
        "nome": {"type": "string"},
        "empresa": {"type": "string"}
      }
    }
  }'
```

## 🔄 Backup e Restore

### Backup
```bash
# Backup uploads
docker run --rm -v langextract-api_langextract-uploads:/data \
  -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /data .

# Backup outputs
docker run --rm -v langextract-api_langextract-outputs:/data \
  -v $(pwd):/backup alpine tar czf /backup/outputs.tar.gz -C /data .
```

### Restore
```bash
# Restore uploads
docker run --rm -v langextract-api_langextract-uploads:/data \
  -v $(pwd):/backup alpine tar xzf /backup/uploads.tar.gz -C /data
```

## 📈 Monitoramento

### Métricas
- CPU/RAM: Portainer Dashboard
- Logs: `docker logs -f <container>`
- Health: `curl http://localhost:8000/health`

### Alertas
- Configure alertas no Portainer
- Monitore uso de disco dos volumes
- Monitore logs de erro

---

## 🎯 Checklist de Deploy

- [ ] Chave Gemini configurada
- [ ] API_SECRET_KEY gerada
- [ ] Portas configuradas
- [ ] Stack deployada no Portainer
- [ ] Health check funcionando
- [ ] Autenticação testada
- [ ] Extração testada
- [ ] Cloudflare Tunnel configurado
- [ ] Backup configurado
- [ ] Monitoramento ativo

**✅ Deploy concluído com sucesso!**