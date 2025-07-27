"""Test cases for the QA service."""
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.qa_chain import ConstitutionQAService
from app.services.vector_store import VectorStoreService
from langchain.schema.document import Document

class TestQAService:
    """Test cases for the QA service."""
    
    @pytest.fixture
    def mock_vector_store_service(self):
        """Mock the vector store service."""
        mock_service = MagicMock(spec=VectorStoreService)
        
        # Create mock documents for search results
        mock_docs = [
            Document(
                page_content="Article 14 - The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                metadata={
                    "source": "app/data/constitution/source/PART03.txt",
                    "section_type": "Part",
                    "section_name": "PART03",
                    "article_number": 14,
                    "chunk_id": 0
                }
            ),
            Document(
                page_content="Article 15 - The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.",
                metadata={
                    "source": "app/data/constitution/source/PART03.txt",
                    "section_type": "Part",
                    "section_name": "PART03",
                    "article_number": 15,
                    "chunk_id": 1
                }
            )
        ]
        
        # Set up mock methods
        mock_service.similarity_search.return_value = mock_docs
        
        # Mock retriever
        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = mock_docs
        mock_service.get_retriever.return_value = mock_retriever
        
        return mock_service
    
    @patch('app.services.qa_chain.ChatOpenAI')
    def test_extract_sources(self, mock_chat_openai, mock_vector_store_service):
        """Test the extract_sources method."""
        # Create the service with the mock
        qa_service = ConstitutionQAService()
        qa_service.vector_store_service = mock_vector_store_service
        
        # Create mock documents
        mock_docs = [
            Document(
                page_content="Article 14 - The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                metadata={
                    "source": "app/data/constitution/source/PART03.txt",
                    "section_type": "Part",
                    "section_name": "PART03",
                    "article_number": 14,
                    "chunk_id": 0
                }
            ),
            Document(
                page_content="Article 15 - The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.",
                metadata={
                    "source": "app/data/constitution/source/PART03.txt",
                    "section_type": "Part",
                    "section_name": "PART03",
                    "article_number": 15,
                    "chunk_id": 1
                }
            ),
            # Duplicate to test deduplication
            Document(
                page_content="Article 14 - The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                metadata={
                    "source": "app/data/constitution/source/PART03.txt",
                    "section_type": "Part",
                    "section_name": "PART03",
                    "article_number": 14,
                    "chunk_id": 2
                }
            )
        ]
        
        # Extract sources
        sources = qa_service.extract_sources(mock_docs)
        
        # Assertions
        assert len(sources) == 2  # Should deduplicate
        assert sources[0]["type"] == "Part"
        assert sources[0]["name"] == "PART03"
        assert sources[0]["article"] == 14
        assert "Article 14" in sources[0]["content"]
        
        assert sources[1]["type"] == "Part"
        assert sources[1]["name"] == "PART03"
        assert sources[1]["article"] == 15
        assert "Article 15" in sources[1]["content"] 