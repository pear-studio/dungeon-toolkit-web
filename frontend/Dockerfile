# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段：只保留构建产物
FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/dist ./dist
# 这个镜像只用来把 dist 目录挂载给 nginx
CMD ["sh", "-c", "cp -r /app/dist/. /output/ && echo 'Frontend build copied.'"]
