# =============================================================================
# Script PowerShell para criar ZIP de deploy do LangExtract API para Portainer
# =============================================================================

param(
    [string]$OutputPath = ".",
    [switch]$Verbose
)

# Função para print colorido
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Função para verificar se arquivo existe
function Test-RequiredFile {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-ColorOutput "❌ Arquivo obrigatório não encontrado: $FilePath" "Red"
        exit 1
    }
}

# Função para verificar se diretório existe
function Test-RequiredDirectory {
    param([string]$DirPath)
    
    if (-not (Test-Path $DirPath -PathType Container)) {
        Write-ColorOutput "❌ Diretório obrigatório não encontrado: $DirPath" "Red"
        exit 1
    }
}

Write-ColorOutput "🚀 Criando ZIP para deploy do LangExtract API no Portainer" "Blue"
Write-ColorOutput "==========================================================" "Blue"

# Verificar se estamos no diretório correto
if (-not (Test-Path "docker-compose.portainer-lite.yml")) {
    Write-ColorOutput "❌ Execute este script na pasta raiz do projeto LangExtract" "Red"
    Write-ColorOutput "💡 Navegue até a pasta que contém docker-compose.portainer-lite.yml" "Yellow"
    exit 1
}

# Verificar arquivos obrigatórios
Write-ColorOutput "🔍 Verificando arquivos obrigatórios..." "Yellow"
Test-RequiredFile "Dockerfile.api"
Test-RequiredFile "docker-compose.portainer-lite.yml"
Test-RequiredFile ".env.portainer-lite"
Test-RequiredFile "requirements.api.txt"
Test-RequiredDirectory "api"

Write-ColorOutput "✅ Todos os arquivos obrigatórios encontrados" "Green"

# Limpar arquivos temporários
Write-ColorOutput "🧹 Limpando arquivos temporários..." "Yellow"

# Remover __pycache__
Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
    $path = Join-Path $PWD $_
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        if ($Verbose) { Write-ColorOutput "   Removido: $path" "Gray" }
    }
}

# Remover arquivos .pyc, .pyo, .pyd
$tempFiles = @("*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db")
foreach ($pattern in $tempFiles) {
    Get-ChildItem -Path . -Recurse -File -Name $pattern | ForEach-Object {
        $path = Join-Path $PWD $_
        if (Test-Path $path) {
            Remove-Item $path -Force -ErrorAction SilentlyContinue
            if ($Verbose) { Write-ColorOutput "   Removido: $path" "Gray" }
        }
    }
}

# Criar nome do arquivo ZIP com timestamp
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipName = "langextract-api-$timestamp.zip"
$zipPath = Join-Path $OutputPath $zipName

Write-ColorOutput "📦 Criando arquivo ZIP: $zipName" "Yellow"

# Lista de arquivos/pastas a excluir
$excludePatterns = @(
    ".git*",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "uploads",
    "outputs",
    "logs",
    "*.log",
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
    "*.tmp",
    "*.temp",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    ".tox",
    "dist",
    "build",
    "*.egg-info",
    "create_deploy_zip.sh",
    "create_deploy_zip.ps1"
)

try {
    # Usar System.IO.Compression para criar ZIP
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    # Remover ZIP existente se houver
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    # Criar ZIP
    $zip = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Create)
    
    # Função para verificar se arquivo deve ser excluído
    function Should-Exclude {
        param([string]$RelativePath)
        
        foreach ($pattern in $excludePatterns) {
            if ($RelativePath -like "*$pattern*" -or $RelativePath -like "$pattern*") {
                return $true
            }
        }
        return $false
    }
    
    # Adicionar arquivos ao ZIP
    $fileCount = 0
    Get-ChildItem -Path . -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
        $relativePath = $relativePath.Replace("\", "/")  # Usar / para compatibilidade
        
        if (-not (Should-Exclude $relativePath)) {
            $entry = $zip.CreateEntry($relativePath)
            $entryStream = $entry.Open()
            $fileStream = [System.IO.File]::OpenRead($_.FullName)
            $fileStream.CopyTo($entryStream)
            $fileStream.Close()
            $entryStream.Close()
            $fileCount++
            
            if ($Verbose) {
                Write-ColorOutput "   Adicionado: $relativePath" "Gray"
            }
        } elseif ($Verbose) {
            Write-ColorOutput "   Excluído: $relativePath" "DarkGray"
        }
    }
    
    $zip.Dispose()
    
    Write-ColorOutput "✅ ZIP criado com sucesso!" "Green"
    Write-ColorOutput "📊 $fileCount arquivos adicionados ao ZIP" "Cyan"
    
} catch {
    Write-ColorOutput "❌ Erro ao criar ZIP: $($_.Exception.Message)" "Red"
    exit 1
}

# Mostrar informações do arquivo
$zipInfo = Get-Item $zipPath
$zipSizeMB = [math]::Round($zipInfo.Length / 1MB, 2)

Write-ColorOutput "📊 Informações do arquivo:" "Blue"
Write-ColorOutput "   📁 Nome: $zipName" "White"
Write-ColorOutput "   📏 Tamanho: $zipSizeMB MB" "White"
Write-ColorOutput "   📍 Local: $($zipInfo.FullName)" "White"

# Verificar arquivos críticos no ZIP
Write-ColorOutput "`n🔍 Verificando arquivos críticos no ZIP..." "Yellow"

$criticalFiles = @(
    "Dockerfile.api",
    "docker-compose.portainer-lite.yml",
    ".env.portainer-lite",
    "requirements.api.txt",
    "api/main.py",
    "api/__init__.py"
)

try {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    
    foreach ($file in $criticalFiles) {
        $normalizedFile = $file.Replace("\", "/")
        $found = $zip.Entries | Where-Object { $_.FullName -eq $normalizedFile }
        
        if ($found) {
            Write-ColorOutput "   ✅ $file" "Green"
        } else {
            Write-ColorOutput "   ❌ $file (FALTANDO!)" "Red"
        }
    }
    
    $zip.Dispose()
    
} catch {
    Write-ColorOutput "⚠️ Não foi possível verificar o conteúdo do ZIP" "Yellow"
}

Write-ColorOutput "`n🎯 Próximos passos:" "Blue"
Write-ColorOutput "1. Acesse seu Portainer" "White"
Write-ColorOutput "2. Vá em Stacks > Add stack" "White"
Write-ColorOutput "3. Escolha 'Upload' como build method" "White"
Write-ColorOutput "4. Faça upload do arquivo: $zipName" "White"
Write-ColorOutput "5. Configure as variáveis de ambiente" "White"
Write-ColorOutput "6. Deploy da stack" "White"

Write-ColorOutput "`n💡 Dicas:" "Yellow"
Write-ColorOutput "• Use docker-compose.portainer-lite.yml como compose path" "White"
Write-ColorOutput "• Copie as variáveis do arquivo .env.portainer-lite" "White"
Write-ColorOutput "• Não esqueça de configurar GEMINI_API_KEY e API_SECRET_KEY" "White"

Write-ColorOutput "`n🎉 Deploy ZIP criado com sucesso!" "Green"
Write-ColorOutput "==========================================================" "Blue"

# Abrir pasta do arquivo se solicitado
if ($PSCmdlet.ShouldProcess("Explorer", "Abrir pasta do ZIP")) {
    $openFolder = Read-Host "`nDeseja abrir a pasta do arquivo ZIP? (s/N)"
    if ($openFolder -eq "s" -or $openFolder -eq "S" -or $openFolder -eq "sim") {
        Start-Process "explorer.exe" -ArgumentList "/select,`"$($zipInfo.FullName)`""
    }
}