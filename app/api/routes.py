"""API routes for the Indian Constitution AI application."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
from datetime import datetime
import os
import shutil
from pathlib import Path

from app.services.qa_chain import ConstitutionQAService
from app.core.config import settings
from loguru import logger

# Create a router
router = APIRouter()

# Define request and response models
class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = []

class SourceInfo(BaseModel):
    type: str
    article: str
    content: str
    page_number: Optional[Union[int, str]] = "Unknown"
    section: Optional[str] = ""

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    timestamp: str

# Create QA service instance
qa_service = ConstitutionQAService()

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question about the Indian Constitution.
    
    Args:
        request (QuestionRequest): The question request
        
    Returns:
        AnswerResponse: The answer response
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Process the question
        result = qa_service.answer_question(
            question=request.question,
            chat_history=request.chat_history
        )
        
        # Return the response
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-index")
async def build_vector_index(force: bool = False):
    """
    Build the vector index.
    
    Args:
        force (bool): Whether to force recreate the index
        
    Returns:
        dict: Status message
    """
    try:
        # Create the vector store
        qa_service.vector_store_service.create_vector_store(force_recreate=force)
        
        return {"status": "success", "message": "Vector index built successfully"}
    
    except Exception as e:
        logger.error(f"Error building vector index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def check_status():
    """
    Check the status of the API.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Indian Constitution AI"
    }

@router.post("/flush-index")
async def flush_index():
    """Remove all ingested documents and delete the vector store."""
    try:
        vector_store_path = settings.VECTOR_STORE_PATH
        vector_store_dir = str(Path(vector_store_path).parent)
        
        if os.path.exists(vector_store_dir):
            try:
                # Try to remove the entire directory
                shutil.rmtree(vector_store_dir, ignore_errors=True)
                return {
                    "status": "success",
                    "message": f"Index directory flushed successfully: {vector_store_dir}"
                }
            except Exception as e:
                logger.error(f"Error removing directory: {str(e)}")
                # If directory removal fails, try to remove individual files
                try:
                    for file in Path(vector_store_dir).glob("*"):
                        try:
                            if file.is_file():
                                file.unlink()
                            elif file.is_dir():
                                shutil.rmtree(str(file))
                        except Exception as e:
                            logger.warning(f"Could not remove {file}: {str(e)}")
                    return {
                        "status": "partial_success",
                        "message": "Some index files may remain due to permission issues"
                    }
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Could not flush index files: {str(e)}"
                    )
        
        return {
            "status": "success",
            "message": "No index found to flush"
        }
    except Exception as e:
        logger.error(f"Error flushing index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index-status")
async def get_index_status():
    """Get information about the current index status."""
    try:
        vector_store_path = settings.VECTOR_STORE_PATH
        vector_store_dir = str(Path(vector_store_path).parent)
        
        if not os.path.exists(vector_store_dir):
            return {
                "status": "not_found",
                "message": "No index found. Constitution has not been ingested yet.",
                "document_count": 0,
                "index_path": vector_store_dir
            }
        
        # Try to load the vector store
        try:
            qa_service.vector_store_service.load_vector_store()
            doc_count = len(qa_service.vector_store_service.vector_store.index_to_docstore_id) if qa_service.vector_store_service.vector_store else 0
        except Exception as e:
            logger.warning(f"Could not load vector store: {str(e)}")
            doc_count = 0
        
        # Get directory size
        total_size = 0
        try:
            for path in Path(vector_store_dir).rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
        except Exception as e:
            logger.warning(f"Could not calculate complete directory size: {str(e)}")
        
        return {
            "status": "active" if doc_count > 0 else "exists_but_empty",
            "message": "Index is active and ready" if doc_count > 0 else "Index exists but may be empty or corrupted",
            "document_count": doc_count,
            "index_path": vector_store_dir,
            "last_modified": datetime.fromtimestamp(os.path.getmtime(vector_store_dir)).isoformat(),
            "index_size_mb": total_size / (1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Error getting index status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_constitution():
    """Manually trigger constitution ingestion."""
    try:
        # Ensure the parent directory exists with proper permissions
        vector_store_dir = Path(settings.VECTOR_STORE_PATH).parent
        vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to set directory permissions if possible
        try:
            vector_store_dir.chmod(0o755)  # rwxr-xr-x
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {str(e)}")
        
        # First try to flush existing index
        try:
            await flush_index()
        except Exception as e:
            logger.warning(f"Could not flush existing index: {str(e)}")
        
        # Rebuild the index
        qa_service.vector_store_service.create_vector_store(force_recreate=True)
        
        # Get stats about the new index
        try:
            doc_count = len(qa_service.vector_store_service.vector_store.index_to_docstore_id)
        except Exception:
            doc_count = 0
        
        return {
            "status": "success",
            "message": "Constitution ingested successfully",
            "document_count": doc_count,
            "index_path": str(vector_store_dir)
        }
    except Exception as e:
        logger.error(f"Error ingesting constitution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))