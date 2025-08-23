"""FastAPI application for LangExtract API."""

import os
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
import structlog

from api.models import (
    ExtractionRequest,
    ExtractionResponse,
    HealthResponse,
    AuthRequest,
    AuthResponse,
    ModelInfo,
    ExtractionStatus
)
from api.auth import authenticate_token, create_access_token
from api.extraction_service import ExtractionService
from api.file_handler import FileHandler
from api.config import get_settings

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize services
settings = get_settings()
extraction_service = ExtractionService()
file_handler = FileHandler()
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting LangExtract API")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    logger.info("Shutting down LangExtract API")


# Create FastAPI app
app = FastAPI(
    title="LangExtract API",
    description="API for extracting structured information from text using LLMs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=None  # Will be set by the model
    )


@app.post("/auth/token", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """Authenticate and get access token."""
    # Simple authentication - in production, use proper user management
    if auth_request.username == "admin" and auth_request.password == "admin":
        access_token = create_access_token(data={"sub": auth_request.username})
        return AuthResponse(access_token=access_token, token_type="bearer")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/models", response_model=List[ModelInfo])
async def get_available_models(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get list of available models."""
    await authenticate_token(credentials.credentials)
    
    return [
        ModelInfo(
            model_id="gemini-2.5-flash",
            provider="gemini",
            description="Fast and efficient Gemini model",
            requires_api_key=True
        ),
        ModelInfo(
            model_id="gemini-2.5-pro",
            provider="gemini",
            description="Advanced Gemini model for complex tasks",
            requires_api_key=True
        ),
        ModelInfo(
            model_id="gpt-4o",
            provider="openai",
            description="OpenAI GPT-4 Omni model",
            requires_api_key=True
        ),
        ModelInfo(
            model_id="gpt-4o-mini",
            provider="openai",
            description="Smaller, faster GPT-4 model",
            requires_api_key=True
        ),
        ModelInfo(
            model_id="llama3.2:1b",
            provider="ollama",
            description="Local Llama 3.2 1B model",
            requires_api_key=False
        ),
        ModelInfo(
            model_id="gemma2:2b",
            provider="ollama",
            description="Local Gemma 2 2B model",
            requires_api_key=False
        ),
    ]


@app.post("/extract", response_model=ExtractionResponse)
async def extract_from_text(
    request: ExtractionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Extract structured information from text."""
    await authenticate_token(credentials.credentials)
    
    try:
        result = await extraction_service.extract_from_text(request)
        return result
    except Exception as e:
        logger.error("Extraction failed", error=str(e), request_id=getattr(request, 'request_id', None))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


@app.post("/extract/file", response_model=ExtractionResponse)
async def extract_from_file(
    file: UploadFile = File(...),
    model_id: str = "gemini-2.5-flash",
    prompt_description: str = "Extract key information from the document",
    examples: str = "[]",  # JSON string of examples
    temperature: float = 0.3,
    max_char_buffer: int = 1000,
    max_workers: int = 10,
    batch_length: int = 10,
    extraction_passes: int = 1,
    api_key: str = None,
    model_url: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Extract structured information from uploaded file."""
    await authenticate_token(credentials.credentials)
    
    try:
        # Handle file upload
        file_content = await file_handler.process_upload(file)
        
        # Create extraction request
        request = ExtractionRequest(
            text=file_content,
            prompt_description=prompt_description,
            examples=examples,
            model_id=model_id,
            temperature=temperature,
            max_char_buffer=max_char_buffer,
            max_workers=max_workers,
            batch_length=batch_length,
            extraction_passes=extraction_passes,
            api_key=api_key,
            model_url=model_url
        )
        
        result = await extraction_service.extract_from_text(request)
        return result
        
    except Exception as e:
        logger.error("File extraction failed", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File extraction failed: {str(e)}"
        )


@app.get("/extract/{extraction_id}/status", response_model=ExtractionStatus)
async def get_extraction_status(
    extraction_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get status of an extraction job."""
    await authenticate_token(credentials.credentials)
    
    status_info = await extraction_service.get_extraction_status(extraction_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction not found"
        )
    
    return status_info


@app.get("/extract/{extraction_id}/download")
async def download_extraction_result(
    extraction_id: str,
    format: str = "jsonl",  # jsonl, html, json
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Download extraction results."""
    await authenticate_token(credentials.credentials)
    
    try:
        file_path = await extraction_service.get_result_file(extraction_id, format)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result file not found"
            )
        
        return FileResponse(
            path=file_path,
            filename=f"extraction_{extraction_id}.{format}",
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error("Download failed", error=str(e), extraction_id=extraction_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)