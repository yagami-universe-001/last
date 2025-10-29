# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system packages (ffmpeg is needed for Pyrogram bots that process media)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Optional: make start.sh executable if you use it
RUN chmod +x start.sh || true

# Default environment (you can override via docker-compose or .env)
ENV PYTHONUNBUFFERED=1

# Start the bot
# You can change "main.py" to your bot's main entry file (e.g., bot.py)
CMD ["python3", "main.py"]
