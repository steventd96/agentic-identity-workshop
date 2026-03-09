# Multi-stage build for AskHR Frontend Application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm install

# Copy application source
COPY . .

# Accept build arguments for React environment variables
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_LANGFLOW_API_URL
ARG REACT_APP_LANGFLOW_API_KEY
ARG REACT_APP_LANGFLOW_HOST_URL
ARG REACT_APP_LANGFLOW_FLOW_ID
ARG REACT_APP_LANGFLOW_COMPONENT_ID

# Set environment variables for build
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_LANGFLOW_API_URL=$REACT_APP_LANGFLOW_API_URL
ENV REACT_APP_LANGFLOW_API_KEY=$REACT_APP_LANGFLOW_API_KEY
ENV REACT_APP_LANGFLOW_HOST_URL=$REACT_APP_LANGFLOW_HOST_URL
ENV REACT_APP_LANGFLOW_FLOW_ID=$REACT_APP_LANGFLOW_FLOW_ID
ENV REACT_APP_LANGFLOW_COMPONENT_ID=$REACT_APP_LANGFLOW_COMPONENT_ID

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]