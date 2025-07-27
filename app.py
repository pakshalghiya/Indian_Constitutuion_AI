from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from groq import Groq
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle
import shutil
import re
import streamlit as st

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Indian Constitution AI",
    description="An AI-powered API for answering questions about the Indian Constitution",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API keys from environment variables
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Define request and response models
class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = []

class AnswerResponse(BaseModel):
    answer: str
    sources: List[dict]  # Will contain page numbers and relevant sections
    timestamp: str

# System prompt to guide the AI
SYSTEM_PROMPT = """
You are ConstitutionGPT, an expert AI assistant specializing in the Indian Constitution.
Your purpose is to provide accurate, detailed, and helpful information about:
- The history and development of the Indian Constitution
- Constitutional articles, amendments, and their interpretations
- Fundamental Rights, Directive Principles, and Fundamental Duties
- The structure of government (Executive, Legislative, Judicial)
- Constitutional bodies and their functions
- Important Supreme Court judgments related to constitutional matters
- Recent constitutional developments and debates

Always cite specific articles, amendments, or court cases when relevant.
If you're unsure about any information, acknowledge the limitations of your knowledge.
Maintain a respectful, educational tone and avoid political bias.
"""

@app.get("/")
async def root():
    return {"message": "Welcome to the Indian Constitution AI API. Use /ask endpoint to ask questions."}

# Add new endpoints for index management
@app.post("/flush-index")
async def flush_index():
    """Remove all ingested documents and delete the vector store."""
    try:
        vector_store_files = [
            "constitution_vectorstore.pkl",
            "faiss.index",
            "index_metadata.json"
        ]
        
        files_removed = []
        for file in vector_store_files:
            if os.path.exists(file):
                os.remove(file)
                files_removed.append(file)
        
        return {
            "status": "success",
            "message": f"Index flushed successfully. Removed files: {files_removed}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error flushing index: {str(e)}")

@app.get("/index-status")
async def get_index_status():
    """Get information about the current index status."""
    try:
        if not os.path.exists("constitution_vectorstore.pkl"):
            return {
                "status": "not_found",
                "message": "No index found. Constitution has not been ingested yet.",
                "document_count": 0
            }
        
        with open("constitution_vectorstore.pkl", "rb") as f:
            vectorstore = pickle.load(f)
            
        # Get index statistics
        index_stats = {
            "status": "active",
            "message": "Index is active and ready",
            "document_count": len(vectorstore.index_to_docstore_id),
            "last_modified": datetime.fromtimestamp(os.path.getmtime("constitution_vectorstore.pkl")).isoformat(),
            "index_size_mb": os.path.getsize("constitution_vectorstore.pkl") / (1024 * 1024)
        }
        
        return index_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting index status: {str(e)}")

@app.post("/ingest")
async def ingest_constitution():
    """Manually trigger constitution ingestion."""
    try:
        if not os.path.exists("20240716890312078.pdf"):
            raise HTTPException(status_code=404, detail="Constitution PDF not found")
        
        # First flush any existing index
        await flush_index()
        
        # Process and index the constitution
        vectorstore = process_constitution_pdf("20240716890312078.pdf")
        
        return {
            "status": "success",
            "message": "Constitution ingested successfully",
            "document_count": len(vectorstore.index_to_docstore_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting constitution: {str(e)}")

# Modify the process_constitution_pdf function to be more verbose
def process_constitution_pdf(pdf_path: str):
    """Process and index the Constitution PDF with enhanced metadata extraction and logging."""
    logger.info(f"Starting to process PDF: {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    logger.info(f"Loaded {len(pages)} pages from PDF")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ".", " "]
    )
    
    # Enhanced metadata extraction with logging
    processed_pages = []
    for i, page in enumerate(pages):
        # Extract article numbers
        article_match = re.search(r'Article (\d+)', page.page_content)
        if article_match:
            page.metadata['article_number'] = article_match.group(1)
        
        # Extract section titles
        section_match = re.search(r'^([A-Z\s]+)$', page.page_content, re.MULTILINE)
        if section_match:
            page.metadata['section_title'] = section_match.group(1)
        
        page.metadata['page_number'] = i + 1
        processed_pages.append(page)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1} pages...")
    
    splits = text_splitter.split_documents(processed_pages)
    logger.info(f"Created {len(splits)} text chunks for indexing")
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)
    logger.info(f"Created vector store with {len(vectorstore.index_to_docstore_id)} documents")
    
    # Save with metadata
    with open("constitution_vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)
    
    logger.info("Vector store saved successfully")
    return vectorstore

# Update the ask_question endpoint to better handle sources
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        logger.info(f"Received question: {request.question}")
        
        # Check if index exists
        if not os.path.exists("constitution_vectorstore.pkl"):
            raise HTTPException(
                status_code=400,
                detail="Constitution has not been indexed yet. Please ingest the document first."
            )
        
        with open("constitution_vectorstore.pkl", "rb") as f:
            vectorstore = pickle.load(f)
        
        # Get relevant documents with scores
        search_results = vectorstore.similarity_search_with_score(
            request.question,
            k=5
        )
        
        # Format sources with more detail
        sources = []
        context_parts = []
        
        for doc, score in search_results:
            source = {
                "page_number": doc.metadata.get("page_number", "Unknown"),
                "article_number": doc.metadata.get("article_number", "N/A"),
                "section_title": doc.metadata.get("section_title", "N/A"),
                "excerpt": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "relevance_score": float(score)
            }
            sources.append(source)
            context_parts.append(f"[Page {source['page_number']}, Article {source['article_number']}]: {source['excerpt']}")
        
        context = "\n\n".join(context_parts)
        
        # Prepare messages for the model
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""
Based on the following sections from the Indian Constitution, answer this question: {request.question}

Relevant sections:
{context}
 
Please provide a detailed answer and cite specific articles, sections, or pages when possible.
"""}
        ]
        
        # Call the Groq API
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = chat_completion.choices[0].message.content
        
        return AnswerResponse(
            answer=answer,
            sources=sources,  # Now includes more detailed source information
            timestamp=datetime.now().isoformat(),
            confidence_score=confidence_score
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn app:app --reload