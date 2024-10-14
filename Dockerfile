# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for MongoDB URI (You can also pass these during runtime)
ENV MONGO_URI="your_mongodb_connection_string"

# Create log directory
RUN mkdir -p /app/logs

# Expose port if needed (only if your app serves a web service)
# EXPOSE 8000

# Define the command to run your pipeline
CMD ["python", "pdf_pipeline.py"]
