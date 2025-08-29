FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use env vars from the platform (Koyeb/Render dashboards)
# Example:
# ENV API_ID=12345
# ENV API_HASH=xxxxxxxxxxxxxxxxxxxx
# ENV BOT_TOKEN=1234:abcd
# ENV FORCE_SUB_CHANNEL=@YourChannel
# ENV DATABASE_CHANNEL=-1001234567890
# ENV MONGO_URL=mongodb+srv://user:pass@cluster/db
# ENV ADMINS=123456789,987654321
# ENV AUTO_DELETE_MINUTES=0

CMD ["python", "main.py"]
