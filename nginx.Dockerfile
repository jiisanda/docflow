# Builds the UI and bakes it, plus the nginx config, into one image (prod).
FROM node:22-alpine AS ui
WORKDIR /ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

FROM nginx:1.28.0-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf.d/   /etc/nginx/conf.d/
COPY nginx/snippets/ /etc/nginx/snippets/
COPY nginx/prod/     /etc/nginx/docflow/
COPY --from=ui /ui/dist /usr/share/nginx/html
