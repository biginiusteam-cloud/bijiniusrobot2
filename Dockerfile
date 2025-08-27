# Small, fast Python image
FROM python:3.10-slim

# System deps (certs & locales are useful)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source
COPY . .

# Run the bot
CMD ["python", "main.py"]
