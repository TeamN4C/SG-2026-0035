FROM node:24.22.0

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts \
    && npm cache clean --force

COPY repro.js ./

EXPOSE 31338

CMD ["node", "repro.js"]
