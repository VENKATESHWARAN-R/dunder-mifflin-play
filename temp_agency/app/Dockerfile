# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy project files
COPY . /app/app

# Install dependencies using uv
RUN uv pip install -e .

# Expose the FastAPI port
# Added port 8080 for the cloudrun, anyway it will ignore this instruction
# running in local env uses 6000
# and 8080 for cloud run
EXPOSE 6000 8080 

# Start the FastAPI server with Uvicorn
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${RUNTIME_PORT:-6000}"]
