FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies including OpenMP for FAISS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libomp5 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify FAISS import during build
RUN python -c "import faiss; print(f'faiss {faiss.__version__} OK')"

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]
