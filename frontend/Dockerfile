# AegisAI Frontend Dockerfile

# ---------------- Build stage ----------------
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Copy .env.local if it exists
# This ensures VITE_GEMINI_API_KEY is available at build time
COPY .env.local .env.local

# Build arguments (optional override from Docker Compose)
ARG VITE_GEMINI_API_KEY
ARG VITE_API_URL

# Set ENV for Vite build
ENV VITE_GEMINI_API_KEY=${VITE_GEMINI_API_KEY}
ENV VITE_API_URL=${VITE_API_URL}

# Build the app
RUN npm run build

# ---------------- Production stage ----------------
FROM node:18-alpine

WORKDIR /app

# Install serve to run the built app
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Run application
CMD ["serve", "-s", "dist", "-l", "3000"]
