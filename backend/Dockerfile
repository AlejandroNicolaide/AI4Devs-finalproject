FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf-cache

WORKDIR /app

# torch solo CPU (~200 MB en lugar de ~2 GB con CUDA); sentence-transformers lo reutiliza
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt

# El modelo de embeddings se descarga al construir la imagen: la primera subida de material no espera ~460 MB
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY docker-entrypoint.sh ./
# tolera CRLF si el código se construyó desde un checkout de Windows
RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh \
    && useradd --create-home app && chown -R app /app /opt/hf-cache
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

ENTRYPOINT ["./docker-entrypoint.sh"]
