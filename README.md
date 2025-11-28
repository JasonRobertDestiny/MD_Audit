<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue.js-3.4-green.svg" alt="Vue.js">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-teal.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-GPT--4o-purple.svg" alt="AI Powered">
</p>

<h1 align="center">MD Audit</h1>

<p align="center">
  <strong>Intelligent Markdown SEO Diagnostic Agent</strong><br>
  Dual-engine analysis combining rule-based checking with AI semantic analysis
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#web-interface">Web Interface</a> •
  <a href="#cli-usage">CLI Usage</a> •
  <a href="#api-reference">API</a> •
  <a href="#configuration">Configuration</a> •
  <a href="./README_CN.md">中文文档</a>
</p>

---

## Overview

**MD Audit** is a Python-based SEO diagnostic agent specifically designed for Markdown content. It combines a rule-based engine (75% weight) with AI semantic analysis (25% weight) to automatically evaluate SEO quality and provide actionable optimization suggestions.

### Why MD Audit?

- **Native Markdown Support**: Analyze `.md` files directly without conversion
- **Dual-Engine Analysis**: Fast rule checking + intelligent AI insights
- **Beautiful Web UI**: Modern Vue.js interface with Aurora animations
- **Actionable Reports**: Specific suggestions with code examples, not generic advice
- **Graceful Degradation**: Falls back to rule-only analysis when AI is unavailable

---

## Features

### Core Analysis

| Dimension | Weight | Checks |
|-----------|--------|--------|
| **Metadata** | 30% | Title length (30-60 chars), Description length (120-160 chars) |
| **Structure** | 25% | Unique H1 tag, Image alt coverage (≥80%), Internal/external links |
| **Keywords** | 20% | Keyword density (1%-2.5%), Keyword placement (title/desc/first paragraph) |
| **AI Semantic** | 25% | Content depth, Readability, Topic relevance |

### Web Interface Features

- **Drag & Drop Upload**: Simply drag your Markdown files
- **Real-time Analysis**: Watch progress with animated indicators
- **Score Celebration**: Confetti effects for excellent scores (85+)
- **Aurora Background**: Beautiful animated gradient background
- **Responsive Design**: Works on desktop and mobile

### CLI Features

- Single file and batch directory analysis
- Custom keyword specification
- Configurable rules via JSON
- Multiple output formats

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ (for web interface)
- OpenAI API key (optional, for AI analysis)

### Installation

```bash
# Clone the repository
git clone https://github.com/JasonRobertDestiny/MD_Audit.git
cd MD_Audit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install Python dependencies
pip install -r requirements.txt
pip install -e .

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Configuration

```bash
# Set your OpenAI API key (optional, for AI analysis)
export MD_AUDIT_LLM_API_KEY=your_openai_api_key

# Or create a .env file
echo "MD_AUDIT_LLM_API_KEY=your_openai_api_key" > .env
```

---

## Web Interface

### Start the Application

```bash
# Terminal 1: Start the backend API
source venv/bin/activate
python -m md_audit.main serve --reload

# Terminal 2: Start the frontend
cd frontend
npm run dev
```

Access the web interface at **http://localhost:5173**

### Web UI Features

- **Homepage**: Upload zone with drag & drop support
- **Analysis Progress**: Animated step-by-step progress indicator
- **Score Display**: Circular score ring with gradient colors
- **Diagnostic Cards**: Categorized issues (Critical, Warning, Success)
- **Keyword Tags**: Extracted keywords display

---

## CLI Usage

### Basic Analysis

```bash
# Analyze a single file (auto-extract keywords)
md-audit analyze docs/article.md

# Or use Python module
python -m md_audit.main analyze docs/article.md
```

### Advanced Options

```bash
# Specify keywords manually
md-audit analyze docs/article.md -k "Python" "SEO" "optimization"

# Save report to file
md-audit analyze docs/article.md -o report.md

# Use custom configuration
md-audit analyze docs/article.md --config custom_config.json

# Disable AI analysis (rules only)
md-audit analyze docs/article.md --no-ai

# Batch analyze a directory
md-audit analyze docs/ -o reports/ --workers 8
```

---

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Analyze uploaded Markdown file |
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@article.md" \
  -F "keywords=SEO,Markdown"
```

### Response Schema

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
      "message": "Title length is optimal (45 characters)",
      "current_value": 45,
      "expected_range": "30-60"
    }
  ],
  "extracted_keywords": ["python", "seo", "markdown"]
}
```

---

## Configuration

### Default Configuration

Located at `config/default_config.json`:

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

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MD_AUDIT_LLM_API_KEY` | OpenAI API key | - |
| `MD_AUDIT_LLM_MODEL` | LLM model to use | `gpt-4o` |
| `SEO_RULES_CONFIG` | Custom config file path | `config/default_config.json` |

---

## Architecture

```
MD_Audit/
├── md_audit/                 # Core Python package
│   ├── main.py              # CLI entry point
│   ├── analyzer.py          # Main analyzer orchestrator
│   ├── config.py            # Configuration management
│   ├── reporter.py          # Report generation
│   ├── engines/
│   │   ├── rules_engine.py  # Rule-based analysis
│   │   └── ai_engine.py     # AI semantic analysis
│   ├── parsers/
│   │   └── markdown_parser.py  # Markdown/Frontmatter parsing
│   └── models/
│       └── data_models.py   # Pydantic data models
├── frontend/                 # Vue.js web interface
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page views
│   │   └── assets/styles/   # Tailwind CSS
│   └── tailwind.config.js   # Tailwind configuration
├── web/                      # FastAPI backend
│   └── main.py              # API endpoints
├── config/                   # Configuration files
├── tests/                    # Test suite
└── docs/                     # Documentation
```

---

## Scoring System

### Score Grades

| Score Range | Grade | Badge |
|-------------|-------|-------|
| 90-100 | Excellent | Green |
| 70-89 | Good | Blue |
| 50-69 | Needs Work | Amber |
| 0-49 | Poor | Red |

### Severity Levels

- **Critical**: Must fix immediately (e.g., missing title)
- **High**: Significant SEO impact (e.g., title too short)
- **Medium**: Optimization opportunity (e.g., description slightly long)
- **Low**: Minor suggestion (e.g., could add more internal links)

---

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=md_audit --cov-report=html
```

### Code Quality

```bash
# Format code
black md_audit/

# Lint code
ruff check md_audit/

# Auto-fix lint issues
ruff check --fix md_audit/
```

### Building Frontend

```bash
cd frontend
npm run build
```

---

## Tech Stack

### Backend
- **Python 3.8+**: Core language
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **OpenAI**: AI semantic analysis
- **BeautifulSoup4**: HTML parsing
- **python-frontmatter**: YAML frontmatter parsing

### Frontend
- **Vue.js 3.4**: UI framework
- **Tailwind CSS 3.4**: Styling
- **Vite 7**: Build tool
- **Axios**: HTTP client

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Inspired by [SEO-AutoPilot](https://github.com/example/SEO-AutoPilot) for configuration and keyword extraction patterns
- [ReactBits](https://reactbits.dev) for UI animation inspiration

---

<p align="center">
  Made with dedication by <a href="https://github.com/JasonRobertDestiny">JasonRobertDestiny</a>
</p>
