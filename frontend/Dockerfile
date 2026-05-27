FROM node:20-alpine

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy application code (overridden by volume mount in dev)
COPY . .

# Run as the built-in non-root `node` user
RUN chown -R node:node /app
USER node

# Expose Next.js port
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Dev command (overridden in compose for prod)
CMD ["npm", "run", "dev"]
