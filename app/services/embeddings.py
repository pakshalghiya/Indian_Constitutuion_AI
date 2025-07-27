"""
Service to handle text embeddings for the Indian Constitution.
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import glob

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema.document import Document

from app.core.config import settings
from loguru import logger

class ConstitutionEmbeddingService:
    """Service to handle document embeddings for the Indian Constitution."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.embedding_model = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_constitution_documents(self) -> List[Document]:
        """
        Load all constitution documents from the source directory.
        
        Returns:
            List[Document]: A list of Document objects containing the content
        """
        constitution_docs = []
        source_path = settings.CONSTITUTION_SOURCE_PATH
        
        logger.info(f"Loading constitution documents from {source_path}")
        
        # Load all parts of the constitution
        for file_path in glob.glob(f"{source_path}/PART*.txt"):
            part_name = os.path.basename(file_path).replace(".txt", "")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                constitution_docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "section_type": "Part",
                            "section_name": part_name
                        }
                    )
                )
                logger.debug(f"Loaded {part_name} with {len(content)} characters")
        
        # Load the preamble
        preamble_path = f"{source_path}/Preamble.txt"
        if os.path.exists(preamble_path):
            with open(preamble_path, "r", encoding="utf-8") as f:
                content = f.read()
                constitution_docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": preamble_path,
                            "section_type": "Preamble",
                            "section_name": "Preamble"
                        }
                    )
                )
                logger.debug(f"Loaded Preamble with {len(content)} characters")
        
        # Load all schedules
        for file_path in glob.glob(f"{source_path}/SCHEDULE*.txt"):
            schedule_name = os.path.basename(file_path).replace(".txt", "")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                constitution_docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "section_type": "Schedule",
                            "section_name": schedule_name
                        }
                    )
                )
                logger.debug(f"Loaded {schedule_name} with {len(content)} characters")
        
        logger.info(f"Loaded {len(constitution_docs)} constitution documents")
        return constitution_docs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split the documents into smaller chunks for embedding.
        
        Args:
            documents (List[Document]): The documents to split
            
        Returns:
            List[Document]: The split documents
        """
        logger.info(f"Splitting {len(documents)} documents into smaller chunks")
        split_docs = self.text_splitter.split_documents(documents)
        
        # Enhance metadata for each split document
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = i
            
            # Extract article numbers or section numbers where possible
            content = doc.page_content.lower()
            if "article" in content and any(str(num) in content for num in range(1, 400)):
                # Try to extract article numbers mentioned in the text
                for num in range(1, 400):
                    if f"article {num}" in content or f"article {num}." in content:
                        doc.metadata["article_number"] = num
                        break
        
        logger.info(f"Split into {len(split_docs)} chunks")
        return split_docs 