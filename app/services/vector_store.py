"""
Service to manage the vector store for the Indian Constitution.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

from langchain.schema.document import Document
from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter

from app.core.config import settings
from app.services.embeddings import ConstitutionEmbeddingService
from loguru import logger

class VectorStoreService:
    """Service to manage the vector store for the Indian Constitution."""
    
    def __init__(self):
        """Initialize the vector store service."""
        self.embedding_service = ConstitutionEmbeddingService()
        self.embedding_model = self.embedding_service.embedding_model
        self.vector_store = None
    
    def process_document_metadata(self, doc: Document) -> Document:
        """Process and enhance document metadata."""
        content = doc.page_content
        
        # Extract article numbers
        article_match = re.search(r'Article (\d+[A-Z]?)', content)
        if article_match:
            doc.metadata['article_number'] = article_match.group(1)
        
        # Extract section type
        section_matches = {
            'FUNDAMENTAL RIGHTS': 'Fundamental Rights',
            'DIRECTIVE PRINCIPLES': 'Directive Principles',
            'FUNDAMENTAL DUTIES': 'Fundamental Duties',
            'UNION GOVERNMENT': 'Union Government',
            'STATE GOVERNMENT': 'State Government',
            'JUDICIARY': 'Judiciary',
            'EMERGENCY PROVISIONS': 'Emergency Provisions'
        }
        
        for pattern, section_type in section_matches.items():
            if pattern in content.upper():
                doc.metadata['section_type'] = section_type
                break
        
        # Extract section name (first line or heading)
        lines = content.split('\n')
        if lines:
            doc.metadata['section_name'] = lines[0].strip()
        
        return doc
    
    def create_vector_store(self, force_recreate: bool = False) -> None:
        """
        Create the vector store from the constitution documents.
        
        Args:
            force_recreate (bool): Whether to force recreate the vector store
        """
        # Check if vector store already exists
        vector_store_path = settings.VECTOR_STORE_PATH
        
        if os.path.exists(vector_store_path) and not force_recreate:
            logger.info(f"Vector store already exists at {vector_store_path}")
            self.load_vector_store()
            return
        
        # Create directory if it doesn't exist
        Path(vector_store_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load and process constitution documents
        constitution_docs = self.embedding_service.load_constitution_documents()
        split_docs = self.embedding_service.split_documents(constitution_docs)
        
        logger.info(f"Creating vector store with {len(split_docs)} documents")
        
        # Process documents with enhanced metadata
        processed_docs = []
        for doc in split_docs:
            processed_doc = self.process_document_metadata(doc)
            processed_docs.append(processed_doc)
        
        # Create vector store
        if settings.VECTOR_STORE_TYPE.lower() == "faiss":
            self.vector_store = FAISS.from_documents(
                documents=processed_docs,
                embedding=self.embedding_model
            )
            # Save to disk
            self.vector_store.save_local(vector_store_path)
            logger.info(f"Created and saved FAISS vector store to {vector_store_path}")
        
        elif settings.VECTOR_STORE_TYPE.lower() == "chroma":
            self.vector_store = Chroma.from_documents(
                documents=processed_docs,
                embedding=self.embedding_model,
                persist_directory=vector_store_path
            )
            # Save to disk
            self.vector_store.persist()
            logger.info(f"Created and saved Chroma vector store to {vector_store_path}")
        
        else:
            raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}")
    
    def load_vector_store(self) -> None:
        """Load the vector store from disk."""
        vector_store_path = settings.VECTOR_STORE_PATH
        
        if not os.path.exists(vector_store_path):
            logger.warning(f"Vector store does not exist at {vector_store_path}")
            self.create_vector_store()
            return
        
        try:
            if settings.VECTOR_STORE_TYPE.lower() == "faiss":
                self.vector_store = FAISS.load_local(
                    folder_path=vector_store_path,
                    embeddings=self.embedding_model,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded FAISS vector store from {vector_store_path}")
            
            elif settings.VECTOR_STORE_TYPE.lower() == "chroma":
                self.vector_store = Chroma(
                    persist_directory=vector_store_path,
                    embedding_function=self.embedding_model
                )
                logger.info(f"Loaded Chroma vector store from {vector_store_path}")
            
            else:
                raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}")
        
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            logger.info("Creating new vector store instead")
            self.create_vector_store(force_recreate=True)
    
    def get_retriever(self, filter_threshold: float = 0.78) -> ContextualCompressionRetriever:
        """
        Get a retriever for the vector store with additional filtering.
        
        Args:
            filter_threshold (float): Similarity threshold for filtering
            
        Returns:
            ContextualCompressionRetriever: The retriever
        """
        if self.vector_store is None:
            self.load_vector_store()
        
        # Basic retriever
        base_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.NUM_RETRIEVED_DOCUMENTS}
        )
        
        # Add embeddings filter to improve relevance
        embeddings_filter = EmbeddingsFilter(
            embeddings=self.embedding_model,
            similarity_threshold=filter_threshold
        )
        
        # Create the final retriever with compression
        return ContextualCompressionRetriever(
            base_compressor=embeddings_filter,
            base_retriever=base_retriever
        )
        
    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Perform a similarity search on the vector store.
        
        Args:
            query (str): The query to search for
            k (int, optional): The number of results to return
                
        Returns:
            List[Document]: The search results
        """
        if self.vector_store is None:
            self.load_vector_store()
        
        if k is None:
            k = settings.NUM_RETRIEVED_DOCUMENTS
        
        return self.vector_store.similarity_search(query, k=k) 