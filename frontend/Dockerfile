## Frontend Dockerfile
# FROM node:24.14.0-bookworm-slim
# 53.63MB Size
FROM node:24.14.0-alpine3.23

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]