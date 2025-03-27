# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Map ./REPOSITORY to /app/REPOSITORY
VOLUME /app/REPOSITORY

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# WILL BE OVERRIDDEN BY docker-compose.yml
# Define environment variable
ENV IRB_DATABASE_PATH sqlite:///database.db
ENV IRB_REPOSITORY_URL http://127.0.0.1:8000/static/
# Change this key for production!
ENV IRB_API_KEY 3456345-456-456
# url root for the API
ENV IRB_ROOT=/

# Run app.py when the container launches
CMD ["python", "entrypoint.py"]
