FROM python:3.11-slim

WORKDIR /app
ENV PYTHONIOENCODING=utf-8

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY main.py .
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Expose the REST API port
EXPOSE 8000

# Run the Flask REST API
CMD ["python", "app.py"]
