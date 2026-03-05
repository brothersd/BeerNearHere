# Backend Dockerfile
#https://hub.docker.com/_/python
FROM python:3.13-slim-bookworm

## ROOT USER: Install system dependencies
#RUN apt-get update && \
#    apt-get install -y curl && \
#    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PYTHONPATH="/app"

COPY requirements.txt .

#Dev
# RUN pip install -r requirements.txt
#Prod
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app/staticfiles

# Copy application code to docker
COPY . .

RUN chown -R appuser:appuser /app

# Switch to user account
USER appuser

EXPOSE 8000

# Default Command (Optimized for Dev)
# Use runserver here so your code changes reflect instantly.
# Use Gunicorn in a separate 'docker-compose.prod.yml' later.
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]