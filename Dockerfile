FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[api]"

COPY src ./src

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

EXPOSE 8000

CMD ["uvicorn", "doc_intelligence.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
