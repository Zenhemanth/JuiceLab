# Use a broader Python base image
FROM python:3.9-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for certain Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmysqlclient-dev \
    default-libmysqlclient-dev

# Set the working directory in the container
WORKDIR /app

# Copy project files to the working directory
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies with error logging for debugging
RUN pip install --no-cache-dir -r requirements.txt || { echo "Error during pip install"; exit 1; }

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
