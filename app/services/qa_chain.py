"""
Service to handle QA chains for the Indian Constitution.
"""
from typing import Dict, List, Any, Optional
import re

from langchain.schema.document import Document
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.services.vector_store import VectorStoreService
from loguru import logger

# System message for the LLM
CONSTITUTION_SYSTEM_PROMPT = """You are ConstitutionGPT, an expert AI assistant specializing in the Indian Constitution.
Your purpose is to provide accurate, detailed, and helpful information based ONLY on the Indian Constitution.

When answering questions, follow these guidelines:
1. Base your answers exclusively on the Indian Constitution and related jurisprudence
2. Always cite specific articles, amendments, or sections when relevant
3. If a topic isn't covered in the provided context, acknowledge the limitations and do not make up information
4. Maintain a respectful, educational tone and avoid political bias
5. If you're unsure about any information, acknowledge the limitations of your knowledge
6. Structure your responses clearly, using headings and bullet points when appropriate
7. When quoting from the Constitution, clearly indicate it as a direct quote

Remember, your primary goal is to educate users about the Indian Constitution accurately.
"""

class ConstitutionQAService:
    """Service to handle QA chains for the Indian Constitution."""
    
    def __init__(self):
        """Initialize the QA chain service."""
        self.vector_store_service = VectorStoreService()
        self.llm = ChatGroq(
            model_name='llama-3.1-8b-instant',
            temperature=0.3,
            api_key=settings.GROQ_API_KEY
        )
    
    def extract_sources(self, source_documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract source information from documents."""
        sources = []
        seen_sources = set()
        
        for doc in source_documents:
            # Extract article references from the content
            article_refs = re.finditer(r'Article (\d+[A-Z]?(?:\([a-z]\))?)', doc.page_content)
            
            for match in article_refs:
                article_ref = match.group(0)  # Full match (e.g., "Article 51A(a)")
                article_num = match.group(1)  # Just the number (e.g., "51A(a)")
                
                # Create source entry
                source_entry = {
                    "type": doc.metadata.get("section_type", "Constitutional Provision"),
                    "article": article_ref,
                    "content": self._extract_relevant_content(doc.page_content, match.start(), 200),
                    "page_number": doc.metadata.get("page_number", "Unknown"),
                    "section": doc.metadata.get("section_name", "")
                }
                
                # Create unique identifier
                source_id = f"{article_ref}:{source_entry['type']}"
                
                if source_id not in seen_sources:
                    sources.append(source_entry)
                    seen_sources.add(source_id)
        
        return sources
    
    def _extract_relevant_content(self, content: str, match_position: int, context_length: int = 200) -> str:
        """Extract relevant content around a match position."""
        start = max(0, match_position - context_length // 2)
        end = min(len(content), match_position + context_length // 2)
        
        # Find sentence boundaries
        content_slice = content[start:end]
        sentences = re.split(r'(?<=[.!?])\s+', content_slice)
        
        if len(sentences) > 1:
            # Return complete sentences
            return ' '.join(sentences[:-1]) + '.'
        return content_slice + "..."
    
    def answer_question(self, question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Answer a question about the Indian Constitution."""
        # Get relevant documents
        retriever = self.vector_store_service.get_retriever()
        docs = retriever.get_relevant_documents(question)
        
        # Combine all documents into a single context string
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Build message history
        messages = [SystemMessage(content=CONSTITUTION_SYSTEM_PROMPT)]
        
        # Add chat history if provided
        if chat_history:
            for message in chat_history:
                if message["role"] == "user":
                    messages.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    messages.append(AIMessage(content=message["content"]))
        
        # Create the prompt with context and question
        messages.append(HumanMessage(content=question))
        
        # Modify the system message to explicitly request article citations
        context_message = f"""
Here is the relevant information from the Indian Constitution to answer the question:

{context}

Please provide a detailed answer that:
1. Cites specific articles and sections (e.g., "Article 51A(a)")
2. Uses direct quotes when appropriate
3. Organizes information clearly
4. References only the information provided above
"""
        
        messages.append(SystemMessage(content=context_message))
        
        logger.info(f"Processing question: {question}")

        # Get answer from LLM
        response = self.llm.invoke(messages)
        answer = response.content
        
        logger.info(f"Generated answer of length {len(answer)}")
        
        # Extract sources
        sources = self.extract_sources(docs)
        
        # Sort sources by article number
        sources.sort(key=lambda x: x.get("article", ""))
        
        return {
            "answer": answer,
            "sources": sources
        } 