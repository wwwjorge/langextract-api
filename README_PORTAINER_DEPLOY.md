# LangExtract API - Deploy via Portainer (WSL)

Este guia fornece instruções para deploy da LangExtract API usando Portainer no WSL.

## Pré-requisitos

- WSL2 instalado e configurado
- Docker instalado no WSL
- Portainer instalado e rodando
- Ollama rodando no host (opcional, para modelos locais)

## Configuração Rápida

### 1. Preparar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações necessárias
nano .env
```

### 2. Deploy via Portainer

1. Acesse o Portainer
2. Vá para **Stacks** > **Add Stack**
3. Nome: `langextract-api`
4. Método: **Repository**
5. Repository URL: `https://github.com/seu-usuario/seu-repo.git`
6. Compose path: `docker-compose.yml`
7. Environment variables: Cole o conteúdo do seu `.env`
8. Clique em **Deploy the stack**

### 3. Verificar Deploy

Após o deploy, a API estará disponível em:
- URL: `http://localhost:8001`
- Documentação: `http://localhost:8001/docs`
- Health Check: `http://localhost:8001/health`

## Configurações Importantes

### Ollama (Modelos Locais)

Para usar Ollama rodando no host WSL:
```env
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### CORS

Para desenvolvimento:
```env
CORS_ORIGINS=*
```

Para produção (especifique domínios):
```env
CORS_ORIGINS=https://seudominio.com,https://app.seudominio.com
```

### API Keys

Configure as chaves necessárias no arquivo `.env`:
```env
OPENAI_API_KEY=sua-chave-openai
GEMINI_API_KEY=sua-chave-gemini
ANTHROPIC_API_KEY=sua-chave-anthropic
```

## Estrutura do Deploy

```
langextract-api/
├── docker-compose.yml    # Configuração principal
├── .env                  # Variáveis de ambiente
├── Dockerfile           # Build da aplicação
└── api/                 # Código da API
```

## Volumes Persistentes

O deploy cria os seguintes volumes:
- `langextract-uploads`: Arquivos enviados
- `langextract-logs`: Logs da aplicação
- `langextract-cache`: Cache da aplicação

## Recursos Alocados

- **CPU**: Limite de 1.0 core, reserva de 0.25 core
- **Memória**: Limite de 1GB, reserva de 256MB
- **Health Check**: Verificação a cada 30s

## Troubleshooting

### Problema: Ollama não conecta
**Solução**: Verifique se o Ollama está rodando e use `172.17.0.1:11434`

### Problema: Erro de permissão nos volumes
**Solução**: Verifique as permissões dos diretórios no WSL

### Problema: API não responde
**Solução**: Verifique os logs no Portainer > Containers > langextract-api > Logs

## Comandos Úteis

```bash
# Verificar status dos containers
docker ps

# Ver logs da aplicação
docker logs langextract-api

# Acessar container
docker exec -it langextract-api bash

# Reiniciar stack
docker-compose restart
```

## Segurança

- Mantenha as API keys seguras
- Use HTTPS em produção
- Configure CORS adequadamente
- Monitore os logs regularmente

## Suporte

Para problemas específicos, verifique:
1. Logs do container no Portainer
2. Status do health check
3. Conectividade com provedores externos
4. Configuração das variáveis de ambiente