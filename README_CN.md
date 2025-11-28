<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue.js-3.4-green.svg" alt="Vue.js">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-teal.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-GPT--4o-purple.svg" alt="AI Powered">
</p>

<h1 align="center">MD Audit</h1>

<p align="center">
  <strong>智能 Markdown SEO 诊断 Agent</strong><br>
  结合规则引擎与 AI 语义分析的双引擎诊断系统
</p>

<p align="center">
  <a href="#核心特性">特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#web-界面">Web 界面</a> •
  <a href="#命令行使用">CLI 使用</a> •
  <a href="#api-接口">API</a> •
  <a href="#配置说明">配置</a> •
  <a href="./README.md">English</a>
</p>

---

## 项目简介

**MD Audit** 是一个基于 Python 的 Markdown SEO 诊断 Agent，专门针对 Markdown 内容进行 SEO 质量评估。系统采用双引擎架构：规则引擎（75% 权重）+ AI 语义分析（25% 权重），自动评估内容质量并提供可执行的优化建议。

### 为什么选择 MD Audit？

- **原生 Markdown 支持**：直接分析 `.md` 文件，无需转换
- **双引擎分析**：快速规则检查 + 智能 AI 洞察
- **精美 Web 界面**：现代 Vue.js 界面，配备 Aurora 动画效果
- **可执行建议**：提供具体的代码示例，而非泛泛而谈
- **优雅降级**：AI 不可用时自动切换为纯规则分析

---

## 核心特性

### 分析维度

| 维度 | 权重 | 检查项 |
|------|------|--------|
| **元数据** | 30% | Title 长度（30-60字符）、Description 长度（120-160字符） |
| **结构** | 25% | H1 标签唯一性、图片 Alt 覆盖率（≥80%）、内外部链接 |
| **关键词** | 20% | 关键词密度（1%-2.5%）、关键词位置（标题/描述/首段） |
| **AI 语义** | 25% | 内容深度、可读性、主题相关性 |

### Web 界面特性

- **拖拽上传**：直接拖拽 Markdown 文件即可分析
- **实时分析**：动画进度指示器展示分析过程
- **分数庆祝**：优秀分数（85+）触发彩纸庆祝效果
- **Aurora 背景**：精美的动态渐变背景
- **响应式设计**：适配桌面和移动设备

### CLI 特性

- 单文件和批量目录分析
- 自定义关键词指定
- JSON 配置文件支持
- 多种输出格式

---

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+（Web 界面需要）
- OpenAI API 密钥（可选，用于 AI 分析）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/JasonRobertDestiny/MD_Audit.git
cd MD_Audit

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装 Python 依赖
pip install -r requirements.txt
pip install -e .

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 配置 API 密钥

```bash
# 设置 OpenAI API 密钥（可选，用于 AI 分析）
export MD_AUDIT_LLM_API_KEY=your_openai_api_key

# 或创建 .env 文件
echo "MD_AUDIT_LLM_API_KEY=your_openai_api_key" > .env
```

---

## Web 界面

### 启动应用

```bash
# 终端 1：启动后端 API
source venv/bin/activate
python -m md_audit.main serve --reload

# 终端 2：启动前端
cd frontend
npm run dev
```

访问 **http://localhost:5173** 即可使用 Web 界面

### 界面功能

- **首页**：支持拖拽的上传区域
- **分析进度**：动画步骤进度指示器
- **分数展示**：渐变色环形分数显示
- **诊断卡片**：分类显示问题（严重/警告/通过）
- **关键词标签**：展示提取的关键词

---

## 命令行使用

### 基础用法

```bash
# 分析单个文件（自动提取关键词）
md-audit analyze docs/article.md

# 或使用 Python 模块
python -m md_audit.main analyze docs/article.md
```

### 高级选项

```bash
# 手动指定关键词
md-audit analyze docs/article.md -k "Python" "SEO" "优化"

# 保存报告到文件
md-audit analyze docs/article.md -o report.md

# 使用自定义配置
md-audit analyze docs/article.md --config custom_config.json

# 禁用 AI 分析（仅规则检查）
md-audit analyze docs/article.md --no-ai

# 批量分析目录
md-audit analyze docs/ -o reports/ --workers 8
```

---

## API 接口

### REST 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| `POST` | `/api/analyze` | 分析上传的 Markdown 文件 |
| `GET` | `/api/health` | 健康检查端点 |
| `GET` | `/docs` | 交互式 API 文档 |

### 请求示例

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@article.md" \
  -F "keywords=SEO,Markdown"
```

### 响应格式

```json
{
  "total_score": 85.5,
  "metadata_score": 28.0,
  "structure_score": 22.5,
  "keyword_score": 18.0,
  "ai_score": 17.0,
  "diagnostics": [
    {
      "rule_id": "META_01",
      "severity": "success",
      "message": "标题长度合适（45字符）",
      "current_value": 45,
      "expected_range": "30-60"
    }
  ],
  "extracted_keywords": ["python", "seo", "markdown"]
}
```

---

## 配置说明

### 默认配置

配置文件位于 `config/default_config.json`：

```json
{
  "title_rules": {
    "min_length": 30,
    "max_length": 60
  },
  "description_rules": {
    "min_length": 120,
    "max_length": 160
  },
  "keyword_rules": {
    "min_density": 0.01,
    "max_density": 0.025,
    "max_auto_keywords": 5
  },
  "content_rules": {
    "min_length": 300,
    "min_h1_count": 1,
    "max_h1_count": 1,
    "min_image_alt_ratio": 0.8
  },
  "llm_model": "gpt-4o",
  "enable_ai_analysis": true
}
```

### 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `MD_AUDIT_LLM_API_KEY` | OpenAI API 密钥 | - |
| `MD_AUDIT_LLM_MODEL` | 使用的 LLM 模型 | `gpt-4o` |
| `SEO_RULES_CONFIG` | 自定义配置文件路径 | `config/default_config.json` |

---

## 项目架构

```
MD_Audit/
├── md_audit/                 # 核心 Python 包
│   ├── main.py              # CLI 入口
│   ├── analyzer.py          # 主分析器协调器
│   ├── config.py            # 配置管理
│   ├── reporter.py          # 报告生成
│   ├── engines/
│   │   ├── rules_engine.py  # 规则引擎
│   │   └── ai_engine.py     # AI 语义分析引擎
│   ├── parsers/
│   │   └── markdown_parser.py  # Markdown/Frontmatter 解析
│   └── models/
│       └── data_models.py   # Pydantic 数据模型
├── frontend/                 # Vue.js Web 界面
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── views/           # 页面视图
│   │   └── assets/styles/   # Tailwind CSS
│   └── tailwind.config.js   # Tailwind 配置
├── web/                      # FastAPI 后端
│   └── main.py              # API 端点
├── config/                   # 配置文件
├── tests/                    # 测试套件
└── docs/                     # 文档
```

---

## 评分体系

### 分数等级

| 分数范围 | 等级 | 标识 |
|----------|------|------|
| 90-100 | 优秀 | 绿色 |
| 70-89 | 良好 | 蓝色 |
| 50-69 | 需改进 | 橙色 |
| 0-49 | 较差 | 红色 |

### 严重程度

- **严重 (Critical)**：必须立即修复（如缺少标题）
- **高 (High)**：显著影响 SEO（如标题过短）
- **中 (Medium)**：有优化空间（如描述略长）
- **低 (Low)**：小建议（如可增加内部链接）

---

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=md_audit --cov-report=html
```

### 代码质量

```bash
# 格式化代码
black md_audit/

# 代码检查
ruff check md_audit/

# 自动修复
ruff check --fix md_audit/
```

### 构建前端

```bash
cd frontend
npm run build
```

---

## 技术栈

### 后端
- **Python 3.8+**：核心语言
- **FastAPI**：REST API 框架
- **Pydantic**：数据验证
- **OpenAI**：AI 语义分析
- **BeautifulSoup4**：HTML 解析
- **python-frontmatter**：YAML frontmatter 解析

### 前端
- **Vue.js 3.4**：UI 框架
- **Tailwind CSS 3.4**：样式框架
- **Vite 7**：构建工具
- **Axios**：HTTP 客户端

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

- 配置系统和关键词提取逻辑参考自 [SEO-AutoPilot](https://github.com/example/SEO-AutoPilot)
- UI 动画灵感来自 [ReactBits](https://reactbits.dev)

---

<p align="center">
  由 <a href="https://github.com/JasonRobertDestiny">JasonRobertDestiny</a> 用心打造
</p>
