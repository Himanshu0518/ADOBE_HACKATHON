FROM --platform=linux/amd64 python:3.12-slim-bookworm

# Set working directory inside the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- NLTK Stopwords Download ---
# Ensure nltk is included if not already
RUN pip install --no-cache-dir nltk && \
    python -m nltk.downloader stopwords punkt

# Copy entire project after dependencies
COPY . .

# Ensure input/output folders exist
RUN mkdir -p /app/input /app/output

# Set default command
CMD ["python", "-m", "src.main"]

# Optional metadata
LABEL maintainer="Your Name <your.email@example.com>" \
      description="Adobe India Hackathon Round 1 Solution"
