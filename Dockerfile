FROM python:3.10-slim
WORKDIR /app
COPY gpu_worker/requirements.txt .
RUN pip install -r requirements.txt
COPY gpu_worker/ .
CMD ["python3", "handler.py"]