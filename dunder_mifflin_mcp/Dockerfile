# Use the official Python lightweight image
FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

COPY pyproject.toml /app/
COPY . /app/dunder_mifflin_mcp/


RUN uv pip install .

EXPOSE $PORT

# Run the FastMCP server
CMD ["python", "-m", "dunder_mifflin_mcp.server"]