ARG WOPR_API_UPSTREAM="wopr-api"
ARG WOPR_API_UPSTREAM_PORT="8080"
ARG WOPR_ML_UPSTREAM="wopr-ml"
ARG WOPR_ML_UPSTREAM_PORT="8080"

# build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY src ./src
COPY vite.config.ts .
COPY web/index.html .
RUN npm run build

# runtime stage
FROM nginx:alpine
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
