# Primera etapa
FROM python:3.11-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Etapa final
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

CMD ["python", "pipeline.py"]
