# Stage 1: Builder
FROM python:3.11-slim-bookworm@sha256:94a8fee35252d06ab75856f15f12c7bae67b10e8a6da93c7fded82b2610926cd AS builder

WORKDIR /build

COPY requirements-docker.txt .

RUN pip install --no-cache-dir --prefix=/install \
    -r requirements-docker.txt


# Stage 2: Runtime
FROM python:3.11-slim-bookworm@sha256:94a8fee35252d06ab75856f15f12c7bae67b10e8a6da93c7fded82b2610926cd AS runtime

WORKDIR /app

# Install dependencies from builder stage
COPY --from=builder /install /usr/local
RUN python -m pip uninstall -y wheel || true
RUN python -m pip install --no-cache-dir --upgrade --force-reinstall wheel==0.46.2 jaraco.context==6.1.0

# Copy application files
COPY . .

# Create a non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

# Run as non-root user
USER appuser

# Application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
    --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]