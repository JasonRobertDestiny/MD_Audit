# 技术设计文档 (Technical Design Document)
# Markdown SEO 诊断 Agent

**文档版本**: v1.0
**创建日期**: 2025-11-27
**技术负责人**: Claude Code (Tech Architect)
**开发团队**: Codex

---

## 1. 系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                    (main.py + argparse)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Analyzer                            │
│               (MarkdownSEOAnalyzer)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Markdown Parser  → 2. Rules Engine  → 3. AI Engine  │
│  │  4. Score Calculator → 5. Report Generator           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
┌──────────────────┐  ┌──────────────┐  ┌────────────────────┐
│  Markdown Parser │  │ Rules Engine │  │    AI Engine       │
│  (parsers.py)    │  │(rules_engine.│  │   (ai_engine.py)   │
│                  │  │      py)     │  │                    │
│ - frontmatter    │  │              │  │ - OpenAI Client    │
│ - markdown       │  │ - META_*     │  │ - Prompt Builder   │
│ - BeautifulSoup  │  │ - STRUC_*    │  │ - Response Parser  │
│                  │  │ - KEY_*      │  │                    │
└──────────────────┘  └──────────────┘  └────────────────────┘
          │                  │                    │
          └──────────────────┴────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │   Data Models       │
                   │   (models.py)       │
                   │                     │
                   │ - SEOReport         │
                   │ - Issue             │
                   │ - Suggestion        │
                   │ - RuleCheckResult   │
                   └─────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │   Configuration     │
                   │   (config.py)       │
                   │                     │
                   │ - MarkdownSEOConfig │
                   │ - JSON loader       │
                   │ - Env var support   │
                   └─────────────────────┘
```

### 1.2 模块职责

| 模块 | 文件 | 职责 | 依赖 |
|------|------|------|------|
| **CLI层** | `main.py` | 命令行入口，参数解析 | argparse |
| **核心分析器** | `analyzer.py` | 协调解析、规则检查、AI分析 | 所有模块 |
| **Markdown解析器** | `parsers.py` | 解析Frontmatter和Markdown | frontmatter, markdown, BeautifulSoup |
| **规则引擎** | `rules_engine.py` | 执行静态规则检查 | config.py, models.py |
| **AI引擎** | `ai_engine.py` | LLM语义分析 | openai, config.py |
| **报告生成器** | `reporter.py` | 生成Markdown报告 | models.py |
| **数据模型** | `models.py` | Pydantic数据模型定义 | pydantic |
| **配置系统** | `config.py` | 规则配置管理 | dataclasses, json |

---

## 2. 目录结构

```
MD_Audit/
├── md_seo_agent/           # 主包目录
│   ├── __init__.py         # 包初始化
│   ├── models.py           # Pydantic数据模型
│   ├── config.py           # 配置系统
│   ├── parsers.py          # Markdown解析器
│   ├── rules_engine.py     # 规则检查引擎
│   ├── ai_engine.py        # AI语义分析引擎
│   ├── reporter.py         # 报告生成器
│   └── analyzer.py         # 核心分析器
├── config/                 # 配置文件目录
│   └── seo_rules.json      # 默认SEO规则配置
├── tests/                  # 测试目录
│   ├── __init__.py
│   ├── test_parsers.py
│   ├── test_rules_engine.py
│   ├── test_ai_engine.py
│   └── test_analyzer.py
├── examples/               # 示例文件
│   ├── sample_good.md      # 高分示例
│   ├── sample_bad.md       # 低分示例
│   └── sample_report.md    # 报告示例
├── docs/                   # 文档目录
│   ├── PRD.md              # 产品需求文档
│   ├── TECH_DESIGN.md      # 本文档
│   ├── CODEX_PROMPT.md     # Codex开发指令
│   └── TEST_PLAN.md        # 测试计划
├── main.py                 # CLI入口
├── requirements.txt        # 依赖列表
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

---

## 3. 数据模型设计

### 3.1 models.py 完整定义

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Issue(BaseModel):
    """诊断问题"""
    id: str = Field(..., description="问题ID，如META_01")
    severity: str = Field(..., description="严重程度: critical, high, medium, low")
    category: str = Field(..., description="分类: metadata, structure, keyword, content")
    message: str = Field(..., description="问题描述")
    current_value: Optional[str] = Field(None, description="当前值")
    expected_value: Optional[str] = Field(None, description="期望值")
    fix_example: Optional[str] = Field(None, description="修复示例代码")
    location: Optional[str] = Field(None, description="问题位置，如'Frontmatter第3行'")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "META_01",
                "severity": "critical",
                "category": "metadata",
                "message": "Title缺失",
                "current_value": "",
                "expected_value": "30-60字符的标题",
                "fix_example": "---\ntitle: \"Markdown SEO最佳实践\"\n---",
                "location": "Frontmatter"
            }
        }

class Suggestion(BaseModel):
    """优化建议"""
    priority: str = Field(..., description="优先级: critical, high, medium, low")
    category: str = Field(..., description="分类")
    recommendation: str = Field(..., description="建议内容")
    rationale: Optional[str] = Field(None, description="建议理由")
    example: Optional[str] = Field(None, description="示例")

class ScoreBreakdown(BaseModel):
    """分项得分"""
    dimension: str = Field(..., description="评分维度")
    score: float = Field(..., ge=0, le=100, description="得分")
    weight: float = Field(..., ge=0, le=1, description="权重")
    weighted_score: float = Field(..., ge=0, le=100, description="加权得分")
    status: str = Field(..., description="状态: critical/high/medium/low")

    @property
    def emoji(self) -> str:
        """根据分数返回emoji"""
        if self.score < 40:
            return "🔴"
        elif self.score < 60:
            return "🟠"
        elif self.score < 80:
            return "🟡"
        else:
            return "🟢"

class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    content_depth_score: float = Field(..., ge=0, le=10, description="内容深度评分")
    readability_score: float = Field(..., ge=0, le=10, description="可读性评分")
    keyword_relevance_score: Optional[float] = Field(None, ge=0, le=10, description="关键词相关性评分")
    recommendations: List[str] = Field(default_factory=list, description="AI建议列表")
    analysis_details: Optional[Dict[str, Any]] = Field(None, description="详细分析")

class RuleCheckResult(BaseModel):
    """规则检查结果"""
    rule_id: str
    passed: bool
    score: float = Field(ge=0, le=100)
    severity: str
    message: str
    details: Optional[Dict[str, Any]] = None

class SEOReport(BaseModel):
    """SEO诊断报告主体"""
    file_path: str = Field(..., description="分析的文件路径")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    total_score: float = Field(..., ge=0, le=100, description="总分")

    # 分项得分
    score_breakdown: List[ScoreBreakdown] = Field(..., description="各维度得分详情")

    # 问题列表
    critical_issues: List[Issue] = Field(default_factory=list)
    high_priority_issues: List[Issue] = Field(default_factory=list)
    medium_priority_issues: List[Issue] = Field(default_factory=list)
    low_priority_issues: List[Issue] = Field(default_factory=list)

    # 建议列表
    suggestions: List[Suggestion] = Field(default_factory=list)

    # AI分析结果
    ai_analysis: Optional[AIAnalysisResult] = Field(None, description="AI语义分析结果")

    # 关键词信息
    keywords_analyzed: List[str] = Field(default_factory=list, description="分析的关键词列表")
    auto_extracted_keywords: bool = Field(False, description="是否自动提取关键词")

    @property
    def emoji_badge(self) -> str:
        """总分对应的emoji徽章"""
        if self.total_score < 40:
            return "🔴"
        elif self.total_score < 60:
            return "🟠"
        elif self.total_score < 80:
            return "🟡"
        else:
            return "🟢"

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "examples/sample.md",
                "total_score": 68.5,
                "score_breakdown": [
                    {"dimension": "元数据", "score": 20, "weight": 0.3, "weighted_score": 6, "status": "high"},
                    {"dimension": "结构", "score": 18, "weight": 0.25, "weighted_score": 4.5, "status": "medium"},
                    {"dimension": "关键词", "score": 15, "weight": 0.2, "weighted_score": 3, "status": "medium"},
                    {"dimension": "AI语义", "score": 15, "weight": 0.25, "weighted_score": 3.75, "status": "medium"}
                ]
            }
        }
```

---

## 4. 核心模块设计

### 4.1 配置系统 (config.py)

**参考**: `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/seo_rules_config.py`

```python
import os
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class TitleRules:
    """Title规则配置"""
    min_length: int = 30
    max_length: int = 60
    ideal_min: int = 50
    ideal_max: int = 60
    critical_threshold: int = 30
    warning_threshold: int = 60

    def get_priority_for_length(self, length: int) -> str:
        """根据长度返回优先级"""
        if length == 0:
            return "critical"
        elif length < self.critical_threshold:
            return "high"
        elif length > self.warning_threshold:
            return "high"
        elif length < self.ideal_min:
            return "medium"
        else:
            return "low"

@dataclass
class DescriptionRules:
    """Description规则配置"""
    min_length: int = 120
    max_length: int = 160
    ideal_min: int = 150
    ideal_max: int = 160
    critical_threshold: int = 120

    def get_priority_for_length(self, length: int) -> str:
        if length == 0:
            return "high"
        elif length < self.critical_threshold:
            return "medium"
        elif length > self.max_length:
            return "medium"
        else:
            return "low"

@dataclass
class KeywordRules:
    """关键词规则配置"""
    min_density: float = 0.01  # 1%
    max_density: float = 0.025  # 2.5%
    ideal_density: float = 0.015  # 1.5%

    def get_priority_for_density(self, density: float) -> str:
        if density < self.min_density:
            return "medium"
        elif density > self.max_density:
            return "high"  # 关键词堆砌
        else:
            return "low"

@dataclass
class ContentRules:
    """内容规则配置"""
    min_word_count: int = 300
    recommended_min: int = 500
    ideal_word_count: int = 1000

    def get_priority_for_word_count(self, word_count: int) -> str:
        if word_count < self.min_word_count:
            return "high"
        elif word_count < self.recommended_min:
            return "medium"
        else:
            return "low"

@dataclass
class MarkdownSEOConfig:
    """Markdown SEO配置主类"""
    # 规则配置
    title: TitleRules = None
    description: DescriptionRules = None
    keywords: KeywordRules = None
    content: ContentRules = None

    # LLM配置
    llm_api_key: str = ""
    llm_base_url: str = "https://newapi.deepwisdom.ai/v1"
    llm_model: str = "gpt-4o"
    llm_timeout: int = 30
    llm_max_retries: int = 3
    enable_ai_analysis: bool = True

    def __post_init__(self):
        """初始化子规则"""
        if self.title is None:
            self.title = TitleRules()
        if self.description is None:
            self.description = DescriptionRules()
        if self.keywords is None:
            self.keywords = KeywordRules()
        if self.content is None:
            self.content = ContentRules()

    @classmethod
    def load_from_file(cls, config_file: str) -> 'MarkdownSEOConfig':
        """从JSON文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 实例化子规则
            title_rules = TitleRules(**config_data.get('title', {}))
            desc_rules = DescriptionRules(**config_data.get('description', {}))
            keyword_rules = KeywordRules(**config_data.get('keywords', {}))
            content_rules = ContentRules(**config_data.get('content', {}))

            # 创建主配置
            config = cls(
                title=title_rules,
                description=desc_rules,
                keywords=keyword_rules,
                content=content_rules,
                llm_api_key=config_data.get('llm_api_key', ''),
                llm_base_url=config_data.get('llm_base_url', 'https://newapi.deepwisdom.ai/v1'),
                llm_model=config_data.get('llm_model', 'gpt-4o'),
                llm_timeout=config_data.get('llm_timeout', 30),
                llm_max_retries=config_data.get('llm_max_retries', 3),
                enable_ai_analysis=config_data.get('enable_ai_analysis', True)
            )

            logger.info(f"✅ 配置已从文件加载: {config_file}")
            return config

        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {e}, 使用默认配置")
            return cls()

    @classmethod
    def load_from_env(cls) -> 'MarkdownSEOConfig':
        """从环境变量加载配置"""
        config_path = os.getenv('SEO_RULES_CONFIG')
        if config_path and os.path.exists(config_path):
            return cls.load_from_file(config_path)

        # 尝试默认配置路径
        default_config = Path(__file__).parent.parent / 'config' / 'seo_rules.json'
        if default_config.exists():
            return cls.load_from_file(str(default_config))

        # 使用默认配置
        config = cls()

        # 从环境变量读取LLM配置
        config.llm_api_key = os.getenv('OPENAI_API_KEY', 'sk-tVlvoM4GZwWVT7GQWWcU8aD7J0pGguWBGiPFd6l4uF4JVMRM')
        config.llm_base_url = os.getenv('OPENAI_BASE_URL', 'https://newapi.deepwisdom.ai/v1')
        config.llm_model = os.getenv('OPENAI_MODEL', 'gpt-4o')

        logger.info("✅ 使用默认配置")
        return config

    def save_to_file(self, config_file: str):
        """保存配置到JSON文件"""
        config_data = {
            'title': asdict(self.title),
            'description': asdict(self.description),
            'keywords': asdict(self.keywords),
            'content': asdict(self.content),
            'llm_api_key': self.llm_api_key,
            'llm_base_url': self.llm_base_url,
            'llm_model': self.llm_model,
            'llm_timeout': self.llm_timeout,
            'llm_max_retries': self.llm_max_retries,
            'enable_ai_analysis': self.enable_ai_analysis
        }

        Path(config_file).parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 配置已保存到: {config_file}")
```

### 4.2 Markdown解析器 (parsers.py)

```python
import frontmatter
import markdown
from bs4 import BeautifulSoup
from typing import Dict, Tuple, List
from collections import Counter
import re

# 参考: /mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py:16-94
def is_quality_keyword(keyword_phrase: str) -> bool:
    """
    过滤高质量关键词

    拒绝:
    - URL片段 (http://, www., .com等)
    - HTML/CSS代码 (<, >, {, }, class=等)
    - 纯数字或特殊字符
    - 停用词
    """
    words = keyword_phrase.lower().split()
    keyword_lower = keyword_phrase.lower()

    # Rule 0: 拒绝URL片段
    url_indicators = ['http', 'https', 'www', '.com', '.net', '://']
    if any(indicator in keyword_lower for indicator in url_indicators):
        return False

    # Rule 1: 拒绝HTML/CSS代码片段
    code_indicators = ['<', '>', '{', '}', 'class=', 'style=']
    if any(indicator in keyword_lower for indicator in code_indicators):
        return False

    # Rule 2: 拒绝纯数字或特殊字符
    if keyword_phrase.replace(' ', '').replace('-', '').isdigit():
        return False

    # Rule 3: 检查特殊字符比例
    special_char_count = sum(1 for c in keyword_phrase if not c.isalnum() and c != ' ')
    if special_char_count > len(keyword_phrase) * 0.3:
        return False

    # 单词检查
    if len(words) == 1:
        word = words[0]
        STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        if word in STOP_WORDS or len(word) < 3 or len(word) > 30:
            return False
        return True

    # 多词短语检查
    if len(words) > 5:  # 太长的短语不是好关键词
        return False

    return True

class MarkdownParser:
    """Markdown解析器"""

    def __init__(self):
        self.md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables'])

    def parse_file(self, file_path: str) -> Tuple[Dict, str, str]:
        """
        解析Markdown文件

        Returns:
            (frontmatter_dict, markdown_content, html_content)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        frontmatter_dict = post.metadata
        markdown_content = post.content
        html_content = self.md.convert(markdown_content)

        return frontmatter_dict, markdown_content, html_content

    def extract_structure(self, html_content: str) -> Dict:
        """
        从HTML提取结构信息

        Returns:
            {
                'h1_tags': [...],
                'h2_tags': [...],
                'images': [{'src': ..., 'alt': ...}],
                'links': [{'href': ..., 'text': ...}]
            }
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        structure = {
            'h1_tags': [h1.get_text() for h1 in soup.find_all('h1')],
            'h2_tags': [h2.get_text() for h2 in soup.find_all('h2')],
            'h3_tags': [h3.get_text() for h3 in soup.find_all('h3')],
            'images': [
                {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'has_alt': bool(img.get('alt'))
                }
                for img in soup.find_all('img')
            ],
            'links': [
                {
                    'href': a.get('href', ''),
                    'text': a.get_text().strip()
                }
                for a in soup.find_all('a', href=True)
            ]
        }

        return structure

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict]:
        """
        自动提取Top关键词

        Returns:
            [{'keyword': 'SEO工具', 'count': 8, 'density': 0.8}, ...]
        """
        # 分词（简单实现，仅英文）
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)

        # 统计词频
        word_counter = Counter(words)

        # 提取双词组
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        bigram_counter = Counter(bigrams)

        # 合并并过滤
        all_keywords = []
        for keyword, count in word_counter.most_common(top_n * 3):
            if is_quality_keyword(keyword):
                density = (count / total_words) * 100 if total_words > 0 else 0
                all_keywords.append({
                    'keyword': keyword,
                    'count': count,
                    'density': round(density, 2)
                })

        for keyword, count in bigram_counter.most_common(top_n * 2):
            if is_quality_keyword(keyword):
                # 双词组密度 = (count * 2) / total_words
                density = (count * 2 / total_words) * 100 if total_words > 0 else 0
                all_keywords.append({
                    'keyword': keyword,
                    'count': count,
                    'density': round(density, 2)
                })

        # 排序并返回Top N
        all_keywords.sort(key=lambda x: x['count'], reverse=True)
        return all_keywords[:top_n]
```

### 4.3 规则引擎 (rules_engine.py)

```python
from typing import List, Dict
from md_seo_agent.models import RuleCheckResult, Issue
from md_seo_agent.config import MarkdownSEOConfig

class RulesEngine:
    """规则检查引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config

    def check_all(
        self,
        frontmatter: Dict,
        html_content: str,
        structure: Dict,
        markdown_content: str,
        keywords_info: Dict
    ) -> Dict:
        """
        执行所有规则检查

        Returns:
            {
                'metadata_results': [...],
                'structure_results': [...],
                'keyword_results': [...]
            }
        """
        results = {
            'metadata_results': self.check_metadata(frontmatter),
            'structure_results': self.check_structure(structure),
            'keyword_results': self.check_keywords(keywords_info, frontmatter, markdown_content)
        }

        return results

    def check_metadata(self, frontmatter: Dict) -> List[RuleCheckResult]:
        """检查元数据 (META_*)"""
        results = []

        # META_01: Title检查
        title = frontmatter.get('title', '')
        title_length = len(title)

        if title_length == 0:
            results.append(RuleCheckResult(
                rule_id="META_01",
                passed=False,
                score=0,
                severity="critical",
                message="Title缺失",
                details={
                    'current_length': 0,
                    'expected_range': f"{self.config.title.min_length}-{self.config.title.max_length}"
                }
            ))
        elif title_length < self.config.title.min_length:
            priority = self.config.title.get_priority_for_length(title_length)
            results.append(RuleCheckResult(
                rule_id="META_01",
                passed=False,
                score=50,
                severity=priority,
                message=f"Title过短 ({title_length}字符，建议30-60)",
                details={'current': title, 'length': title_length}
            ))
        elif title_length > self.config.title.max_length:
            results.append(RuleCheckResult(
                rule_id="META_01",
                passed=False,
                score=50,
                severity="high",
                message=f"Title过长 ({title_length}字符，建议30-60)",
                details={'current': title, 'length': title_length}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="META_01",
                passed=True,
                score=100,
                severity="low",
                message="Title长度合适",
                details={'current': title, 'length': title_length}
            ))

        # META_02: Description检查
        description = frontmatter.get('description', '')
        desc_length = len(description)

        if desc_length == 0:
            results.append(RuleCheckResult(
                rule_id="META_02",
                passed=False,
                score=0,
                severity="high",
                message="Description缺失",
                details={'expected_range': '120-160'}
            ))
        elif desc_length < self.config.description.min_length:
            results.append(RuleCheckResult(
                rule_id="META_02",
                passed=False,
                score=30,
                severity="medium",
                message=f"Description过短 ({desc_length}字符，建议120-160)",
                details={'current': description, 'length': desc_length}
            ))
        elif desc_length > self.config.description.max_length:
            results.append(RuleCheckResult(
                rule_id="META_02",
                passed=False,
                score=70,
                severity="medium",
                message=f"Description过长 ({desc_length}字符，建议120-160)",
                details={'current': description, 'length': desc_length}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="META_02",
                passed=True,
                score=100,
                severity="low",
                message="Description长度合适",
                details={'current': description, 'length': desc_length}
            ))

        return results

    def check_structure(self, structure: Dict) -> List[RuleCheckResult]:
        """检查结构 (STRUC_*)"""
        results = []

        # STRUC_01: H1标签检查
        h1_count = len(structure.get('h1_tags', []))

        if h1_count == 0:
            results.append(RuleCheckResult(
                rule_id="STRUC_01",
                passed=False,
                score=0,
                severity="high",
                message="缺少H1标签",
                details={'count': 0}
            ))
        elif h1_count > 1:
            results.append(RuleCheckResult(
                rule_id="STRUC_01",
                passed=False,
                score=50,
                severity="medium",
                message=f"检测到{h1_count}个H1标签，建议只有1个",
                details={'count': h1_count, 'h1_list': structure['h1_tags']}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="STRUC_01",
                passed=True,
                score=100,
                severity="low",
                message="H1标签唯一性符合要求",
                details={'h1': structure['h1_tags'][0]}
            ))

        # STRUC_02: 图片Alt属性检查
        images = structure.get('images', [])
        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get('has_alt'))

        if total_images == 0:
            coverage = 100  # 没有图片视为100%覆盖
        else:
            coverage = (images_with_alt / total_images) * 100

        if coverage < 50:
            results.append(RuleCheckResult(
                rule_id="STRUC_02",
                passed=False,
                score=0,
                severity="high",
                message=f"图片Alt属性覆盖率过低 ({coverage:.0f}%)",
                details={'total': total_images, 'with_alt': images_with_alt}
            ))
        elif coverage < 80:
            results.append(RuleCheckResult(
                rule_id="STRUC_02",
                passed=False,
                score=50,
                severity="medium",
                message=f"图片Alt属性覆盖率偏低 ({coverage:.0f}%)",
                details={'total': total_images, 'with_alt': images_with_alt}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="STRUC_02",
                passed=True,
                score=100,
                severity="low",
                message=f"图片Alt属性覆盖率良好 ({coverage:.0f}%)",
                details={'total': total_images, 'with_alt': images_with_alt}
            ))

        # STRUC_03: 链接存在性检查
        links = structure.get('links', [])
        has_links = len(links) > 0

        if not has_links:
            results.append(RuleCheckResult(
                rule_id="STRUC_03",
                passed=False,
                score=0,
                severity="medium",
                message="文章缺少链接（内部或外部）",
                details={'count': 0}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="STRUC_03",
                passed=True,
                score=100,
                severity="low",
                message=f"文章包含{len(links)}个链接",
                details={'count': len(links)}
            ))

        return results

    def check_keywords(
        self,
        keywords_info: Dict,
        frontmatter: Dict,
        markdown_content: str
    ) -> List[RuleCheckResult]:
        """检查关键词 (KEY_*)"""
        results = []

        target_keyword = keywords_info.get('target_keyword')
        if not target_keyword:
            # 无关键词时跳过关键词检查
            return results

        keyword_data = keywords_info.get('keyword_data', {})
        density = keyword_data.get('density', 0)

        # KEY_01: 关键词密度检查
        priority = self.config.keywords.get_priority_for_density(density)

        if density < self.config.keywords.min_density:
            results.append(RuleCheckResult(
                rule_id="KEY_01",
                passed=False,
                score=30,
                severity=priority,
                message=f"关键词密度过低 ({density:.2f}%，建议1%-2.5%)",
                details={'keyword': target_keyword, 'density': density}
            ))
        elif density > self.config.keywords.max_density:
            results.append(RuleCheckResult(
                rule_id="KEY_02",
                passed=False,
                score=50,
                severity=priority,
                message=f"关键词密度过高，可能被判定为关键词堆砌 ({density:.2f}%)",
                details={'keyword': target_keyword, 'density': density}
            ))
        else:
            results.append(RuleCheckResult(
                rule_id="KEY_01",
                passed=True,
                score=100,
                severity="low",
                message=f"关键词密度合适 ({density:.2f}%)",
                details={'keyword': target_keyword, 'density': density}
            ))

        # KEY_02: 关键词位置检查
        title = frontmatter.get('title', '').lower()
        description = frontmatter.get('description', '').lower()
        first_paragraph = markdown_content[:500].lower()  # 首500字符

        in_title = target_keyword.lower() in title
        in_description = target_keyword.lower() in description
        in_first_para = target_keyword.lower() in first_paragraph

        position_score = 0
        if in_title:
            position_score += 33
        if in_description:
            position_score += 33
        if in_first_para:
            position_score += 34

        severity = "low" if position_score >= 67 else "medium"

        results.append(RuleCheckResult(
            rule_id="KEY_02",
            passed=(position_score >= 67),
            score=position_score,
            severity=severity,
            message=f"关键词位置覆盖 {position_score}%",
            details={
                'keyword': target_keyword,
                'in_title': in_title,
                'in_description': in_description,
                'in_first_paragraph': in_first_para
            }
        ))

        return results
```

---

## 5. AI引擎设计 (ai_engine.py)

```python
import os
import asyncio
import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from md_seo_agent.models import AIAnalysisResult
from md_seo_agent.config import MarkdownSEOConfig

logger = logging.getLogger(__name__)

class AIEngine:
    """AI语义分析引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            timeout=config.llm_timeout
        )

    async def analyze_semantics(
        self,
        content: str,
        keyword: Optional[str] = None
    ) -> Optional[AIAnalysisResult]:
        """
        LLM语义分析

        Args:
            content: 内容文本（限制长度2000字符）
            keyword: 可选的目标关键词

        Returns:
            AIAnalysisResult 或 None（失败时）
        """
        content_sample = content[:2000]  # 限制长度

        prompt = self._build_prompt(content_sample, keyword)

        for attempt in range(self.config.llm_max_retries):
            try:
                logger.info(f"🤖 调用LLM分析 (尝试 {attempt + 1}/{self.config.llm_max_retries})...")

                response = await self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=[
                        {"role": "system", "content": "你是专业的SEO分析师"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                result_json = json.loads(response.choices[0].message.content)

                ai_result = AIAnalysisResult(
                    content_depth_score=result_json.get('content_depth_score', 5.0),
                    readability_score=result_json.get('readability_score', 5.0),
                    keyword_relevance_score=result_json.get('keyword_relevance_score'),
                    recommendations=result_json.get('recommendations', []),
                    analysis_details=result_json.get('details', {})
                )

                logger.info(f"✅ LLM分析成功: 内容深度{ai_result.content_depth_score}/10, 可读性{ai_result.readability_score}/10")
                return ai_result

            except Exception as e:
                logger.warning(f"⚠️ LLM调用失败 (尝试 {attempt + 1}/{self.config.llm_max_retries}): {str(e)}")
                if attempt < self.config.llm_max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"❌ LLM分析最终失败，将降级到纯规则分析")
                    return None

    def _build_prompt(self, content: str, keyword: Optional[str]) -> str:
        """构建LLM Prompt"""
        keyword_section = f"\n目标关键词: {keyword}" if keyword else "\n目标关键词: 无（请基于内容自动判断）"

        prompt = f"""
你是SEO专家，请评估以下Markdown内容的质量。

内容摘要（前2000字符）:
{content}
{keyword_section}

请从以下维度评分（0-10分）：
1. **内容深度与价值** (content_depth_score):
   - 是否提供独特见解？
   - 是否有具体案例或数据支持？
   - 是否深入分析问题而非浅尝辄止？

2. **阅读流畅度** (readability_score):
   - 段落是否清晰简洁？
   - 句子长度是否适中？
   - 逻辑是否连贯？

3. **关键词相关性** (keyword_relevance_score, 仅在提供关键词时评分):
   - 内容是否围绕关键词展开？
   - 关键词使用是否自然？

4. **优化建议** (recommendations):
   - 提供3-5条具体的优化建议
   - 建议应可执行，非泛泛而谈

请以JSON格式输出：
{{
    "content_depth_score": 8.5,
    "readability_score": 9.0,
    "keyword_relevance_score": 7.5,
    "recommendations": [
        "建议1：增加具体案例",
        "建议2：缩短段落长度"
    ],
    "details": {{
        "strengths": ["优点1", "优点2"],
        "weaknesses": ["待改进1", "待改进2"]
    }}
}}
"""
        return prompt
```

---

## 6. 核心分析器 (analyzer.py)

```python
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
from md_seo_agent.config import MarkdownSEOConfig
from md_seo_agent.models import SEOReport, ScoreBreakdown, Issue, Suggestion, AIAnalysisResult
from md_seo_agent.parsers import MarkdownParser
from md_seo_agent.rules_engine import RulesEngine
from md_seo_agent.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class MarkdownSEOAnalyzer:
    """核心分析器"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config
        self.parser = MarkdownParser()
        self.rules_engine = RulesEngine(config)
        self.ai_engine = AIEngine(config) if config.enable_ai_analysis else None

    def analyze_file(
        self,
        md_file_path: str,
        keyword: Optional[str] = None
    ) -> SEOReport:
        """
        分析Markdown文件

        Args:
            md_file_path: Markdown文件路径
            keyword: 可选的目标关键词

        Returns:
            SEOReport对象
        """
        logger.info(f"🔍 开始分析文件: {md_file_path}")

        # 1. 解析Markdown
        frontmatter, markdown_content, html_content = self.parser.parse_file(md_file_path)
        structure = self.parser.extract_structure(html_content)

        # 2. 关键词处理
        keywords_info = self._process_keywords(markdown_content, keyword)

        # 3. 规则检查
        rule_results = self.rules_engine.check_all(
            frontmatter,
            html_content,
            structure,
            markdown_content,
            keywords_info
        )

        # 4. AI语义检查（异步）
        ai_result = None
        if self.ai_engine:
            ai_result = asyncio.run(
                self.ai_engine.analyze_semantics(markdown_content, keywords_info.get('target_keyword'))
            )

        # 5. 计算总分
        total_score, score_breakdown = self._calculate_score(rule_results, ai_result)

        # 6. 生成问题和建议
        issues = self._generate_issues(rule_results, frontmatter, structure, keywords_info)
        suggestions = self._generate_suggestions(rule_results, ai_result)

        # 7. 构建报告
        report = SEOReport(
            file_path=md_file_path,
            total_score=total_score,
            score_breakdown=score_breakdown,
            critical_issues=[i for i in issues if i.severity == 'critical'],
            high_priority_issues=[i for i in issues if i.severity == 'high'],
            medium_priority_issues=[i for i in issues if i.severity == 'medium'],
            low_priority_issues=[i for i in issues if i.severity == 'low'],
            suggestions=suggestions,
            ai_analysis=ai_result,
            keywords_analyzed=keywords_info.get('keywords_analyzed', []),
            auto_extracted_keywords=keywords_info.get('auto_extracted', False)
        )

        logger.info(f"✅ 分析完成，总分: {total_score:.1f}/100")
        return report

    def _process_keywords(self, markdown_content: str, user_keyword: Optional[str]) -> Dict:
        """处理关键词：用户提供或自动提取"""
        if user_keyword:
            # 用户提供关键词
            keyword_count = markdown_content.lower().count(user_keyword.lower())
            total_words = len(markdown_content.split())
            density = (keyword_count / total_words) * 100 if total_words > 0 else 0

            return {
                'target_keyword': user_keyword,
                'keyword_data': {
                    'count': keyword_count,
                    'density': density
                },
                'keywords_analyzed': [user_keyword],
                'auto_extracted': False
            }
        else:
            # 自动提取Top关键词
            extracted_keywords = self.parser.extract_keywords(markdown_content, top_n=10)
            top_keyword = extracted_keywords[0] if extracted_keywords else None

            if top_keyword:
                return {
                    'target_keyword': top_keyword['keyword'],
                    'keyword_data': {
                        'count': top_keyword['count'],
                        'density': top_keyword['density']
                    },
                    'keywords_analyzed': [kw['keyword'] for kw in extracted_keywords],
                    'auto_extracted': True
                }
            else:
                return {
                    'target_keyword': None,
                    'keywords_analyzed': [],
                    'auto_extracted': True
                }

    def _calculate_score(self, rule_results: Dict, ai_result: Optional[AIAnalysisResult]) -> tuple:
        """计算总分和分项得分"""
        # 元数据得分 (权重30%)
        metadata_scores = [r.score for r in rule_results['metadata_results']]
        metadata_score = sum(metadata_scores) / len(metadata_scores) if metadata_scores else 0
        metadata_weighted = (metadata_score / 100) * 30

        # 结构得分 (权重25%)
        structure_scores = [r.score for r in rule_results['structure_results']]
        structure_score = sum(structure_scores) / len(structure_scores) if structure_scores else 0
        structure_weighted = (structure_score / 100) * 25

        # 关键词得分 (权重20%)
        keyword_scores = [r.score for r in rule_results['keyword_results']]
        keyword_score = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 100
        keyword_weighted = (keyword_score / 100) * 20

        # AI语义得分 (权重25%)
        if ai_result:
            # 内容深度15% + 可读性10%
            ai_score = (ai_result.content_depth_score / 10 * 15) + (ai_result.readability_score / 10 * 10)
        else:
            ai_score = 0

        total_score = metadata_weighted + structure_weighted + keyword_weighted + ai_score

        # 分项得分详情
        score_breakdown = [
            ScoreBreakdown(
                dimension="元数据",
                score=metadata_score,
                weight=0.3,
                weighted_score=metadata_weighted,
                status=self._get_status(metadata_score)
            ),
            ScoreBreakdown(
                dimension="结构",
                score=structure_score,
                weight=0.25,
                weighted_score=structure_weighted,
                status=self._get_status(structure_score)
            ),
            ScoreBreakdown(
                dimension="关键词",
                score=keyword_score,
                weight=0.2,
                weighted_score=keyword_weighted,
                status=self._get_status(keyword_score)
            ),
            ScoreBreakdown(
                dimension="AI语义",
                score=ai_score / 0.25 if ai_score else 0,  # 转换回0-100
                weight=0.25,
                weighted_score=ai_score,
                status=self._get_status(ai_score / 0.25 if ai_score else 0)
            )
        ]

        return total_score, score_breakdown

    def _get_status(self, score: float) -> str:
        """根据分数返回状态"""
        if score < 40:
            return "critical"
        elif score < 60:
            return "high"
        elif score < 80:
            return "medium"
        else:
            return "low"

    def _generate_issues(
        self,
        rule_results: Dict,
        frontmatter: Dict,
        structure: Dict,
        keywords_info: Dict
    ) -> List[Issue]:
        """从规则检查结果生成问题列表"""
        issues = []

        # 元数据问题
        for result in rule_results['metadata_results']:
            if not result.passed:
                issue = self._rule_result_to_issue(result, frontmatter)
                if issue:
                    issues.append(issue)

        # 结构问题
        for result in rule_results['structure_results']:
            if not result.passed:
                issue = self._rule_result_to_issue(result, structure)
                if issue:
                    issues.append(issue)

        # 关键词问题
        for result in rule_results['keyword_results']:
            if not result.passed:
                issue = self._rule_result_to_issue(result, keywords_info)
                if issue:
                    issues.append(issue)

        return issues

    def _rule_result_to_issue(self, result, context) -> Optional[Issue]:
        """将RuleCheckResult转换为Issue"""
        # 这里根据具体的rule_id生成详细的Issue
        # 包含修复示例和位置信息
        # 具体实现略（Codex需要补充）
        pass

    def _generate_suggestions(
        self,
        rule_results: Dict,
        ai_result: Optional[AIAnalysisResult]
    ) -> List[Suggestion]:
        """生成优化建议"""
        suggestions = []

        # 从规则结果生成建议（略）
        # 从AI结果生成建议
        if ai_result and ai_result.recommendations:
            for rec in ai_result.recommendations:
                suggestions.append(Suggestion(
                    priority="medium",
                    category="content",
                    recommendation=rec,
                    rationale="AI分析建议"
                ))

        return suggestions
```

---

## 7. 报告生成器 (reporter.py)

```python
from md_seo_agent.models import SEOReport
from datetime import datetime

class ReportGenerator:
    """Markdown报告生成器"""

    def generate_markdown_report(self, report: SEOReport) -> str:
        """生成Markdown格式报告"""

        md_lines = []

        # 标题和基本信息
        md_lines.append(f"# 📝 SEO诊断报告\n")
        md_lines.append(f"**文件**: `{report.file_path}`")
        md_lines.append(f"**分析时间**: {report.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"**总分**: {report.total_score:.1f}/100 {report.emoji_badge}\n")

        # 评分详情表格
        md_lines.append("## 📊 评分详情\n")
        md_lines.append("| 维度 | 得分 | 权重 | 状态 |")
        md_lines.append("|------|------|------|------|")

        for breakdown in report.score_breakdown:
            md_lines.append(
                f"| {breakdown.dimension} | {breakdown.score:.0f}/{breakdown.weight*100:.0f} | "
                f"{breakdown.weight*100:.0f}% | {breakdown.emoji} {breakdown.status} |"
            )

        md_lines.append("\n---\n")

        # 严重问题
        if report.critical_issues:
            md_lines.append("## 🔴 严重问题 (Critical)\n")
            for issue in report.critical_issues:
                md_lines.append(f"### {issue.id}: {issue.message}\n")
                md_lines.append(f"- **严重程度**: {issue.severity}")
                if issue.current_value:
                    md_lines.append(f"- **当前值**: {issue.current_value}")
                if issue.expected_value:
                    md_lines.append(f"- **建议值**: {issue.expected_value}")
                if issue.fix_example:
                    md_lines.append(f"- **修复示例**:\n```yaml\n{issue.fix_example}\n```")
                md_lines.append("")

        # 高优先级问题
        if report.high_priority_issues:
            md_lines.append("## 🟠 高优先级警告 (High)\n")
            for issue in report.high_priority_issues:
                md_lines.append(f"### {issue.id}: {issue.message}\n")
                # 类似格式
                md_lines.append("")

        # AI优化建议
        if report.ai_analysis:
            md_lines.append("## 💡 AI优化建议\n")
            ai = report.ai_analysis
            md_lines.append(f"### 内容深度分析 ({ai.content_depth_score:.1f}/10)\n")
            md_lines.append("#### AI建议:\n")
            for rec in ai.recommendations:
                md_lines.append(f"- {rec}")
            md_lines.append("")

        # 快速修复清单
        md_lines.append("## 📝 快速修复清单\n")
        for issue in (report.critical_issues + report.high_priority_issues):
            md_lines.append(f"- [ ] {issue.message}")

        return "\n".join(md_lines)

    def save_report(self, report: SEOReport, output_path: str):
        """保存报告到文件"""
        markdown_content = self.generate_markdown_report(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
```

---

## 8. CLI入口 (main.py)

```python
import argparse
import logging
from pathlib import Path
from md_seo_agent.config import MarkdownSEOConfig
from md_seo_agent.analyzer import MarkdownSEOAnalyzer
from md_seo_agent.reporter import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description='Markdown SEO诊断Agent')
    parser.add_argument('file', type=str, help='Markdown文件路径')
    parser.add_argument('--keyword', type=str, help='目标关键词（可选）')
    parser.add_argument('--output', type=str, help='输出报告路径（可选）')
    parser.add_argument('--config', type=str, help='配置文件路径（可选）')

    args = parser.parse_args()

    # 加载配置
    if args.config:
        config = MarkdownSEOConfig.load_from_file(args.config)
    else:
        config = MarkdownSEOConfig.load_from_env()

    # 分析文件
    analyzer = MarkdownSEOAnalyzer(config)
    report = analyzer.analyze_file(args.file, args.keyword)

    # 生成报告
    reporter = ReportGenerator()
    markdown_report = reporter.generate_markdown_report(report)

    # 输出
    if args.output:
        reporter.save_report(report, args.output)
        print(f"✅ 报告已保存到: {args.output}")
    else:
        print(markdown_report)

if __name__ == "__main__":
    main()
```

---

## 9. 配置文件示例 (config/seo_rules.json)

```json
{
  "title": {
    "min_length": 30,
    "max_length": 60,
    "ideal_min": 50,
    "ideal_max": 60,
    "critical_threshold": 30,
    "warning_threshold": 60
  },
  "description": {
    "min_length": 120,
    "max_length": 160,
    "ideal_min": 150,
    "ideal_max": 160,
    "critical_threshold": 120
  },
  "keywords": {
    "min_density": 0.01,
    "max_density": 0.025,
    "ideal_density": 0.015
  },
  "content": {
    "min_word_count": 300,
    "recommended_min": 500,
    "ideal_word_count": 1000
  },
  "llm_api_key": "",
  "llm_base_url": "https://newapi.deepwisdom.ai/v1",
  "llm_model": "gpt-4o",
  "llm_timeout": 30,
  "llm_max_retries": 3,
  "enable_ai_analysis": true
}
```

---

## 10. 关键参考代码位置

| 功能 | 参考文件 | 行号 | 说明 |
|------|---------|------|------|
| 配置系统 | `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/seo_rules_config.py` | 全文 | dataclass设计模式 |
| 关键词过滤 | `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py` | 16-94 | `is_quality_keyword()` 实现 |
| Title检查 | `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py` | 653-672 | `analyze_title()` 实现 |
| Description检查 | `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py` | 673-696 | `analyze_description()` 实现 |
| 数据模型 | `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/page.py` | 88-216 | `Page` 类设计 |

---

**文档结束**

**下一步**: 请参考 `CODEX_PROMPT.md` 查看详细的开发指令，以及 `TEST_PLAN.md` 查看测试计划。
