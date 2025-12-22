ARG WOPR_API_UPSTREAM="wopr-api"
ARG WOPR_API_UPSTREAM_PORT="8080"
ARG WOPR_ML_UPSTREAM="wopr-ml"
ARG WOPR_ML_UPSTREAM_PORT="8080"

# build stage
FROM node:20-alpine AS build
USER 2222:2222
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY src ./src
COPY public ./public
COPY web/index.html ./index.html
COPY vite.config.ts ./vite.config.ts
RUN npm run build

# runtime stage
FROM nginx:alpine
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
RUN chgrp -R root /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 770 /var/cache/nginx /var/run /var/log/nginx
EXPOSE 8080
