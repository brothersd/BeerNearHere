# Frontend Dockerfile - Production Optimized
FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

RUN npm install && \
    # Verify installation succeeded
    node -e "require('react')"

# Copy source code (fixed syntax)
COPY . .

# Build the React app in production mode
RUN npm run build

# Production stage - minimal nginx image
FROM nginx:stable-alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl ca-certificates

# Copy built React app from builder stage (Verify if this should be /app/build or /app/dist)
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config from build context
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check (fixed syntax)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]