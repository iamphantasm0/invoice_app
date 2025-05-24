# Use official Python slim image
FROM python:3.12-slim

# Install dependencies needed for WeasyPrint and your app
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to root of your project
WORKDIR /invoice_app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the app using uvicorn pointing to your app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
