FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY gpu_Worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gpu_Worker/ .

CMD ["python3", "-u", "handler.py"]
