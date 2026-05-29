FROM node:20-alpine

WORKDIR /app

# Pre-create node_modules + .next dirs with node ownership so that anonymous
# volumes mounted at these paths inherit the right uid/gid. Otherwise the
# `node` user can't write to /app/.next at runtime (EACCES on trace file).
RUN mkdir -p /app/node_modules /app/.next \
    && chown -R node:node /app
USER node

# Install dependencies first (cached layer when package.json unchanged)
COPY --chown=node:node package*.json ./
RUN npm install

# Copy application code. In dev this is overlaid by the host volume mount.
COPY --chown=node:node . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "run", "dev"]
