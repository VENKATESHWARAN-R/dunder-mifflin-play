FROM python:3.13-slim

# Set working directory
WORKDIR /app/ryan_howard

# Install uv
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy agent-specific files
COPY . /app/ryan_howard/
COPY main.py /app/
# Install agent specific dependencies
RUN uv pip install -e .

# Expose the agent service port
EXPOSE 10010 8080
# Added port 8080 for the cloudrun, anyway it will ignore this instruction
# running in local env uses 10010
# and 8080 for cloud run

# Change to the base directory
WORKDIR /app

# Start the agent service
#CMD ["uvicorn", "ryan_howard.a2a_server:app", "--host", "0.0.0.0", "--port", "10010"]
#CMD ["sh", "-c", "uvicorn ryan_howard.a2a_server:app --host 0.0.0.0 --port ${RUNTIME_PORT:-10010}"]

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${RUNTIME_PORT:-10010}"]