#!/bin/bash

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}   Indian Constitution AI - Installation Script         ${NC}"
echo -e "${BLUE}========================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
echo -e "\n${YELLOW}Checking for Python 3.9+...${NC}"
if ! command_exists python3; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Python version $PYTHON_VERSION is not supported. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Create virtual environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Updating...${NC}"
else
    echo -e "${YELLOW}Creating new virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Don't forget to update it with your OpenAI API key!${NC}"
else
    echo -e "\n${YELLOW}.env file already exists. Skipping...${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p app/data/constitution/source app/data/embeddings/faiss_index logs

# Download constitution source files and build index
echo -e "\n${YELLOW}Downloading Indian Constitution files...${NC}"
python -m app.utils.download_constitution

echo -e "\n${YELLOW}Building vector store index...${NC}"
python -m app.utils.build_index

echo -e "\n${GREEN}========================================================${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}========================================================${NC}"
echo -e "\n${YELLOW}To start the application, run:${NC}"
echo -e "${BLUE}./run.sh${NC}"
echo -e "\n${YELLOW}Don't forget to update the .env file with your OpenAI API key!${NC}"
echo -e "${YELLOW}Visit the FastAPI docs at:${NC} ${BLUE}http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Visit the Streamlit frontend at:${NC} ${BLUE}http://localhost:8501${NC}"
echo -e "\n${GREEN}Happy querying!${NC}\n" 