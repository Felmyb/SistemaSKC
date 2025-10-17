# SmartKitchen Connect - Backend Dockerfile
# Standard: IEEE 830 | Requirement: RNF-05 (Docker deployment)

# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables (RNF-02, RNF-03)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/static /app/media

# Collect static files (will be overridden by volume in docker-compose)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check (RNF-01 - Performance monitoring)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=5)"

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
