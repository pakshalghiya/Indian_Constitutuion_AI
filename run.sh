#!/bin/bash

# Function to handle cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        echo "Loading OpenAI API key from .env file"
        export $(grep -v '^#' .env | xargs)
    else
        echo "Error: OPENAI_API_KEY environment variable not set and .env file not found."
        echo "Please set your OpenAI API key in the .env file or export it as an environment variable."
        exit 1
    fi
fi

# Create necessary directories if they don't exist
mkdir -p app/data/constitution/source app/data/embeddings/faiss_index logs

# Create the virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start the backend
echo "Starting FastAPI backend..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 2

# Start the frontend
echo "Starting Streamlit frontend..."
cd frontend && streamlit run streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

# Wait for backend or frontend to exit
wait $BACKEND_PID $FRONTEND_PID

# Call cleanup on exit
cleanup
