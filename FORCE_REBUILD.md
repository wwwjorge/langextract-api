# 🔄 Forçar Rebuild Completo - Resolver Erros de Dependências

## 🚨 Problema
Após as correções de código, os erros persistem porque o Docker está usando cache de layers antigas com dependências desatualizadas.

## ✅ Solução: Rebuild Forçado

### Opção 1: Via Portainer (Recomendado)
1. **Deletar Stack Completamente:**
   - Vá para **Stacks** → **langextract-api**
   - Clique em **"Delete this stack"**
   - ✅ Marque **"Remove associated volumes"** (se quiser limpar dados)
   - Confirme a exclusão

2. **Recriar Stack com Build Forçado:**
   - **Add stack** → **Repository**
   - **Name:** `langextract-api`
   - **Repository URL:** `https://github.com/wwwjorge/langextract-api.git`
   - **Reference:** `refs/heads/main`
   - **Compose path:** `docker-compose.portainer-simple.yml`
   - ⚠️ **IMPORTANTE:** Na seção **"Advanced mode"**
   - Adicione: `--no-cache --pull` nos build args
   - **Deploy the stack**

### Opção 2: Via Docker CLI (Se tiver acesso SSH)
```bash
# Parar e remover containers
docker-compose -f docker-compose.portainer-simple.yml down --volumes

# Remover imagens antigas
docker rmi $(docker images -q langextract*)

# Limpar cache do Docker
docker builder prune -a -f

# Rebuild forçado sem cache
docker-compose -f docker-compose.portainer-simple.yml build --no-cache --pull

# Subir novamente
docker-compose -f docker-compose.portainer-simple.yml up -d
```

### Opção 3: Modificar docker-compose Temporariamente
Adicione no `docker-compose.portainer-simple.yml`:
```yaml
services:
  langextract-api:
    build:
      context: .
      dockerfile: Dockerfile.api
      args:
        - BUILDKIT_INLINE_CACHE=0
      no_cache: true  # Força rebuild
```

## 🔍 Verificar se Funcionou
Após o rebuild, os logs devem mostrar:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

**SEM os erros:**
- ❌ `PydanticImportError: BaseSettings has been moved`
- ❌ `UserWarning: Field "model_id" has conflict`
- ❌ `error reading bcrypt version`
- ❌ `AttributeError: module 'bcrypt' has no attribute '__about__'`

## 🎯 Por que Isso Acontece?
- Docker usa cache de layers para acelerar builds
- Quando mudamos `requirements.txt`, o cache pode não detectar
- `--no-cache` força download e instalação de todas as dependências
- `--pull` garante que a imagem base Python seja a mais recente

## ✅ Resultado Esperado
Após o rebuild forçado:
- ✅ API inicia sem erros
- ✅ Dependências atualizadas (`pydantic-settings`, `bcrypt`)
- ✅ Configurações do Pydantic v2 funcionando
- ✅ `/health` endpoint respondendo normalmente