# Backend Dockerfile - Production Optimized
FROM python:3.13-alpine AS builder

# Install system dependencies required for building Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

WORKDIR /app

COPY requirements.txt .

# Install Python dependencies in a separate layer for better caching
RUN pip install --no-cache-dir -r requirements.txt && \
    # Verify installation succeeded
    python -c "import django; import rest_framework"

# Production stage - minimal image
FROM python:3.13-alpine AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH=/usr/local/bin:$PATH

WORKDIR /app

# Install runtime dependencies only (no build tools)
RUN apk add --no-cache \
    # Required for psycopg2-binary and cryptography
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    postgresql-libs \
    # For gunicorn
    ca-certificates

# Create a non-root user for security (alpine uses adduser)
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    mkdir -p /app/staticfiles /var/log/django && \
    chown -R appuser:appgroup /app /var/log/django

# Copy Python dependencies from builder stage (better caching)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY . .

# Set ownership to non-root user
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app

# Switch to non-root user for security
USER appuser

# Expose port (gunicorn default)
EXPOSE 8000

# Health check using Django's built-in health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ready/ || exit 1

# Run with gunicorn for production (better than runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", \
     "--threads", "2", "--timeout", "30", \
     "config.wsgi:application"]