FROM node:18-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    netcat-traditional \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --only=production
RUN npm install axios --save

# Copy application code
COPY . .

# Create wrapper script for startup
RUN echo '#!/bin/sh\n\
update-ca-certificates\n\
exec gosu nextjs "$@"' > /usr/local/bin/docker-entrypoint.sh && \
chmod +x /usr/local/bin/docker-entrypoint.sh

# Create non-root user for security
RUN groupadd -g 1001 nodejs && \
    useradd -u 1001 -g nodejs nextjs && \
    chown -R nextjs:nodejs /app

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start application
CMD ["node", "server.js"]
