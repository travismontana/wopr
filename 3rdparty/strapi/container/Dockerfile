# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Strapi 5 Production Dockerfile
# Creates a new Strapi 5 project from scratch
# 
# Build: docker build --build-arg STRAPI_VERSION=5.30.1 -t your-registry/strapi:5.30.1 .
# Push: docker push your-registry/strapi:5.30.1

ARG NODE_VERSION=20-alpine
ARG STRAPI_VERSION=5.30.1

# ===================================
# Stage 1: Create and build Strapi project
# ===================================
FROM node:${NODE_VERSION} AS builder

ARG STRAPI_VERSION

WORKDIR /build

# Install dependencies for Strapi CLI
RUN apk add --no-cache python3 make g++ && \
    npm install -g @strapi/strapi@${STRAPI_VERSION}

# Create new Strapi project with PostgreSQL
# Use --no-run to skip starting the server
RUN npx create-strapi-app@${STRAPI_VERSION} app \
    --dbclient=postgres \
    --no-run

WORKDIR /build/app

# Build the admin panel
ENV NODE_ENV=production
RUN npm run build

# ===================================
# Stage 2: Production runtime
# ===================================
FROM node:${NODE_VERSION}

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user
#RUN addgroup -g 1000 strapi && \
#    adduser -D -u 1000 -G strapi strapi

WORKDIR /srv/app

# Copy built application
COPY --from=builder --chown=strapi:strapi /build/app ./

# Create uploads directory with proper permissions
RUN mkdir -p /srv/app/public/uploads && \
    chown -R strapi:strapi /srv/app

# Switch to non-root user
USER strapi

# Expose port
EXPOSE 1337

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:1337/_health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start Strapi
CMD ["npm", "run", "start"]