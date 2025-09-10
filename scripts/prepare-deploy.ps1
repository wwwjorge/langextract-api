# LangExtract API - Deploy Preparation Script (PowerShell)
# This script prepares the environment for Docker deployment on Windows

param(
    [switch]$Help,
    [switch]$CheckOnly,
    [switch]$BuildOnly,
    [switch]$NoHealth
)

# Configuration
$AppName = "langextract-api"
$DockerImage = "${AppName}:latest"
$NetworkName = "${AppName}-network"
$VolumeUploads = "${AppName}-uploads"
$VolumeLogs = "${AppName}-logs"
$VolumeCache = "${AppName}-cache"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-Requirements {
    Write-Info "Checking system requirements..."
    
    # Check Docker
    try {
        $null = docker --version
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $null = docker-compose --version
    }
    catch {
        try {
            $null = docker compose version
        }
        catch {
            Write-Error "Docker Compose is not installed. Please install Docker Compose first."
            exit 1
        }
    }
    
    # Check if Docker daemon is running
    try {
        $null = docker info 2>$null
    }
    catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop first."
        exit 1
    }
    
    Write-Success "All requirements satisfied"
}

function New-Directories {
    Write-Info "Creating necessary directories..."
    
    # Create local directories for development
    $directories = @("uploads", "logs", "cache", "data")
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directories created successfully"
}

function New-DockerVolumes {
    Write-Info "Creating Docker volumes..."
    
    $volumes = @($VolumeUploads, $VolumeLogs, $VolumeCache)
    
    foreach ($volume in $volumes) {
        try {
            docker volume create $volume 2>$null | Out-Null
        }
        catch {
            Write-Warning "Volume $volume already exists"
        }
    }
    
    Write-Success "Docker volumes created successfully"
}

function New-DockerNetwork {
    Write-Info "Creating Docker network..."
    
    try {
        docker network create $NetworkName --driver bridge 2>$null | Out-Null
    }
    catch {
        Write-Warning "Network $NetworkName already exists"
    }
    
    Write-Success "Docker network created successfully"
}

function Set-Environment {
    Write-Info "Setting up environment configuration..."
    
    # Copy environment template if .env doesn't exist
    if (!(Test-Path ".env")) {
        if (Test-Path "api\.env.sample") {
            Copy-Item "api\.env.sample" ".env"
            Write-Success "Environment file created from template"
            Write-Warning "Please edit .env file with your configuration before starting the application"
        }
        else {
            Write-Error "Environment template not found. Please create .env file manually."
            exit 1
        }
    }
    else {
        Write-Info "Environment file already exists"
    }
}

function Test-Environment {
    Write-Info "Validating environment configuration..."
    
    if (!(Test-Path ".env")) {
        Write-Error "Environment file (.env) not found"
        exit 1
    }
    
    # Check for required environment variables
    $requiredVars = @("API_KEY", "UPLOAD_DIR", "MAX_FILE_SIZE")
    $envContent = Get-Content ".env"
    
    foreach ($var in $requiredVars) {
        if (!($envContent | Select-String "^$var=")) {
            Write-Error "Required environment variable $var not found in .env file"
            exit 1
        }
    }
    
    Write-Success "Environment configuration validated"
}

function Remove-OldContainers {
    Write-Info "Cleaning up old containers and images..."
    
    # Stop and remove existing containers
    try {
        docker-compose down --remove-orphans 2>$null
    }
    catch {
        # Ignore errors if no containers exist
    }
    
    # Remove dangling images
    docker image prune -f | Out-Null
    
    Write-Success "Cleanup completed"
}

function Build-Image {
    Write-Info "Building Docker image..."
    
    # Build the application image
    docker build -t $DockerImage . --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker image build failed"
        exit 1
    }
    
    Write-Success "Docker image built successfully"
}

function Test-Health {
    Write-Info "Running health check..."
    
    # Start services in detached mode
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start services"
        exit 1
    }
    
    # Wait for services to be ready
    Write-Info "Waiting for services to start..."
    Start-Sleep -Seconds 10
    
    # Check if API is responding
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Health check passed - API is responding"
                return $true
            }
        }
        catch {
            # Continue trying
        }
        
        Write-Info "Attempt $attempt/$maxAttempts - waiting for API to respond..."
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Error "Health check failed - API is not responding after $maxAttempts attempts"
    docker-compose logs
    return $false
}

function Show-Status {
    Write-Info "Deployment Status:"
    Write-Host ""
    docker-compose ps
    Write-Host ""
    Write-Info "Available endpoints:"
    Write-Host "  - API: http://localhost:8000"
    Write-Host "  - Documentation: http://localhost:8000/docs"
    Write-Host "  - Health Check: http://localhost:8000/health"
    Write-Host ""
    Write-Info "Logs: docker-compose logs -f"
    Write-Info "Stop: docker-compose down"
}

function Show-Help {
    Write-Host "LangExtract API Deploy Preparation Script"
    Write-Host ""
    Write-Host "Usage: .\prepare-deploy.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help          Show this help message"
    Write-Host "  -CheckOnly     Only check requirements, don't deploy"
    Write-Host "  -BuildOnly     Only build the image, don't start services"
    Write-Host "  -NoHealth      Skip health check"
    Write-Host ""
}

# Main execution
function Start-Main {
    Write-Info "Starting LangExtract API deployment preparation..."
    Write-Host ""
    
    Test-Requirements
    New-Directories
    New-DockerVolumes
    New-DockerNetwork
    Set-Environment
    Test-Environment
    Remove-OldContainers
    Build-Image
    
    if (Test-Health) {
        Show-Status
        Write-Success "Deployment preparation completed successfully!"
    }
    else {
        Write-Error "Deployment preparation failed!"
        exit 1
    }
}

# Handle script parameters
if ($Help) {
    Show-Help
    exit 0
}
elseif ($CheckOnly) {
    Test-Requirements
    Test-Environment
    Write-Success "Requirements check completed"
    exit 0
}
elseif ($BuildOnly) {
    Test-Requirements
    Set-Environment
    Test-Environment
    Build-Image
    Write-Success "Build completed"
    exit 0
}
elseif ($NoHealth) {
    Write-Info "Starting deployment without health check..."
    Test-Requirements
    New-Directories
    New-DockerVolumes
    New-DockerNetwork
    Set-Environment
    Test-Environment
    Remove-OldContainers
    Build-Image
    docker-compose up -d
    Show-Status
    Write-Success "Deployment completed (health check skipped)"
    exit 0
}
else {
    Start-Main
}