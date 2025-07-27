FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend directory
COPY frontend/ /app/frontend/

# Expose port
EXPOSE 8501

# Environment variables
ENV PYTHONPATH=/app

# Make the streamlit app the main command
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 