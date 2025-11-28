# MD Audit Web UI - 用户指南

## 简介

MD Audit Web UI是MD Audit CLI工具的Web前端界面,提供了友好的可视化操作界面。

**核心功能**:
- 📤 拖拽上传Markdown文件
- 📊 实时SEO质量分析
- 📈 可视化诊断报告
- 📜 历史记录管理
- 🔍 问题筛选和详情查看

## 快速开始

### 1. 安装依赖

```bash
# 安装Web服务依赖
pip install -r requirements.txt

# 或仅安装Web相关依赖
pip install 'fastapi[all]' uvicorn slowapi python-multipart aiofiles
```

### 2. 启动服务

```bash
# 使用CLI命令启动（推荐）
md-audit serve

# 自定义端口
md-audit serve --port 8080

# 允许外网访问
md-audit serve --host 0.0.0.0

# 开发模式（代码热重载）
md-audit serve --reload
```

### 3. 访问Web界面

服务启动后，在浏览器访问:
- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 使用指南

### 上传并分析文件

1. 打开首页 http://localhost:8000
2. 拖拽Markdown文件到上传区，或点击选择文件
3. 点击"开始分析"按钮
4. 等待5秒左右，查看诊断报告

**支持的文件格式**:
- `.md` - Markdown标准格式
- `.txt` - 纯文本（当作Markdown解析）
- `.markdown` - Markdown扩展名

**文件大小限制**: 最大10MB

### 查看诊断报告

报告包含以下部分:

1. **总分卡片**: 100分制评分 + 等级（优秀/良好/中等/较差）
2. **严重问题**: 🔴 必须修复的问题（红色）
3. **建议优化**: 🟡 可选的优化建议（黄色）
4. **检查通过**: 🟢 已符合标准的项目（绿色，默认折叠）
5. **关键词信息**: 提取的关键词列表

### 历史记录管理

点击导航栏的"历史记录"查看过去的诊断记录:

1. **列表视图**: 显示文件名、时间、评分、问题数量
2. **筛选功能**: 可筛选"有严重问题"或"有建议优化"的记录
3. **详情查看**: 点击任意记录查看完整报告
4. **分页加载**: 每页显示20条记录

## API文档

### API端点

#### 1. 文件诊断

```http
POST /api/v1/analyze
Content-Type: multipart/form-data

file: <Markdown文件>
keywords: ["关键词1", "关键词2"] (可选)
```

**响应**:
```json
{
  "report": {
    "total_score": 92.5,
    "diagnostics": [...],
    ...
  },
  "history_id": "20241127143000_1234567890"
}
```

#### 2. 历史记录列表

```http
GET /api/v1/history?page=1&page_size=20&severity=all
```

**响应**:
```json
{
  "items": [
    {
      "id": "...",
      "timestamp": "2024-11-27T14:30:00",
      "file_name": "article.md",
      "total_score": 92.5,
      "severity_counts": {
        "error": 0,
        "warning": 3,
        "success": 15
      }
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

#### 3. 历史记录详情

```http
GET /api/v1/history/{record_id}
```

#### 4. 健康检查

```http
GET /api/health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "analyzer_version": "1.0.0",
  "ai_enabled": true
}
```

完整API文档访问: http://localhost:8000/docs

## 技术架构

### 后端 (FastAPI)

**技术栈**:
- FastAPI 0.100+ - Web框架
- Uvicorn - ASGI服务器
- Pydantic - 数据验证
- slowapi - 速率限制

**目录结构**:
```
web/
├── api/              # API路由
│   ├── analyze.py   # 文件分析API
│   ├── history.py   # 历史记录API
│   └── health.py    # 健康检查API
├── services/         # 业务服务
│   ├── analyzer_service.py   # 分析服务（复用CLI）
│   ├── history_service.py    # 历史记录管理
│   └── file_service.py       # 文件处理
├── models/           # API模型
│   ├── requests.py
│   └── responses.py
└── main.py          # FastAPI应用入口
```

### 前端 (Vue 3)

**技术栈**:
- Vue.js 3.4+ - 前端框架
- Vite 5.0+ - 构建工具
- Tailwind CSS 3.4+ - UI框架
- Axios 1.6+ - HTTP客户端

**目录结构**:
```
frontend/
├── src/
│   ├── components/       # UI组件
│   │   ├── FileUploader.vue     # 文件上传
│   │   ├── ReportViewer.vue     # 报告展示
│   │   ├── HistoryList.vue      # 历史记录
│   │   └── DiagnosticItem.vue   # 诊断项
│   ├── views/           # 页面视图
│   │   ├── HomePage.vue
│   │   └── HistoryPage.vue
│   ├── router/          # 路由配置
│   └── assets/          # 静态资源
├── index.html
├── vite.config.js
└── package.json
```

### 数据存储

**历史记录存储**:
- 格式: JSON文件
- 位置: `~/.md-audit/history.json`
- 容量限制: 最多100条（FIFO淘汰）

**临时文件**:
- 位置: `/tmp/md_audit_uploads/`
- 清理策略: 每24小时自动清理

## 部署指南

### 开发环境

```bash
# 后端（终端1）
cd /path/to/MD_Audit
md-audit serve --reload

# 前端（终端2）
cd frontend
npm install
npm run dev
```

前端开发服务器: http://localhost:5173

### 生产环境

#### 1. 构建前端

```bash
cd frontend
npm install
npm run build
```

构建产物自动输出到 `web/static/`

#### 2. 启动后端服务

```bash
md-audit serve --host 0.0.0.0 --port 8000
```

#### 3. 使用systemd管理（Linux）

创建 `/etc/systemd/system/md-audit.service`:

```ini
[Unit]
Description=MD Audit Web Service
After=network.target

[Service]
Type=simple
User=mdaudit
WorkingDirectory=/opt/md-audit
Environment="MD_AUDIT_LLM_API_KEY=sk-xxx"
ExecStart=/opt/md-audit/venv/bin/md-audit serve --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl enable md-audit
sudo systemctl start md-audit
sudo systemctl status md-audit
```

#### 4. 使用Nginx反向代理（可选）

创建 `/etc/nginx/sites-available/md-audit`:

```nginx
server {
    listen 80;
    server_name md-audit.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/md-audit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 安全说明

### MVP阶段安全措施

已实现:
- ✅ 文件大小限制（10MB）
- ✅ 文件类型白名单（.md/.txt/.markdown）
- ✅ 恶意代码检测（script标签等）
- ✅ 速率限制（10次/分钟）
- ✅ 临时文件自动清理

### 生产环境建议

- 🔒 配置HTTPS（使用Let's Encrypt）
- 🔒 限制CORS来源（修改 `web/main.py` 的 `allow_origins`）
- 🔒 添加用户认证（v2.0功能）
- 🔒 配置防火墙规则
- 🔒 定期备份历史记录

## 常见问题

### 1. 启动服务时提示缺少依赖

```bash
pip install 'fastapi[all]' uvicorn slowapi python-multipart aiofiles
```

### 2. 前端无法访问API

检查CORS配置，确保 `web/main.py` 的 `allow_origins` 包含前端地址。

### 3. 文件上传失败（413错误）

Nginx配置需添加 `client_max_body_size 10M;`

### 4. 历史记录丢失

历史记录存储在 `~/.md-audit/history.json`，建议定期备份。

### 5. AI分析失败

检查环境变量 `MD_AUDIT_LLM_API_KEY` 是否正确配置。

## 性能优化

### 后端优化

- ✅ 单例analyzer实例（避免重复初始化）
- ✅ Gzip响应压缩
- ✅ 异步文件清理任务

### 前端优化

- ✅ 代码分割（路由懒加载）
- ✅ Tailwind CSS Tree-shaking
- ✅ 静态资源浏览器缓存

### 预期性能

- 首屏加载: <2秒
- 小文件分析(<100KB): <2秒
- 中等文件分析(100KB-1MB): <5秒
- 大文件分析(1MB-10MB): <10秒

## 联系与支持

- 问题反馈: 提交GitHub Issue
- 文档: 查看项目README.md
- API文档: http://localhost:8000/docs

---

**版本**: 1.0.0
**更新日期**: 2024-11-27
