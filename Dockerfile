# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY tile_processor.py .
COPY xyo_witness_service.py .
COPY orchestrator.py .
COPY demo.py .
COPY entrypoint.py .

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Run entrypoint
CMD ["python", "entrypoint.py"]
