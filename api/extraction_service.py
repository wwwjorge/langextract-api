"""Extraction service for LangExtract API."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

import structlog
from langextract import extract
from langextract.factory import ModelConfig, create_model

from api.models import ExtractionRequest, ExtractionResponse, ExtractionStatus
from api.config import get_settings
from api.auth import get_api_key_for_provider

logger = structlog.get_logger()


class ExtractionService:
    """Service for handling text extraction using LangExtract."""
    
    def __init__(self):
        self.settings = get_settings()
        self.active_extractions: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.settings.max_concurrent_extractions)
    
    async def extract_from_text(self, request: ExtractionRequest) -> ExtractionResponse:
        """Extract structured information from text."""
        extraction_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Store extraction info
        self.active_extractions[extraction_id] = {
            "status": "processing",
            "created_at": start_time,
            "request": request,
            "progress": 0.0
        }
        
        try:
            logger.info(
                "Starting extraction",
                extraction_id=extraction_id,
                model_id=request.model_id,
                text_length=len(request.text)
            )
            
            # Prepare extraction parameters
            extraction_params = await self._prepare_extraction_params(request)
            
            # Update progress
            self.active_extractions[extraction_id]["progress"] = 10.0
            
            # Run extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor,
                self._run_extraction,
                extraction_params
            )
            
            # Update progress
            self.active_extractions[extraction_id]["progress"] = 90.0
            
            # Process results
            processed_results = self._process_results(results)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update extraction status
            self.active_extractions[extraction_id].update({
                "status": "completed",
                "results": processed_results,
                "completed_at": datetime.utcnow(),
                "progress": 100.0
            })
            
            # Save results to file
            await self._save_results(extraction_id, processed_results)
            
            logger.info(
                "Extraction completed",
                extraction_id=extraction_id,
                processing_time=processing_time,
                results_count=len(processed_results) if processed_results else 0
            )
            
            return ExtractionResponse(
                extraction_id=extraction_id,
                status="completed",
                results=processed_results,
                metadata={
                    "text_length": len(request.text),
                    "model_id": request.model_id,
                    "temperature": request.temperature,
                    "max_char_buffer": request.max_char_buffer,
                    "extraction_passes": request.extraction_passes
                },
                processing_time=processing_time,
                model_used=request.model_id,
                created_at=start_time
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Extraction failed",
                extraction_id=extraction_id,
                error=error_msg,
                traceback=traceback.format_exc()
            )
            
            # Update extraction status
            self.active_extractions[extraction_id].update({
                "status": "failed",
                "error": error_msg,
                "completed_at": datetime.utcnow(),
                "progress": 0.0
            })
            
            return ExtractionResponse(
                extraction_id=extraction_id,
                status="failed",
                error=error_msg,
                metadata={
                    "text_length": len(request.text),
                    "model_id": request.model_id
                },
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                model_used=request.model_id,
                created_at=start_time
            )
    
    async def _prepare_extraction_params(self, request: ExtractionRequest) -> Dict[str, Any]:
        """Prepare parameters for LangExtract."""
        # Get API key for the provider
        provider = self._get_provider_from_model(request.model_id)
        api_key = request.api_key or get_api_key_for_provider(provider)
        
        # Prepare examples
        examples = request.examples
        if isinstance(examples, str):
            try:
                examples = json.loads(examples)
            except json.JSONDecodeError:
                examples = []
        
        # Base parameters
        params = {
            "text_or_documents": request.text,
            "prompt_description": request.prompt_description,
            "examples": examples,
            "model_id": request.model_id,
            "temperature": request.temperature,
            "max_char_buffer": request.max_char_buffer,
            "max_workers": request.max_workers,
            "batch_length": request.batch_length,
            "extraction_passes": request.extraction_passes,
            "format_type": request.format_type,
            "debug": request.debug
        }
        
        # Add API key if available
        if api_key:
            params["api_key"] = api_key
        
        # Add model URL for Ollama
        if provider == "ollama":
            params["model_url"] = request.model_url or self.settings.ollama_base_url
        
        # Add additional context if provided
        if request.additional_context:
            params["additional_context"] = request.additional_context
        
        return params
    
    def _run_extraction(self, params: Dict[str, Any]) -> Any:
        """Run the actual extraction (blocking operation)."""
        try:
            return extract(**params)
        except Exception as e:
            logger.error("LangExtract execution failed", error=str(e))
            raise
    
    def _process_results(self, results: Any) -> List[Dict[str, Any]]:
        """Process and normalize extraction results."""
        if results is None:
            return []
        
        # Handle different result formats
        if isinstance(results, list):
            return [self._normalize_result(result) for result in results]
        elif isinstance(results, dict):
            return [self._normalize_result(results)]
        else:
            # Try to convert to dict
            try:
                if hasattr(results, '__dict__'):
                    return [self._normalize_result(results.__dict__)]
                else:
                    return [{"result": str(results)}]
            except Exception:
                return [{"result": str(results)}]
    
    def _normalize_result(self, result: Any) -> Dict[str, Any]:
        """Normalize a single result to a dictionary."""
        if isinstance(result, dict):
            return result
        elif hasattr(result, '__dict__'):
            return result.__dict__
        else:
            return {"value": result}
    
    def _get_provider_from_model(self, model_id: str) -> str:
        """Determine provider from model ID."""
        if model_id.startswith("gpt-") or model_id.startswith("text-"):
            return "openai"
        elif model_id.startswith("gemini-"):
            return "gemini"
        elif ":" in model_id:  # Ollama format
            return "ollama"
        else:
            return "gemini"  # Default
    
    async def _save_results(self, extraction_id: str, results: List[Dict[str, Any]]):
        """Save extraction results to files."""
        try:
            output_dir = self.settings.outputs_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as JSON
            json_path = os.path.join(output_dir, f"{extraction_id}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            # Save as JSONL
            jsonl_path = os.path.join(output_dir, f"{extraction_id}.jsonl")
            with open(jsonl_path, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(json.dumps(result, ensure_ascii=False, default=str) + '\n')
            
            logger.info(
                "Results saved",
                extraction_id=extraction_id,
                json_path=json_path,
                jsonl_path=jsonl_path
            )
            
        except Exception as e:
            logger.error(
                "Failed to save results",
                extraction_id=extraction_id,
                error=str(e)
            )
    
    async def get_extraction_status(self, extraction_id: str) -> Optional[ExtractionStatus]:
        """Get status of an extraction job."""
        extraction_info = self.active_extractions.get(extraction_id)
        if not extraction_info:
            return None
        
        # Check if results are available
        results_available = extraction_info["status"] == "completed"
        download_urls = None
        
        if results_available:
            download_urls = {
                "json": f"/extract/{extraction_id}/download?format=json",
                "jsonl": f"/extract/{extraction_id}/download?format=jsonl"
            }
        
        return ExtractionStatus(
            extraction_id=extraction_id,
            status=extraction_info["status"],
            progress=extraction_info.get("progress", 0.0),
            message=extraction_info.get("error"),
            created_at=extraction_info["created_at"],
            updated_at=extraction_info.get("completed_at", extraction_info["created_at"]),
            completed_at=extraction_info.get("completed_at"),
            results_available=results_available,
            download_urls=download_urls
        )
    
    async def get_result_file(self, extraction_id: str, format: str = "json") -> Optional[str]:
        """Get path to result file."""
        if format not in ["json", "jsonl", "html"]:
            raise ValueError(f"Unsupported format: {format}")
        
        output_dir = self.settings.outputs_dir
        
        if format == "html":
            # Generate HTML visualization if not exists
            html_path = os.path.join(output_dir, f"{extraction_id}.html")
            if not os.path.exists(html_path):
                await self._generate_html_visualization(extraction_id)
            return html_path if os.path.exists(html_path) else None
        else:
            file_path = os.path.join(output_dir, f"{extraction_id}.{format}")
            return file_path if os.path.exists(file_path) else None
    
    async def _generate_html_visualization(self, extraction_id: str):
        """Generate HTML visualization of results."""
        try:
            json_path = os.path.join(self.settings.outputs_dir, f"{extraction_id}.json")
            if not os.path.exists(json_path):
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            html_content = self._create_html_visualization(results, extraction_id)
            
            html_path = os.path.join(self.settings.outputs_dir, f"{extraction_id}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("HTML visualization generated", extraction_id=extraction_id)
            
        except Exception as e:
            logger.error(
                "Failed to generate HTML visualization",
                extraction_id=extraction_id,
                error=str(e)
            )
    
    def _create_html_visualization(self, results: List[Dict[str, Any]], extraction_id: str) -> str:
        """Create HTML visualization of extraction results."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extraction Results - {extraction_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .result-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .result-index {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }}
        .key {{
            font-weight: bold;
            color: #555;
            margin-right: 10px;
        }}
        .value {{
            color: #333;
        }}
        .json-view {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Extraction Results</h1>
        <p>Extraction ID: {extraction_id}</p>
        <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(results)}</div>
            <div class="stat-label">Total Results</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(str(type(r)) for r in results))}</div>
            <div class="stat-label">Result Types</div>
        </div>
    </div>
    
    <div class="results">
"""
        
        for i, result in enumerate(results, 1):
            html += f"""
        <div class="result-card">
            <div class="result-index">Result #{i}</div>
            <div class="json-view">{json.dumps(result, indent=2, ensure_ascii=False, default=str)}</div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def cleanup_old_extractions(self, days: int = None):
        """Clean up old extraction data."""
        if days is None:
            days = self.settings.cleanup_old_files_days
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Clean up in-memory data
        to_remove = []
        for extraction_id, info in self.active_extractions.items():
            if info["created_at"] < cutoff_time:
                to_remove.append(extraction_id)
        
        for extraction_id in to_remove:
            del self.active_extractions[extraction_id]
        
        # Clean up files
        try:
            output_dir = self.settings.outputs_dir
            if os.path.exists(output_dir):
                for filename in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            logger.info("Cleaned up old file", file_path=file_path)
        
        except Exception as e:
            logger.error("Failed to cleanup old files", error=str(e))
        
        logger.info(
            "Cleanup completed",
            removed_extractions=len(to_remove),
            cutoff_days=days
        )