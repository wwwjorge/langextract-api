#!/bin/bash

# Advanced Health Check Script for LangExtract API
# This script performs comprehensive health checks for the application

set -euo pipefail

# Configuration
API_HOST="${API_HOST:-localhost}"
API_PORT="${API_PORT:-8000}"
API_KEY="${API_KEY:-}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-10}"
MAX_RETRIES="${MAX_RETRIES:-3}"
RETRY_DELAY="${RETRY_DELAY:-2}"
VERBOSE="${VERBOSE:-false}"
CHECK_DEPENDENCIES="${CHECK_DEPENDENCIES:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local expected_status="${2:-200}"
    local description="$3"
    
    log_verbose "Checking $description: $url"
    
    local response
    local status_code
    local retry_count=0
    
    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        if command_exists curl; then
            response=$(curl -s -w "\n%{http_code}" \
                --max-time "$HEALTH_TIMEOUT" \
                --connect-timeout 5 \
                -H "X-API-Key: $API_KEY" \
                "$url" 2>/dev/null || echo "000")
            status_code=$(echo "$response" | tail -n1)
        elif command_exists wget; then
            if wget --timeout="$HEALTH_TIMEOUT" \
                --tries=1 \
                --header="X-API-Key: $API_KEY" \
                -q -O - "$url" >/dev/null 2>&1; then
                status_code="200"
            else
                status_code="000"
            fi
        else
            log_error "Neither curl nor wget is available"
            return 1
        fi
        
        if [[ "$status_code" == "$expected_status" ]]; then
            log_success "$description: OK (HTTP $status_code)"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [[ $retry_count -lt $MAX_RETRIES ]]; then
            log_warning "$description: Failed (HTTP $status_code), retrying in ${RETRY_DELAY}s... ($retry_count/$MAX_RETRIES)"
            sleep "$RETRY_DELAY"
        fi
    done
    
    log_error "$description: Failed after $MAX_RETRIES attempts (HTTP $status_code)"
    return 1
}

# Function to check database connectivity
check_database() {
    if [[ "$CHECK_DEPENDENCIES" != "true" ]]; then
        return 0
    fi
    
    local db_host="${POSTGRES_HOST:-postgres}"
    local db_port="${POSTGRES_PORT:-5432}"
    local db_name="${POSTGRES_DB:-langextract}"
    local db_user="${POSTGRES_USER:-langextract}"
    
    log_verbose "Checking database connectivity: $db_host:$db_port"
    
    if command_exists pg_isready; then
        if pg_isready -h "$db_host" -p "$db_port" -d "$db_name" -U "$db_user" -t "$HEALTH_TIMEOUT"; then
            log_success "Database: OK"
            return 0
        else
            log_error "Database: Connection failed"
            return 1
        fi
    elif command_exists nc; then
        if nc -z "$db_host" "$db_port" 2>/dev/null; then
            log_success "Database: Port accessible"
            return 0
        else
            log_error "Database: Port not accessible"
            return 1
        fi
    else
        log_warning "Database: Cannot check (pg_isready and nc not available)"
        return 0
    fi
}

# Function to check Redis connectivity
check_redis() {
    if [[ "$CHECK_DEPENDENCIES" != "true" ]]; then
        return 0
    fi
    
    local redis_host="${REDIS_HOST:-redis}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_password="${REDIS_PASSWORD:-}"
    
    log_verbose "Checking Redis connectivity: $redis_host:$redis_port"
    
    if command_exists redis-cli; then
        local redis_cmd="redis-cli -h $redis_host -p $redis_port"
        if [[ -n "$redis_password" ]]; then
            redis_cmd="$redis_cmd -a $redis_password --no-auth-warning"
        fi
        
        if $redis_cmd ping >/dev/null 2>&1; then
            log_success "Redis: OK"
            return 0
        else
            log_error "Redis: Connection failed"
            return 1
        fi
    elif command_exists nc; then
        if nc -z "$redis_host" "$redis_port" 2>/dev/null; then
            log_success "Redis: Port accessible"
            return 0
        else
            log_error "Redis: Port not accessible"
            return 1
        fi
    else
        log_warning "Redis: Cannot check (redis-cli and nc not available)"
        return 0
    fi
}

# Function to check disk space
check_disk_space() {
    local threshold="${DISK_THRESHOLD:-80}"
    local upload_dir="${UPLOAD_DIR:-/app/uploads}"
    
    log_verbose "Checking disk space for $upload_dir (threshold: ${threshold}%)"
    
    if command_exists df; then
        local usage
        usage=$(df "$upload_dir" 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//' || echo "0")
        
        if [[ "$usage" -lt "$threshold" ]]; then
            log_success "Disk space: OK (${usage}% used)"
            return 0
        else
            log_error "Disk space: Critical (${usage}% used, threshold: ${threshold}%)"
            return 1
        fi
    else
        log_warning "Disk space: Cannot check (df not available)"
        return 0
    fi
}

# Function to check memory usage
check_memory() {
    local threshold="${MEMORY_THRESHOLD:-90}"
    
    log_verbose "Checking memory usage (threshold: ${threshold}%)"
    
    if [[ -f /proc/meminfo ]]; then
        local total_mem
        local available_mem
        local used_percentage
        
        total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        available_mem=$(grep MemAvailable /proc/meminfo | awk '{print $2}' || grep MemFree /proc/meminfo | awk '{print $2}')
        
        if [[ -n "$total_mem" && -n "$available_mem" ]]; then
            used_percentage=$(( (total_mem - available_mem) * 100 / total_mem ))
            
            if [[ "$used_percentage" -lt "$threshold" ]]; then
                log_success "Memory: OK (${used_percentage}% used)"
                return 0
            else
                log_error "Memory: Critical (${used_percentage}% used, threshold: ${threshold}%)"
                return 1
            fi
        fi
    fi
    
    log_warning "Memory: Cannot check (/proc/meminfo not available)"
    return 0
}

# Function to check API endpoints
check_api_endpoints() {
    local base_url="http://${API_HOST}:${API_PORT}"
    local failed=0
    
    log_info "Checking API endpoints..."
    
    # Basic health check
    if ! check_http_endpoint "$base_url/health" "200" "Health endpoint"; then
        failed=$((failed + 1))
    fi
    
    # API info endpoint
    if ! check_http_endpoint "$base_url/" "200" "Root endpoint"; then
        failed=$((failed + 1))
    fi
    
    # Docs endpoint
    if ! check_http_endpoint "$base_url/docs" "200" "Documentation endpoint"; then
        failed=$((failed + 1))
    fi
    
    # Metrics endpoint (if available)
    check_http_endpoint "$base_url/metrics" "200" "Metrics endpoint" || true
    
    return $failed
}

# Function to run all health checks
run_health_checks() {
    local failed=0
    
    log_info "Starting comprehensive health check..."
    log_info "Target: ${API_HOST}:${API_PORT}"
    
    # Check API endpoints
    if ! check_api_endpoints; then
        failed=$((failed + 1))
    fi
    
    # Check dependencies
    if ! check_database; then
        failed=$((failed + 1))
    fi
    
    if ! check_redis; then
        failed=$((failed + 1))
    fi
    
    # Check system resources
    if ! check_disk_space; then
        failed=$((failed + 1))
    fi
    
    if ! check_memory; then
        failed=$((failed + 1))
    fi
    
    return $failed
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Advanced health check script for LangExtract API

Options:
  -h, --help              Show this help message
  -v, --verbose           Enable verbose output
  -q, --quick             Quick check (API only)
  --no-deps              Skip dependency checks
  --host HOST            API host (default: localhost)
  --port PORT            API port (default: 8000)
  --api-key KEY          API key for authentication
  --timeout SECONDS      Health check timeout (default: 10)
  --retries COUNT        Max retry attempts (default: 3)
  --retry-delay SECONDS  Delay between retries (default: 2)

Environment Variables:
  API_HOST               API host
  API_PORT               API port
  API_KEY                API key
  HEALTH_TIMEOUT         Health check timeout
  MAX_RETRIES            Max retry attempts
  RETRY_DELAY            Delay between retries
  VERBOSE                Enable verbose output (true/false)
  CHECK_DEPENDENCIES     Check dependencies (true/false)
  DISK_THRESHOLD         Disk usage threshold percentage
  MEMORY_THRESHOLD       Memory usage threshold percentage

Exit Codes:
  0    All checks passed
  1    One or more checks failed
  2    Invalid arguments

Examples:
  $0                                    # Basic health check
  $0 --verbose                          # Verbose health check
  $0 --quick                           # Quick API-only check
  $0 --host api.example.com --port 443 # Custom host/port
  $0 --no-deps                         # Skip dependency checks

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -q|--quick)
            CHECK_DEPENDENCIES="false"
            shift
            ;;
        --no-deps)
            CHECK_DEPENDENCIES="false"
            shift
            ;;
        --host)
            API_HOST="$2"
            shift 2
            ;;
        --port)
            API_PORT="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --timeout)
            HEALTH_TIMEOUT="$2"
            shift 2
            ;;
        --retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        --retry-delay)
            RETRY_DELAY="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 2
            ;;
    esac
done

# Main execution
main() {
    local start_time
    local end_time
    local duration
    
    start_time=$(date +%s)
    
    if run_health_checks; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_success "All health checks passed! (${duration}s)"
        exit 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_error "Health check failed! (${duration}s)"
        exit 1
    fi
}

# Run main function
main "$@"