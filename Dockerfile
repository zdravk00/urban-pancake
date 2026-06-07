FROM python:3.10-slim
WORKDIR /app
COPY gpu_Worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY gpu_Worker/ .
CMD ["python3", "-u", "handler.py"]
