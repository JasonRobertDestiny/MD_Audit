# MD Audit Docker Image
# 多阶段构建：前端构建 + 后端运行

# ===== 阶段1：构建前端 =====
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install --legacy-peer-deps

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# ===== 阶段2：Python运行环境 =====
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY md_audit/ ./md_audit/
COPY web/ ./web/
COPY config/ ./config/
COPY setup.py ./

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/frontend/dist ./web/static/

# 安装项目
RUN pip install -e .

# 创建数据目录
RUN mkdir -p /app/data /app/uploads

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV MD_AUDIT_ALLOWED_ORIGINS="*"

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]
