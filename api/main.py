#!/usr/bin/env python3
"""LangExtract FastAPI Application."""

import os
import sys
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import jwt
from dotenv import load_dotenv
import uvicorn
import requests

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import langextract as lx

# Configuration from environment
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-key-here')
API_ALGORITHM = os.getenv('API_ALGORITHM', 'HS256')
API_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('API_ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
API_ACCESS_TOKEN = os.getenv('API_ACCESS_TOKEN', 'your-api-access-token-here')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-2.5-flash')
DEFAULT_PROVIDER = os.getenv('DEFAULT_PROVIDER', 'gemini')
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.3'))
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
ALLOWED_FILE_EXTENSIONS = os.getenv('ALLOWED_FILE_EXTENSIONS', '.txt,.pdf,.docx,.md,.json').split(',')
API_PORT = int(os.getenv('API_PORT', '8001'))
API_HOST = os.getenv('API_HOST', '0.0.0.0')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '300'))
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '180'))

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
ALLOWED_METHODS = os.getenv('ALLOWED_METHODS', 'GET,POST,PUT,DELETE').split(',')
ALLOWED_HEADERS = os.getenv('ALLOWED_HEADERS', '*').split(',')

# Provider URL mapping
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
GEMINI_BASE_URL = os.getenv('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
CLOUDFLARE_BASE_URL = os.getenv('CLOUDFLARE_BASE_URL', 'https://api.cloudflare.com/client/v4/accounts')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN', '')

PROVIDER_URLS = {
    'ollama': OLLAMA_BASE_URL,
    'openai': OPENAI_BASE_URL,
    'gemini': GEMINI_BASE_URL,
    'cloudflare': f'{CLOUDFLARE_BASE_URL}/{CLOUDFLARE_ACCOUNT_ID}/ai/run'
}

# FastAPI app initialization
app = FastAPI(
    title="LangExtract API",
    description="API for structured data extraction from text using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

# Security
security = HTTPBearer()

# Pydantic models
class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class ExtractionAttribute(BaseModel):
    """Attributes for an extraction."""
    key: str
    value: str

class ExtractionExample(BaseModel):
    """Example extraction for few-shot learning."""
    text: str
    extractions: List[Dict[str, Any]]

class ExtractionRequest(BaseModel):
    """Request model for text extraction."""
    text: str = Field(..., description="Text to extract from")
    prompt: str = Field(..., description="Extraction prompt/instructions")
    model_id: Optional[str] = Field(DEFAULT_MODEL, description="LLM model to use")
    temperature: Optional[float] = Field(DEFAULT_TEMPERATURE, description="Model temperature")
    examples: Optional[List[ExtractionExample]] = Field(None, description="Few-shot examples")
    schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for extraction")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    provider_url: Optional[str] = Field(None, description="Custom provider URL")

class ExtractionResponse(BaseModel):
    """Response model for extraction results."""
    success: bool
    extractions: List[Dict[str, Any]]
    model_used: str
    provider: str
    processing_time: float
    token_usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    available_models: Dict[str, List[str]]

# Utility functions
async def extract_with_langextract(text: str, prompt: str, model_id: str, temperature: float = 0.3) -> Dict[str, Any]:
    """Extract structured data using LangExtract"""
    try:
        start_time = datetime.utcnow()
        
        # Check if it's a Cloudflare model
        provider = determine_provider(model_id)
        if provider == "cloudflare":
            cf_result = await extract_with_cloudflare(text, prompt, model_id, temperature)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            cf_result.update({
                "model_used": model_id,
                "provider": provider,
                "processing_time": round(processing_time, 2)
            })
            return cf_result
        
        # Use LangExtract for other providers
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            model_id=model_id,
            temperature=temperature,
        )
        
        # Process results
        extractions = []
        for extraction in result.extractions:
            extractions.append({
                "class": extraction.extraction_class,
                "text": extraction.extraction_text,
                "attributes": extraction.attributes or {}
            })
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "success": True,
            "extractions": extractions,
            "model_used": model_id,
            "provider": provider,
            "processing_time": round(processing_time, 2),
            "error": None
        }
        
    except asyncio.TimeoutError:
        return {
            "success": False,
            "extractions": [],
            "model_used": model_id,
            "provider": determine_provider(model_id),
            "processing_time": LLM_TIMEOUT,
            "error": f"Request timed out after {LLM_TIMEOUT} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "extractions": [],
            "model_used": model_id,
            "provider": determine_provider(model_id),
            "processing_time": 0,
            "error": str(e)
        }

async def extract_with_cloudflare(text: str, prompt: str, model_id: str, temperature: float = 0.3) -> Dict[str, Any]:
    """Extract using Cloudflare Workers AI"""
    try:
        url = f"{CLOUDFLARE_BASE_URL}/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model_id}"
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Format prompt for extraction
        full_prompt = f"{prompt}\n\nText to analyze:\n{text}"
        
        payload = {
            "prompt": full_prompt,
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)
            
        if response.status_code == 200:
            result = response.json()
            # Extract the response text
            extracted_text = result.get("result", {}).get("response", "")
            
            # Try to parse as structured data (basic implementation)
            extractions = []
            if extracted_text:
                extractions.append({
                    "class": "extracted_data",
                    "text": extracted_text,
                    "attributes": {}
                })
            
            return {
                "success": True,
                "extractions": extractions,
                "raw_response": extracted_text
            }
        else:
            raise Exception(f"Cloudflare API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        return {
            "success": False,
            "extractions": [],
            "error": str(e)
        }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, API_SECRET_KEY, algorithms=[API_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def determine_provider(model_id: str) -> str:
    """Determine provider based on model ID."""
    model_lower = model_id.lower()
    
    if any(x in model_lower for x in ['gpt', 'openai']):
        return 'openai'
    elif any(x in model_lower for x in ['gemini', 'palm']):
        return 'gemini'
    elif model_id.startswith('@cf/'):
        return 'cloudflare'
    elif any(x in model_lower for x in ['llama', 'mistral', 'tinyllama', 'codellama']):
        return 'ollama'
    else:
        # Default to ollama for unknown models (assume local)
        return 'ollama'

def get_available_models() -> Dict[str, List[str]]:
    """Get available models from different providers."""
    models = {
        'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'gemini': ['gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash'],
        'ollama': [],
        'cloudflare': [
            '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
            '@cf/meta/llama-3.1-70b-instruct',
            '@cf/meta/llama-3.1-8b-instruct',
            '@cf/mistral/mistral-7b-instruct-v0.1',
            '@cf/microsoft/phi-2',
            '@cf/qwen/qwen1.5-14b-chat-awq'
        ]
    }
    
    # Try to get Ollama models
    try:
        ollama_url = PROVIDER_URLS['ollama']
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_models = response.json().get('models', [])
            models['ollama'] = [model.get('name', '') for model in ollama_models]
    except Exception:
        models['ollama'] = ['Connection failed']
    
    return models

def process_file_content(file_content: bytes, filename: str) -> str:
    """Process uploaded file content and extract text."""
    file_ext = Path(filename).suffix.lower()
    
    if file_ext == '.txt':
        return file_content.decode('utf-8')
    elif file_ext == '.md':
        return file_content.decode('utf-8')
    elif file_ext == '.json':
        import json
        data = json.loads(file_content.decode('utf-8'))
        return json.dumps(data, indent=2)
    elif file_ext == '.pdf':
        # TODO: Implement PDF processing
        raise HTTPException(status_code=400, detail="PDF processing not yet implemented")
    elif file_ext == '.docx':
        # TODO: Implement DOCX processing
        raise HTTPException(status_code=400, detail="DOCX processing not yet implemented")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "LangExtract API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        available_models=get_available_models()
    )

@app.post("/auth/token", response_model=Token)
async def login(username: str = Form(...), password: str = Form(...)):
    """Generate access token."""
    # Simple authentication - in production, verify against database
    if username == "admin" and password == "admin":
        access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=API_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/extract", response_model=ExtractionResponse)
async def extract_from_text(
    request: ExtractionRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Extract structured data from text."""
    start_time = datetime.utcnow()
    
    try:
        # Determine provider
        provider = determine_provider(request.model_id)
        
        # Prepare examples for LangExtract
        examples = []
        if request.examples:
            for example in request.examples:
                extractions = []
                for ext in example.extractions:
                    extractions.append(
                        lx.data.Extraction(
                            extraction_class=ext.get('class', ''),
                            extraction_text=ext.get('text', ''),
                            attributes=ext.get('attributes', {})
                        )
                    )
                examples.append(
                    lx.data.ExampleData(
                        text=example.text,
                        extractions=extractions
                    )
                )
        
        # Perform extraction
        result = lx.extract(
            text_or_documents=request.text,
            prompt_description=request.prompt,
            examples=examples,
            model_id=request.model_id,
            temperature=request.temperature,
        )
        
        # Process results
        extractions = []
        for extraction in result.extractions:
            extractions.append({
                "class": extraction.extraction_class,
                "text": extraction.extraction_text,
                "attributes": extraction.attributes or {}
            })
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ExtractionResponse(
            success=True,
            extractions=extractions,
            model_used=request.model_id,
            provider=provider,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        return ExtractionResponse(
            success=False,
            extractions=[],
            model_used=request.model_id,
            provider=determine_provider(request.model_id),
            processing_time=processing_time,
            error=str(e)
        )

@app.post("/extract/file", response_model=ExtractionResponse)
async def extract_from_file(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    model_id: str = Form(DEFAULT_MODEL),
    temperature: float = Form(DEFAULT_TEMPERATURE),
    token_data: TokenData = Depends(verify_token)
):
    """Extract structured data from uploaded file."""
    start_time = datetime.utcnow()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not allowed. Allowed types: {ALLOWED_FILE_EXTENSIONS}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )
    
    try:
        # Process file content
        text_content = process_file_content(file_content, file.filename)
        
        # Determine provider
        provider = determine_provider(model_id)
        
        # Perform extraction
        result = lx.extract(
            text_or_documents=text_content,
            prompt_description=prompt,
            model_id=model_id,
            temperature=temperature,
        )
        
        # Process results
        extractions = []
        for extraction in result.extractions:
            extractions.append({
                "class": extraction.extraction_class,
                "text": extraction.extraction_text,
                "attributes": extraction.attributes or {}
            })
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ExtractionResponse(
            success=True,
            extractions=extractions,
            model_used=model_id,
            provider=provider,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        return ExtractionResponse(
            success=False,
            extractions=[],
            model_used=model_id,
            provider=determine_provider(model_id),
            processing_time=processing_time,
            error=str(e)
        )

@app.get("/models", response_model=Dict[str, List[str]])
async def get_models(token_data: TokenData = Depends(verify_token)):
    """Get available models from all providers."""
    return get_available_models()

@app.get("/providers", response_model=Dict[str, str])
async def get_providers(token_data: TokenData = Depends(verify_token)):
    """Get available providers and their URLs."""
    return PROVIDER_URLS

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )