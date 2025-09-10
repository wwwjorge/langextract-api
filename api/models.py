"""Pydantic models for the LangExtract API."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator
import json


class ExtractionRequest(BaseModel):
    """Request model for text extraction."""
    model_config = {"protected_namespaces": ()}
    
    text: str = Field(..., description="Text to extract information from")
    prompt_description: str = Field(
        ..., 
        description="Description of what to extract",
        example="Extract person names, locations, and dates from the text"
    )
    examples: Union[str, List[Dict[str, Any]]] = Field(
        default="[]",
        description="Examples of expected output format (JSON string or list)"
    )
    model_id: str = Field(
        default="gemini-2.5-flash",
        description="Language model to use for extraction"
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Temperature for model generation"
    )
    max_char_buffer: int = Field(
        default=1000,
        gt=0,
        description="Maximum characters per chunk"
    )
    max_workers: int = Field(
        default=10,
        gt=0,
        le=50,
        description="Maximum number of parallel workers"
    )
    batch_length: int = Field(
        default=10,
        gt=0,
        description="Number of documents to process in each batch"
    )
    extraction_passes: int = Field(
        default=1,
        gt=0,
        le=5,
        description="Number of extraction passes"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the model (if not set in environment)"
    )
    model_url: Optional[str] = Field(
        default=None,
        description="Custom model URL (for Ollama or custom endpoints)"
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Additional context for extraction"
    )
    format_type: str = Field(
        default="JSON",
        description="Output format type"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Optional request ID for tracking"
    )
    
    @validator('examples')
    def validate_examples(cls, v):
        """Validate and parse examples."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Examples must be valid JSON string or list")
        return v


class ExtractionResponse(BaseModel):
    """Response model for extraction results."""
    model_config = {"protected_namespaces": ()}
    
    extraction_id: str = Field(..., description="Unique extraction ID")
    status: str = Field(..., description="Extraction status")
    results: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Extracted results"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extraction metadata"
    )
    processing_time: Optional[float] = Field(
        default=None,
        description="Processing time in seconds"
    )
    model_used: Optional[str] = Field(
        default=None,
        description="Model used for extraction"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="Number of tokens used"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if extraction failed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )


class ExtractionStatus(BaseModel):
    """Status model for extraction jobs."""
    extraction_id: str
    status: str  # pending, processing, completed, failed
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    results_available: bool = False
    download_urls: Optional[Dict[str, str]] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="healthy")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)


class AuthRequest(BaseModel):
    """Authentication request model."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class ModelInfo(BaseModel):
    """Model information model."""
    model_config = {"protected_namespaces": ()}
    
    model_id: str
    provider: str  # gemini, openai, ollama
    description: str
    requires_api_key: bool
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None
    capabilities: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class FileUploadResponse(BaseModel):
    """File upload response model."""
    filename: str
    file_size: int
    content_type: str
    file_id: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchExtractionRequest(BaseModel):
    """Batch extraction request model."""
    model_config = {"protected_namespaces": ()}
    
    texts: List[str] = Field(..., min_items=1, max_items=100)
    prompt_description: str
    examples: Union[str, List[Dict[str, Any]]] = Field(default="[]")
    model_id: str = Field(default="gemini-2.5-flash")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_char_buffer: int = Field(default=1000, gt=0)
    max_workers: int = Field(default=10, gt=0, le=50)
    batch_length: int = Field(default=10, gt=0)
    extraction_passes: int = Field(default=1, gt=0, le=5)
    api_key: Optional[str] = None
    model_url: Optional[str] = None
    
    @validator('examples')
    def validate_examples(cls, v):
        """Validate and parse examples."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Examples must be valid JSON string or list")
        return v


class BatchExtractionResponse(BaseModel):
    """Batch extraction response model."""
    batch_id: str
    status: str
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    results: List[ExtractionResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None


class ConfigurationRequest(BaseModel):
    """Configuration update request model."""
    model_config = {"protected_namespaces": ()}
    
    default_model_id: Optional[str] = None
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_max_char_buffer: Optional[int] = Field(None, gt=0)
    default_max_workers: Optional[int] = Field(None, gt=0, le=50)
    max_file_size_mb: Optional[int] = Field(None, gt=0, le=1000)
    allowed_file_extensions: Optional[List[str]] = None


class ConfigurationResponse(BaseModel):
    """Configuration response model."""
    model_config = {"protected_namespaces": ()}
    
    default_model_id: str
    default_temperature: float
    default_max_char_buffer: int
    default_max_workers: int
    max_file_size_mb: int
    allowed_file_extensions: List[str]
    available_models: List[str]
    api_version: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)