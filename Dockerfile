# Voice Markdown Editor Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for audio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Create directories for data
RUN mkdir -p /app/logs /app/transcripts /app/examples

# Expose port for potential web interface (future)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import main; print('OK')" || exit 1

# Default command
CMD ["python", "main.py", "--help"]

# Docker usage examples:
# Build: docker build -t voice-markdown-editor .
# Run interactive: docker run -it --rm voice-markdown-editor python main.py --interactive
# Run with volume: docker run -it --rm -v $(pwd)/notes:/app/notes voice-markdown-editor python main.py --file notes/todo.md
# Run live mode: docker run -it --rm voice-markdown-editor python main.py --live