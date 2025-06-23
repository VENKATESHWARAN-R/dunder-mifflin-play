# Use an official Python runtime as a parent image
# Using python:3.11-slim for a smaller image size
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 (PostgreSQL adapter)
# This is more robust than using psycopg2-binary in production
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
# This is done first to leverage Docker's layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces the image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Expose the port the app will run on
# We'll run Gunicorn on port 5000 inside the container
EXPOSE 5000

# Define the command to run the application using Gunicorn
# This is a production-ready WSGI server
# It will run the 'app' object from the 'app.py' file
# Binding to 0.0.0.0 makes it accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]