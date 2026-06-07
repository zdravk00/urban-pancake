FROM python:3.10-slim

# Installiere systemweite Abhängigkeiten (ffmpeg ist zwingend für Audio!)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopiere zuerst nur die requirements, damit Docker das Caching optimal nutzt
COPY gpu_Worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes
COPY gpu_Worker/ .

# CMD wird meistens von RunPod überschrieben, aber wir lassen es als Backup
CMD ["python3", "-u", "handler.py"]