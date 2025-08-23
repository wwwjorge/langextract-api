# 🚀 Quick Start: Deploy LangExtract API no Portainer via GitHub

## ⚡ Deploy em 5 Minutos

### 1️⃣ Acesse o Portainer
- URL: `http://seu-portainer:9000`
- Login com suas credenciais

### 2️⃣ Criar Stack
1. **Stacks** → **Add stack**
2. **Name:** `langextract-api`
3. **Build method:** **Repository**
4. **Repository URL:** `https://github.com/wwwjorge/langextract-api.git`
5. **Reference:** `refs/heads/main`
6. **Compose path:** `docker-compose.portainer-lite.yml`

### 3️⃣ Variáveis de Ambiente (Mínimas)
```env
LANGEXTRACT_API_PORT=8000
LANGEXTRACT_API_KEY=sua-api-key-aqui
GEMINI_API_KEY=sua-gemini-key
API_SECRET_KEY=sua-chave-jwt-super-secreta
```

### 4️⃣ Deploy
- Clique **"Deploy the stack"**
- Aguarde 2-3 minutos

### 5️⃣ Testar
- **Health:** `http://seu-host:8000/health`
- **Docs:** `http://seu-host:8000/docs`

---

## 📁 Arquivos Importantes

| Arquivo | Descrição |
|---------|----------|
| `DEPLOY_GITHUB_PORTAINER.md` | 📖 Guia completo de deploy |
| `.env.github-portainer` | 🔧 Template de variáveis |
| `PORTAINER_BUILD_GUIDE.md` | 📋 Guia geral do Portainer |
| `docker-compose.portainer-lite.yml` | 🐳 Configuração Docker |

---

## 🔑 Onde Obter as Chaves

- **Gemini API:** https://makersuite.google.com/app/apikey
- **OpenAI API:** https://platform.openai.com/api-keys
- **JWT Secret:** `openssl rand -hex 32`
- **API Key:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## 🆘 Problemas Comuns

### ❌ Build Falha
**Solução:** Verificar se o repositório está público e acessível

### ❌ Container não Inicia
**Solução:** Verificar se todas as variáveis obrigatórias estão definidas

### ❌ API não Responde
**Solução:** Verificar logs do container e porta configurada

---

## 📞 Suporte

- **Repositório:** https://github.com/wwwjorge/langextract-api
- **Issues:** https://github.com/wwwjorge/langextract-api/issues
- **Documentação:** Acesse `/docs` após deploy

---

## 🎯 Próximos Passos

1. ✅ Deploy básico funcionando
2. 🔒 Configurar SSL/HTTPS
3. 📊 Adicionar monitoramento
4. 🔄 Configurar CI/CD
5. 📦 Backup automático

**Sucesso!** 🎉 Sua API está rodando no Portainer via GitHub!