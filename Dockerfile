FROM ghcr.io/astral-sh/uv:bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    unzip \
    python3-pip \
    && rm -rf /var/lib/apt/lists/

# Install AWS CLI v2 for SSM parameter access
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Copy backend requirements
COPY backend/pyproject.toml ./backend/

# Install Python dependencies
RUN cd /app/backend && uv sync

# Copy backend code
COPY backend/ /app/backend/

# Create directory for environment variables
RUN mkdir -p /claimsdemo/env

# Copy and set permissions for the entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Hardcode environment variables
ENV STATIC=true
ENV ALLOWED_ORIGINS="https://claims.opsloom.io,http://localhost:5173,http://localhost:5174,http://localhost:8080"

EXPOSE 8080

ENTRYPOINT ["/app/docker-entrypoint.sh"]