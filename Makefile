.PHONY: setup build-index run-api run-frontend run-all clean

# Setup environment
setup:
	pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete. Remember to edit your .env file with your OpenAI API key."

# Build or rebuild the vector index
build-index:
	python -m app.utils.build_index

# Force rebuild the vector index
rebuild-index:
	python -m app.utils.build_index --force

# Run the FastAPI backend
run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the Streamlit frontend
run-frontend:
	cd frontend && streamlit run streamlit_app.py

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Clean up temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Available commands:"
	@echo "  make setup          - Set up the environment"
	@echo "  make build-index    - Build the vector index"
	@echo "  make rebuild-index  - Force rebuild the vector index"
	@echo "  make run-api        - Run the FastAPI backend"
	@echo "  make run-frontend   - Run the Streamlit frontend"
	@echo "  make docker-build   - Build Docker containers"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make clean          - Clean up temporary files" 