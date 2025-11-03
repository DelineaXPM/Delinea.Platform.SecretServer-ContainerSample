FROM python:3.11-slim

WORKDIR /app

# Install curl (and clean up to keep image small)
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy source code
COPY src/ /app/src/

# Install SDK from tarball and requests
RUN pip install --upgrade pip && \
    pip install requests && \
    pip install python-tss-sdk

EXPOSE 8080

# Run the new main entrypoint
CMD ["python", "src/main.py"]