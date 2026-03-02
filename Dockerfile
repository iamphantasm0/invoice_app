# Use official Python slim image
FROM python:3.12-slim

# Install dependencies needed for WeasyPrint and your app
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    libcairo2 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /invoice_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use shell form so $PORT env var is resolved at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
