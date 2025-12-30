#buildplease5
# build stage
FROM node:20-alpine AS build

ENV HOME=/app
WORKDIR /app

COPY package.json package-lock.json* tsconfig.json ./
RUN npm install -g npm@latest
RUN npm install
COPY src ./src
#COPY public ./public
COPY web/index.html ./index.html
COPY vite.config.ts ./vite.config.ts
RUN npm run build

# runtime stage
FROM nginxinc/nginx-unprivileged:alpine
WORKDIR /app
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
#RUN touch /run/nginx.pid && chown nginx:nginx /run/nginx.pid 
#RUN chgrp -R 1000 /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d && \
#    chmod -R 770 /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d
#RUN chown -R 1000 /etc/nginx/conf.d

EXPOSE 8080