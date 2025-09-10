# Solução para Problemas de Cache Persistente

Os erros que você está enfrentando são causados por **cache persistente do Docker** que mantém versões antigas das dependências, mesmo após tentativas de rebuild.

## 🔍 Problemas Identificados

1. **PydanticImportError**: Cache mantém importação antiga `from pydantic import BaseSettings`
2. **bcrypt AttributeError**: Incompatibilidade entre versões de `passlib` e `bcrypt` em cache
3. **Warnings de namespace**: Cache de modelos Pydantic antigos

## ✅ Correções Aplicadas no Código

- ✅ Corrigido `requirements.api.txt` com versões compatíveis:
  - `passlib[bcrypt]==1.7.4`
  - `bcrypt==4.1.1`
- ✅ Importações corretas já estão no código:
  - `from pydantic_settings import BaseSettings`
- ✅ Configuração de namespace já está definida nos modelos

## 🚀 Solução Definitiva

### Opção 1: Script Automático (Recomendado)

1. Execute o script de limpeza:
   ```powershell
   .\clean_docker_cache.ps1
   ```

2. No Portainer, delete a stack atual completamente

3. Crie uma nova stack com o arquivo `docker-compose.portainer-nocache.yml`

### Opção 2: Limpeza Manual

1. **Pare e remova todos os containers:**
   ```bash
   docker stop $(docker ps -aq --filter "name=langextract")
   docker rm $(docker ps -aq --filter "name=langextract")
   ```

2. **Remova todas as imagens:**
   ```bash
   docker rmi $(docker images -q --filter "reference=*langextract*") --force
   ```

3. **Limpe o cache de build:**
   ```bash
   docker builder prune --all --force
   docker system prune --all --force
   ```

4. **No Portainer:**
   - Delete a stack atual
   - Crie nova stack com `docker-compose.portainer-nocache.yml`
   - Use as variáveis de ambiente do `.env.portainer`

### Opção 3: Rebuild Forçado no Portainer

1. **Configuração da Stack:**
   - Nome: `langextract-api-clean`
   - Arquivo: `docker-compose.portainer-nocache.yml`
   - Variáveis de ambiente do `.env.portainer`

2. **Modo Avançado (se disponível):**
   - Build arguments: `--no-cache --pull`
   - Environment variables: `DOCKER_BUILDKIT=1`

## 🔧 Verificação do Sucesso

Após o rebuild, os logs devem mostrar:
- ✅ Sem erros de `PydanticImportError`
- ✅ Sem erros de `bcrypt.__about__`
- ✅ Sem erros de `SpawnProcess`
- ✅ API iniciando normalmente em `http://0.0.0.0:8000`

## 📝 Notas Importantes

- O problema **NÃO** está no código-fonte
- O problema **É** o cache do Docker mantendo dependências antigas
- A limpeza completa do cache é **ESSENCIAL**
- Use sempre `docker-compose.portainer-nocache.yml` para evitar cache

## 🆘 Se o Problema Persistir

1. Verifique se todas as imagens foram removidas:
   ```bash
   docker images | grep langextract
   ```

2. Verifique se não há containers rodando:
   ```bash
   docker ps -a | grep langextract
   ```

3. Limpe o cache do sistema operacional:
   ```bash
   docker system df
   docker system prune --all --volumes --force
   ```

Esta solução deve resolver definitivamente os problemas de cache persistente.