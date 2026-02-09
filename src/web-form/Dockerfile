# Web Form React Dockerfile (multi-stage)
FROM node:18-alpine AS build

WORKDIR /app
COPY package.json ./
RUN npm install

# Accept API URL at build time (default: same-origin via nginx proxy)
ARG REACT_APP_API_URL=http://localhost:3000
ENV REACT_APP_API_URL=$REACT_APP_API_URL

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
