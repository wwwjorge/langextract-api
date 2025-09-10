# Script para limpar completamente o cache do Docker e forçar rebuild
# Execute este script antes de fazer o deploy no Portainer

Write-Host "Limpando cache do Docker..." -ForegroundColor Yellow

# Parar todos os containers relacionados ao projeto
Write-Host "Parando containers..." -ForegroundColor Cyan
docker ps -a --filter "name=langextract" --format "table {{.Names}}\t{{.Status}}" | ForEach-Object {
    if ($_ -match "langextract") {
        $containerName = ($_ -split "\s+")[0]
        docker stop $containerName 2>$null
        docker rm $containerName 2>$null
    }
}

# Remover imagens relacionadas ao projeto
Write-Host "Removendo imagens..." -ForegroundColor Cyan
docker images --filter "reference=*langextract*" --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}" | ForEach-Object {
    if ($_ -match "langextract") {
        $imageId = ($_ -split "\s+")[-1]
        docker rmi $imageId --force 2>$null
    }
}

# Limpar cache de build
Write-Host "Limpando cache de build..." -ForegroundColor Cyan
docker builder prune --all --force

# Limpar volumes órfãos
Write-Host "Limpando volumes órfãos..." -ForegroundColor Cyan
docker volume prune --force

# Limpar redes não utilizadas
Write-Host "Limpando redes não utilizadas..." -ForegroundColor Cyan
docker network prune --force

# Limpar sistema completo (cuidado!)
Write-Host "Limpeza final do sistema..." -ForegroundColor Cyan
docker system prune --all --force

Write-Host "Cache do Docker limpo com sucesso!" -ForegroundColor Green
Write-Host "Agora você pode fazer o deploy no Portainer usando o arquivo docker-compose.portainer-nocache.yml" -ForegroundColor Yellow