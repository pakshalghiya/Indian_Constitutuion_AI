from dotenv import load_dotenv
import streamlit as st
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Indian Constitution AI"
    PROJECT_DESCRIPTION: str = "An AI-powered system for answering questions about the Indian Constitution"
    PROJECT_VERSION: str = "2.0.0"
    
    # OpenAI Configuration (for embeddings only)
    OPENAI_API_KEY: str = st.secrets["OPENAI_API_KEY"]
    EMBEDDING_MODEL: str = st.secrets["EMBEDDING_MODEL"]
    
    # Groq Configuration (for chat)
    GROQ_API_KEY: str = st.secrets["GROQ_API_KEY"]
    LLM_MODEL: str = st.secrets["LLM_MODEL"]  # Using Llama3 70B model
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = st.secrets["VECTOR_STORE_PATH"]
    VECTOR_STORE_TYPE: str = st.secrets["VECTOR_STORE_TYPE"] # or "chroma"
    
    # Source Documents Configuration
    CONSTITUTION_SOURCE_PATH: str = st.secrets["CONSTITUTION_SOURCE_PATH"]
    
    # Text Processing
    CHUNK_SIZE: int = int(st.secrets["CHUNK_SIZE"])
    CHUNK_OVERLAP: int = int(st.secrets["CHUNK_OVERLAP"])
    
    # Retrieval Configuration
    NUM_RETRIEVED_DOCUMENTS: int = int(st.secrets["NUM_RETRIEVED_DOCUMENTS"])
    
    # API Security
    CORS_ORIGINS: list = ["*"]  # For production, specify exact origins
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create a settings instance
settings = Settings() 