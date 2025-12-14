FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs/api_responses/chat /app/logs/api_responses/errors /app/logs/api_responses/ocr

# Expose API port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9000/ || exit 1

# Run the FastAPI application
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "9000"]
