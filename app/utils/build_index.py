"""Script to build the vector store index."""
import sys
import os
from pathlib import Path
import argparse

# Add the parent directory to the path so we can import our app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.vector_store import VectorStoreService
from app.core.logging import setup_logging
from app.utils.download_constitution import download_constitution
from app.core.config import settings

logger = setup_logging()

def build_vector_store(force_recreate: bool = False, download: bool = True):
    """
    Build the vector store index.
    
    Args:
        force_recreate (bool): Whether to force recreate the index
        download (bool): Whether to download the constitution files if they don't exist
    """
    logger.info("Building vector store index...")
    
    # Create vector store service
    vector_store_service = VectorStoreService()
    
    # Check if the constitution source files exist
    source_path = os.path.join(settings.CONSTITUTION_SOURCE_PATH, "Preamble.txt")
    if download and not os.path.exists(source_path):
        logger.info("Constitution source files not found. Downloading...")
        download_constitution(force=False)
    
    # Create or load the vector store
    vector_store_service.create_vector_store(force_recreate=force_recreate)
    
    logger.info("Vector store index built successfully!")
    
    # Test retrieval
    test_query = "What are the fundamental rights in the Indian Constitution?"
    logger.info(f"Testing retrieval with query: {test_query}")
    results = vector_store_service.similarity_search(test_query, k=2)
    
    for i, doc in enumerate(results):
        logger.info(f"Result {i+1}:")
        logger.info(f"Metadata: {doc.metadata}")
        logger.info(f"Content: {doc.page_content[:200]}...")
        logger.info("---")
    
    logger.info("Test completed successfully!")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Vector Store Index")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force recreate the index"
    )
    parser.add_argument(
        "--no-download", 
        dest="download",
        action="store_false", 
        help="Do not download constitution files"
    )
    
    args = parser.parse_args()
    
    build_vector_store(force_recreate=args.force, download=args.download) 