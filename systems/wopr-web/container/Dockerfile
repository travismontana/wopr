# build stage
FROM node:20-alpine AS build
ENV HOME=/app
WORKDIR /app
RUN addgroup -g 2222 wopr && \
    adduser -D -u 2222 -G wopr wopr
COPY --chown=2222:2222 package.json package-lock.json* ./
RUN npm install
COPY --chown=2222:2222 src ./src
COPY --chown=2222:2222 public ./public
COPY --chown=2222:2222 web/index.html ./index.html
COPY --chown=2222:2222 vite.config.ts ./vite.config.ts
RUN npm run build

# runtime stage
FROM nginx:alpine
COPY --chown=2222:2222 nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --chown=2222:2222 --from=build /app/dist /usr/share/nginx/html
RUN chgrp -R 2222 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 770 /var/cache/nginx /var/run /var/log/nginx
RUN sed -i 's/user.*nginx/user 2222/g' /etc/nginx/nginx.conf
EXPOSE 8080
