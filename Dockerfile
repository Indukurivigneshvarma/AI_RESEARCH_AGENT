FROM python:3.11-slim

WORKDIR /app

# Install system deps needed by some libs (faiss, newspaper, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

EXPOSE 7860

# IMPORTANT: app is now inside src/main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
