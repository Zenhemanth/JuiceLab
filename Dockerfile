# Use a broader Python base image
FROM python:3.9-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy project files to the working directory
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies with error logging for debugging
RUN pip install --no-cache-dir -r requirements.txt || { echo "Error during pip install"; exit 1; }

# Install MySQL client for database initialization
RUN apt-get update && apt-get install -y default-mysql-client

# Expose the application port
EXPOSE 8000

# Start the application with database initialization
CMD ["bash", "-c", "mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB < /app/db.sql || true && gunicorn app:app --bind 0.0.0.0:8000"]
