FROM python:3.12-slim-bookworm

# Set working directory inside the container
WORKDIR /app

# Copy all files into container
COPY . .

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    swig \
    && rm -rf /var/lib/apt/lists/*

# ✅ Install NLTK first and download corpora (works offline after this)
RUN pip install --no-cache-dir nltk && \
    python -m nltk.downloader stopwords punkt wordnet omw-1.4 averaged_perceptron_tagger

# ✅ Now install remaining project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your module
CMD ["python", "-m", "src.main"]
