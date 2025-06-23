# Use an official Python runtime as a parent image
# Using python:3.11-slim for a smaller image size
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 (PostgreSQL adapter)
# This is more robust than using psycopg2-binary in production
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Expose the port the app will run on
# We'll run Gunicorn on port 5000 inside the container
EXPOSE 5000 8000

#CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]

CMD ["python", "app.py"]