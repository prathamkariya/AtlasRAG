FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src HF_HOME=/app/.cache/huggingface
WORKDIR /app
# CPU-only torch keeps the image small and works on modest hardware
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "atlasrag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
