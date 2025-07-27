# 🇮🇳 Indian Constitution AI

A Retrieval-Augmented Generation (RAG) powered AI system for answering questions about the Indian Constitution with accuracy and proper citations.

## 🌟 Features

- **Vector Store-Based Retrieval**: Uses FAISS or Chroma DB to store and retrieve semantic embeddings of the Indian Constitution
- **Accurate Source Citations**: Provides references to specific articles, parts, and schedules
- **Conversational Interface**: Remembers previous questions and context
- **Interactive Visualization**: Explore relationships between different aspects of the Constitution
- **Easy Deployment**: Includes Docker support and detailed deployment instructions

## 🏗️ Architecture

The system uses a RAG (Retrieval Augmented Generation) architecture:

1. **Text Processing**: The Indian Constitution is split into chunks and embedded using OpenAI embeddings
2. **Vector Storage**: Embeddings are stored in a vector database (FAISS by default)
3. **Retrieval**: When a question is asked, the system retrieves the most relevant sections
4. **Generation**: These sections are used as context for the LLM to generate an accurate response

## 🛠️ Technical Stack

- **Backend**: FastAPI, LangChain, OpenAI API
- **Vector Database**: FAISS / Chroma
- **Frontend**: Streamlit
- **Deployment**: Docker-ready, can be deployed to any cloud platform

## 📋 Requirements

- Python 3.9+
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## 🚀 Quick Start

### Method 1: Using the Installation Script (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd AI_Lawyer

# Run the installation script
./install.sh

# Start the application
./run.sh
```

### Method 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd AI_Lawyer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

4. Download the Constitution files and build the vector store:
   ```bash
   python -m app.utils.download_constitution
   python -m app.utils.build_index
   ```

5. Start the application:
   ```bash
   ./run.sh
   ```

### Method 3: Using Docker Compose

```bash
# Clone the repository
git clone <your-repo-url>
cd AI_Lawyer

# Create .env file and add your OpenAI API key
cp .env.example .env
# Edit .env with your preferred text editor

# Build and start the containers
docker-compose up -d

# Access the application at http://localhost:8501
```

## 🧠 Working with Vector Embeddings

### Building the Vector Store

Before running the application, you need to build the vector store:

```bash
python -m app.utils.build_index
```

Use the `--force` flag to rebuild the index if needed:

```bash
python -m app.utils.build_index --force
```

### Downloading Constitution Files

If you need to download the Constitution files again:

```bash
python -m app.utils.download_constitution --force
```

## 📝 Usage Examples

1. Ask about fundamental rights:
   - "What are the fundamental rights provided in the Indian Constitution?"
   - "Explain Article 21 and its importance."

2. Understand government structure:
   - "How is the Indian Parliament structured?"
   - "What are the powers of the President of India?"

3. Query recent amendments:
   - "What were the most significant recent amendments to the Indian Constitution?"
   - "Explain the GST-related constitutional amendments."

## 🔄 API Endpoints

- `GET /`: Root endpoint with API info
- `GET /health`: Health check endpoint
- `POST /api/v1/ask`: Main endpoint for asking questions
- `POST /api/v1/build-index`: Endpoint to build/rebuild the vector index

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

Or, for a specific test file:

```bash
pytest tests/test_qa_service.py
```

## 🔧 Makefile Commands

The project includes a Makefile with helpful commands:

- `make setup`: Set up the environment
- `make build-index`: Build the vector index
- `make rebuild-index`: Force rebuild the vector index
- `make run-api`: Run the FastAPI backend
- `make run-frontend`: Run the Streamlit frontend
- `make docker-build`: Build Docker containers
- `make docker-up`: Start Docker containers
- `make docker-down`: Stop Docker containers
- `make clean`: Clean up temporary files

## 📚 Documentation

For more detailed documentation:
- API documentation is available at `/docs` when the server is running
- Check the `docs/` directory for additional documentation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Indian Constitution Repository by Prince Mishra](https://github.com/prince-mishra/the-constitution-of-india)
- [RAG Implementation Guides](https://medium.com/@saikrishna_17904/rag-chatbot-indias-constitutional-assembly-debates-e9b75282c54f)
- OpenAI for their embeddings and LLM APIs
- LangChain for their excellent framework

## 📬 Contact

For questions or support, please contact [your contact information]. 