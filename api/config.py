"""Configuration module for LangExtract API."""

import os
from typing import List
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production",
        env="API_SECRET_KEY"
    )
    api_algorithm: str = Field(default="HS256", env="API_ALGORITHM")
    api_access_token_expire_minutes: int = Field(
        default=30, 
        env="API_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # LLM Provider API Keys
    langextract_api_key: str = Field(default="", env="LANGEXTRACT_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", 
        env="OLLAMA_BASE_URL"
    )
    
    # Default Model Settings
    default_model_id: str = Field(
        default="gemini-2.5-flash", 
        env="DEFAULT_MODEL_ID"
    )
    default_temperature: float = Field(
        default=0.3, 
        env="DEFAULT_TEMPERATURE"
    )
    default_max_char_buffer: int = Field(
        default=1000, 
        env="DEFAULT_MAX_CHAR_BUFFER"
    )
    default_max_workers: int = Field(
        default=10, 
        env="DEFAULT_MAX_WORKERS"
    )
    default_batch_length: int = Field(
        default=10, 
        env="DEFAULT_BATCH_LENGTH"
    )
    default_extraction_passes: int = Field(
        default=1, 
        env="DEFAULT_EXTRACTION_PASSES"
    )
    
    # File Upload Settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_file_extensions: str = Field(
        default=".txt,.pdf,.docx,.md,.json", 
        env="ALLOWED_FILE_EXTENSIONS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(
        default="logs/langextract-api.log", 
        env="LOG_FILE"
    )
    
    # Database (optional)
    database_url: str = Field(
        default="sqlite:///./langextract.db", 
        env="DATABASE_URL"
    )
    
    # CORS Settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080", 
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: str = Field(
        default="GET,POST,PUT,DELETE", 
        env="ALLOWED_METHODS"
    )
    allowed_headers: str = Field(default="*", env="ALLOWED_HEADERS")
    
    # Directory Settings
    uploads_dir: str = Field(default="uploads", env="UPLOADS_DIR")
    outputs_dir: str = Field(default="outputs", env="OUTPUTS_DIR")
    logs_dir: str = Field(default="logs", env="LOGS_DIR")
    
    # Processing Settings
    max_concurrent_extractions: int = Field(
        default=5, 
        env="MAX_CONCURRENT_EXTRACTIONS"
    )
    extraction_timeout_seconds: int = Field(
        default=300, 
        env="EXTRACTION_TIMEOUT_SECONDS"
    )
    cleanup_old_files_days: int = Field(
        default=7, 
        env="CLEANUP_OLD_FILES_DAYS"
    )
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60, 
        env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    rate_limit_requests_per_hour: int = Field(
        default=1000, 
        env="RATE_LIMIT_REQUESTS_PER_HOUR"
    )
    
    # Health Check Settings
    health_check_timeout: int = Field(
        default=30, 
        env="HEALTH_CHECK_TIMEOUT"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def allowed_methods_list(self) -> List[str]:
        """Get allowed methods as a list."""
        return [method.strip() for method in self.allowed_methods.split(",")]
    
    @property
    def allowed_headers_list(self) -> List[str]:
        """Get allowed headers as a list."""
        if self.allowed_headers == "*":
            return ["*"]
        return [header.strip() for header in self.allowed_headers.split(",")]
    
    @property
    def allowed_file_extensions_list(self) -> List[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.allowed_file_extensions.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider."""
        provider_keys = {
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
            "langextract": self.langextract_api_key
        }
        return provider_keys.get(provider.lower(), "")
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key is available for provider."""
        return bool(self.get_api_key(provider))
    
    def get_model_config(self, model_id: str = None) -> dict:
        """Get model configuration."""
        model_id = model_id or self.default_model_id
        
        # Determine provider from model_id
        if model_id.startswith("gpt-") or model_id.startswith("text-"):
            provider = "openai"
        elif model_id.startswith("gemini-"):
            provider = "gemini"
        elif ":" in model_id:  # Ollama format like "llama3.2:1b"
            provider = "ollama"
        else:
            provider = "gemini"  # Default
        
        config = {
            "model_id": model_id,
            "provider": provider,
            "temperature": self.default_temperature,
            "max_char_buffer": self.default_max_char_buffer,
            "max_workers": self.default_max_workers,
            "batch_length": self.default_batch_length,
            "extraction_passes": self.default_extraction_passes
        }
        
        # Add provider-specific settings
        if provider == "ollama":
            config["model_url"] = self.ollama_base_url
        else:
            api_key = self.get_api_key(provider)
            if api_key:
                config["api_key"] = api_key
        
        return config
    
    def validate_model_access(self, model_id: str, user_api_key: str = None) -> bool:
        """Validate if model can be accessed."""
        config = self.get_model_config(model_id)
        provider = config["provider"]
        
        if provider == "ollama":
            return True  # Ollama doesn't require API key
        
        # Check if we have API key (from env or user provided)
        has_env_key = self.has_api_key(provider)
        has_user_key = bool(user_api_key)
        
        return has_env_key or has_user_key


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_database_url() -> str:
    """Get database URL."""
    settings = get_settings()
    return settings.database_url


def get_upload_path(filename: str) -> str:
    """Get full path for uploaded file."""
    settings = get_settings()
    return os.path.join(settings.uploads_dir, filename)


def get_output_path(filename: str) -> str:
    """Get full path for output file."""
    settings = get_settings()
    return os.path.join(settings.outputs_dir, filename)


def get_log_path() -> str:
    """Get log file path."""
    settings = get_settings()
    return settings.log_file


def create_directories():
    """Create necessary directories."""
    settings = get_settings()
    
    directories = [
        settings.uploads_dir,
        settings.outputs_dir,
        settings.logs_dir
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_supported_models() -> List[dict]:
    """Get list of supported models with their configurations."""
    settings = get_settings()
    
    models = [
        {
            "model_id": "gemini-2.5-flash",
            "provider": "gemini",
            "description": "Fast and efficient Gemini model",
            "requires_api_key": True,
            "available": settings.has_api_key("gemini")
        },
        {
            "model_id": "gemini-2.5-pro",
            "provider": "gemini",
            "description": "Advanced Gemini model for complex tasks",
            "requires_api_key": True,
            "available": settings.has_api_key("gemini")
        },
        {
            "model_id": "gpt-4o",
            "provider": "openai",
            "description": "OpenAI GPT-4 Omni model",
            "requires_api_key": True,
            "available": settings.has_api_key("openai")
        },
        {
            "model_id": "gpt-4o-mini",
            "provider": "openai",
            "description": "Smaller, faster GPT-4 model",
            "requires_api_key": True,
            "available": settings.has_api_key("openai")
        },
        {
            "model_id": "gpt-3.5-turbo",
            "provider": "openai",
            "description": "OpenAI GPT-3.5 Turbo model",
            "requires_api_key": True,
            "available": settings.has_api_key("openai")
        },
        {
            "model_id": "llama3.2:1b",
            "provider": "ollama",
            "description": "Local Llama 3.2 1B model",
            "requires_api_key": False,
            "available": True
        },
        {
            "model_id": "llama3.2:3b",
            "provider": "ollama",
            "description": "Local Llama 3.2 3B model",
            "requires_api_key": False,
            "available": True
        },
        {
            "model_id": "gemma2:2b",
            "provider": "ollama",
            "description": "Local Gemma 2 2B model",
            "requires_api_key": False,
            "available": True
        },
        {
            "model_id": "qwen2.5:1.5b",
            "provider": "ollama",
            "description": "Local Qwen 2.5 1.5B model",
            "requires_api_key": False,
            "available": True
        }
    ]
    
    return models