# 📦 Deploy via ZIP no Portainer - Guia Completo

## 🤔 Por que preciso de um ZIP?

Quando você usa **build context** no Docker Compose (como `build: .`), o Portainer precisa ter acesso ao código fonte da aplicação para construir a imagem Docker. Existem algumas formas de fazer isso:

### 📋 Opções de Deploy no Portainer:

1. **🔗 Git Repository** (Recomendado para produção)
   - Portainer clona diretamente do GitHub/GitLab
   - Atualizações automáticas
   - Controle de versão

2. **📦 Upload ZIP** (Ideal para desenvolvimento/teste)
   - Upload manual do código
   - Controle total sobre o que é enviado
   - Funciona offline

3. **🐳 Imagem Pré-construída** (Para produção avançada)
   - Imagem já buildada no Docker Hub/Registry
   - Deploy mais rápido
   - Requer CI/CD pipeline

## 🎯 Quando usar ZIP?

✅ **Use ZIP quando:**
- Está testando localmente
- Não quer expor o código no Git público
- Precisa de controle total sobre arquivos enviados
- Está desenvolvendo e fazendo mudanças frequentes
- Portainer está em WSL2/Docker Desktop

❌ **Não use ZIP quando:**
- Está em produção (prefira Git)
- Tem pipeline CI/CD configurado
- Quer atualizações automáticas

## 🛠️ Como Criar o ZIP

### Para Windows (PowerShell):
```powershell
# Navegar até a pasta do projeto
cd "f:\Secondbrain\BrainServer\CodeServer\lagexstract"

# Executar o script
.\create_deploy_zip.ps1

# Ou com mais detalhes:
.\create_deploy_zip.ps1 -Verbose
```

### Para Linux/WSL2 (Bash):
```bash
# Navegar até a pasta do projeto
cd /mnt/f/Secondbrain/BrainServer/CodeServer/lagexstract

# Dar permissão e executar
chmod +x create_deploy_zip.sh
./create_deploy_zip.sh
```

## 📁 O que vai no ZIP?

### ✅ Arquivos Incluídos:
- `Dockerfile.api` - Receita para construir a imagem
- `docker-compose.portainer-lite.yml` - Configuração dos serviços
- `.env.portainer-lite` - Variáveis de ambiente
- `requirements.api.txt` - Dependências Python
- `api/` - Todo o código da aplicação
- Outros arquivos necessários

### ❌ Arquivos Excluídos:
- `.git/` - Histórico do Git (desnecessário)
- `__pycache__/` - Cache Python
- `venv/`, `.venv/` - Ambiente virtual
- `uploads/`, `outputs/`, `logs/` - Dados temporários
- `node_modules/` - Dependências Node.js
- Arquivos temporários (*.tmp, *.log)

## 🚀 Deploy no Portainer

### Passo a Passo:

1. **Acessar Portainer**
   ```
   http://localhost:9000
   ```

2. **Criar Nova Stack**
   - Ir em `Stacks` → `Add stack`
   - Nome: `langextract-api`

3. **Configurar Build Method**
   - Selecionar: `📦 Upload`
   - Upload do arquivo ZIP criado

4. **Configurar Compose File**
   - Compose path: `docker-compose.portainer-lite.yml`
   - Ou copiar o conteúdo do arquivo

5. **Variáveis de Ambiente**
   ```env
   # Copiar do arquivo .env.portainer-lite
   LANGEXTRACT_API_PORT=8000
   GEMINI_API_KEY=sua_chave_aqui
   API_SECRET_KEY=sua_chave_secreta_aqui
   # ... outras variáveis
   ```

6. **Deploy**
   - Clicar em `Deploy the stack`
   - Aguardar o build e inicialização

## 🔧 Portainer em WSL2

### Cenário Comum:
- **Windows Host**: Seus arquivos estão em `f:\Secondbrain\...`
- **WSL2**: Portainer roda em `http://localhost:9000`
- **Docker**: Containers rodam no WSL2

### Como Funciona:
1. **Você cria o ZIP** no Windows ou WSL2
2. **Upload via browser** para o Portainer
3. **Portainer extrai** o ZIP no ambiente WSL2
4. **Docker build** acontece no WSL2
5. **Container roda** no WSL2
6. **Acesso via porta** mapeada para Windows

### Dicas para WSL2:
```bash
# Acessar arquivos Windows do WSL2
cd /mnt/f/Secondbrain/BrainServer/CodeServer/lagexstract

# Verificar se Docker está rodando
docker ps

# Verificar se Portainer está acessível
curl http://localhost:9000
```

## 🔍 Verificação do Deploy

### 1. Verificar Stack no Portainer:
- Status: `Running`
- Containers: `langextract-api` ativo
- Logs: Sem erros críticos

### 2. Testar API:
```bash
# Health check
curl http://localhost:8000/health

# Documentação
open http://localhost:8000/docs
```

### 3. Usar Script de Validação:
```bash
python validate_portainer_deploy.py
```

## 🔄 Atualizações

### Para Atualizar a Aplicação:
1. **Modificar código** localmente
2. **Criar novo ZIP** com script
3. **Parar stack** no Portainer
4. **Upload novo ZIP**
5. **Redeploy stack**

### Comando Rápido:
```powershell
# Parar, atualizar e reiniciar
.\create_deploy_zip.ps1
# Depois fazer upload manual no Portainer
```

## 🐛 Troubleshooting

### ❌ "Build context not found"
**Problema**: Portainer não encontra os arquivos
**Solução**: 
- Verificar se ZIP foi extraído corretamente
- Confirmar compose path: `docker-compose.portainer-lite.yml`
- Verificar se Dockerfile.api está no ZIP

### ❌ "No such file or directory: requirements.api.txt"
**Problema**: Arquivo de dependências não encontrado
**Solução**:
- Verificar se requirements.api.txt está no ZIP
- Confirmar estrutura de pastas no ZIP

### ❌ "Port already in use"
**Problema**: Porta 8000 já está sendo usada
**Solução**:
- Alterar `LANGEXTRACT_API_PORT=8001` nas variáveis
- Ou parar outros serviços na porta 8000

### ❌ Build muito lento
**Problema**: Build demora muito tempo
**Solução**:
- Verificar se `.dockerignore` está funcionando
- Usar imagem base mais leve
- Limpar cache: `docker system prune`

## 📊 Monitoramento

### Logs da Aplicação:
```bash
# Via Portainer
Stacks → langextract-api → Containers → langextract-api → Logs

# Via Docker CLI
docker logs langextract-api_langextract-api_1
```

### Recursos do Sistema:
```bash
# Uso de CPU/Memória
docker stats

# Espaço em disco
docker system df
```

## 🎯 Resumo

### ✅ Vantagens do Deploy via ZIP:
- **Controle total** sobre arquivos enviados
- **Funciona offline** (sem necessidade de Git)
- **Ideal para desenvolvimento** e testes
- **Compatível com WSL2** e Docker Desktop
- **Fácil de automatizar** com scripts

### ⚠️ Considerações:
- **Manual**: Requer upload manual para atualizações
- **Tamanho**: ZIP pode ficar grande com muitos arquivos
- **Versionamento**: Sem controle automático de versão

### 🚀 Próximos Passos:
1. Criar ZIP com script fornecido
2. Upload no Portainer
3. Configurar variáveis de ambiente
4. Deploy e teste
5. Configurar Cloudflare Tunnel (opcional)

---

**💡 Dica**: Para produção, considere migrar para deploy via Git Repository para ter atualizações automáticas e melhor controle de versão.