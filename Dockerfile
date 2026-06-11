FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY main.py .

# Expose no ports — this is a CLI application
# The app uses in-memory storage, no external dependencies needed

# Run the application
CMD ["python", "main.py"]
