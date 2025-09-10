#!/bin/bash

# LangExtract API - Deploy Preparation Script
# This script prepares the environment for Docker deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="langextract-api"
DOCKER_IMAGE="${APP_NAME}:latest"
NETWORK_NAME="${APP_NAME}-network"
VOLUME_UPLOADS="${APP_NAME}-uploads"
VOLUME_LOGS="${APP_NAME}-logs"
VOLUME_CACHE="${APP_NAME}-cache"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

create_directories() {
    log_info "Creating necessary directories..."
    
    # Create local directories for development
    mkdir -p ./uploads
    mkdir -p ./logs
    mkdir -p ./cache
    mkdir -p ./data
    
    # Set proper permissions
    chmod 755 ./uploads ./logs ./cache ./data
    
    log_success "Directories created successfully"
}

create_docker_volumes() {
    log_info "Creating Docker volumes..."
    
    # Create named volumes for persistent data
    docker volume create ${VOLUME_UPLOADS} || log_warning "Volume ${VOLUME_UPLOADS} already exists"
    docker volume create ${VOLUME_LOGS} || log_warning "Volume ${VOLUME_LOGS} already exists"
    docker volume create ${VOLUME_CACHE} || log_warning "Volume ${VOLUME_CACHE} already exists"
    
    log_success "Docker volumes created successfully"
}

create_docker_network() {
    log_info "Creating Docker network..."
    
    # Create custom network for better container communication
    docker network create ${NETWORK_NAME} --driver bridge || log_warning "Network ${NETWORK_NAME} already exists"
    
    log_success "Docker network created successfully"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    
    # Copy environment template if .env doesn't exist
    if [ ! -f .env ]; then
        if [ -f api/.env.sample ]; then
            cp api/.env.sample .env
            log_success "Environment file created from template"
            log_warning "Please edit .env file with your configuration before starting the application"
        else
            log_error "Environment template not found. Please create .env file manually."
            exit 1
        fi
    else
        log_info "Environment file already exists"
    fi
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    if [ ! -f .env ]; then
        log_error "Environment file (.env) not found"
        exit 1
    fi
    
    # Check for required environment variables
    required_vars=("API_KEY" "UPLOAD_DIR" "MAX_FILE_SIZE")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            log_error "Required environment variable ${var} not found in .env file"
            exit 1
        fi
    done
    
    log_success "Environment configuration validated"
}

cleanup_old_containers() {
    log_info "Cleaning up old containers and images..."
    
    # Stop and remove existing containers
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f
    
    log_success "Cleanup completed"
}

build_image() {
    log_info "Building Docker image..."
    
    # Build the application image
    docker build -t ${DOCKER_IMAGE} . --no-cache
    
    log_success "Docker image built successfully"
}

run_health_check() {
    log_info "Running health check..."
    
    # Start services in detached mode
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Check if API is responding
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null; then
            log_success "Health check passed - API is responding"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for API to respond..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Health check failed - API is not responding after $max_attempts attempts"
    docker-compose logs
    return 1
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose ps
    echo ""
    log_info "Available endpoints:"
    echo "  - API: http://localhost:8000"
    echo "  - Documentation: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/health"
    echo ""
    log_info "Logs: docker-compose logs -f"
    log_info "Stop: docker-compose down"
}

# Main execution
main() {
    log_info "Starting LangExtract API deployment preparation..."
    echo ""
    
    check_requirements
    create_directories
    create_docker_volumes
    create_docker_network
    setup_environment
    validate_environment
    cleanup_old_containers
    build_image
    
    if run_health_check; then
        show_status
        log_success "Deployment preparation completed successfully!"
    else
        log_error "Deployment preparation failed!"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "--help" | "-h")
        echo "LangExtract API Deploy Preparation Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check-only   Only check requirements, don't deploy"
        echo "  --build-only   Only build the image, don't start services"
        echo "  --no-health    Skip health check"
        echo ""
        exit 0
        ;;
    "--check-only")
        check_requirements
        validate_environment
        log_success "Requirements check completed"
        exit 0
        ;;
    "--build-only")
        check_requirements
        setup_environment
        validate_environment
        build_image
        log_success "Build completed"
        exit 0
        ;;
    "--no-health")
        log_info "Starting deployment without health check..."
        check_requirements
        create_directories
        create_docker_volumes
        create_docker_network
        setup_environment
        validate_environment
        cleanup_old_containers
        build_image
        docker-compose up -d
        show_status
        log_success "Deployment completed (health check skipped)"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac