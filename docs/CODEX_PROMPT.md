# Codex 开发指令：Markdown SEO 诊断 Agent

## 项目概览

你需要实现一个Python命令行工具，用于诊断Markdown文件的SEO质量。这个工具不是简单的规则检查器，而是结合了静态规则引擎和AI语义分析的双引擎系统。

**核心目标**：给定一个Markdown文件，输出100分制的诊断报告，报告包含具体问题、改进建议、以及AI对内容深度和可读性的评估。

**关键约束**：
- LLM调用失败时，系统必须降级为纯规则分析，不能直接报错
- 所有SEO规则都通过配置文件管理，不允许硬编码阈值
- 用户未提供关键词时，自动提取Top关键词（基于n-gram分析）
- 诊断报告必须是人类可读的Markdown格式，不是JSON

## 为什么这样设计

**双引擎架构的原因**：
规则引擎处理可量化的指标（标题长度、H1数量），AI引擎处理主观质量（内容是否满足搜索意图、可读性）。两者互补，规则引擎保证基准质量，AI引擎提供深度洞察。

**配置化规则的原因**：
不同场景的SEO要求不同。技术博客和营销页面对关键词密度的要求完全不一样。硬编码会导致系统僵化。参考`/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/seo_rules_config.py`的设计，所有阈值都可以调整。

**自动关键词提取的原因**：
大多数用户不知道应该用什么关键词。与其让他们猜，不如系统智能提取。参考`/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py:185-235`的实现，基于词频+质量过滤。

## 上下文文档

在开始编码前，你必须理解以下文档：

1. **PRD文档**：`/mnt/d/VibeCoding_pgm/MD_Audit/docs/PRD.md`
   - 包含完整的评分逻辑表格
   - 用户场景和工作流程
   - LLM API配置细节

2. **技术设计文档**：`/mnt/d/VibeCoding_pgm/MD_Audit/docs/TECH_DESIGN.md`
   - 完整的系统架构
   - 所有模块的代码模板
   - 数据模型定义

3. **参考代码**（不要照搬，理解模式）：
   - `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/analyzer.py`
     - 第16-94行：关键词质量过滤逻辑（拒绝URL片段、代码、技术术语）
     - 第185-235行：n-gram关键词提取（unigrams、bigrams、trigrams）
     - 第653-696行：标题和描述验证逻辑
   - `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/seo_rules_config.py`
     - 完整的配置系统设计，dataclass + JSON加载
   - `/mnt/d/SEO_develop/SEO-AutoPilot/pyseoanalyzer/page.py`
     - Pydantic数据模型封装模式

## 实现阶段（7个阶段）

### Phase 0: 项目脚手架（15分钟）

**目标**：创建项目目录结构和基础配置文件。

**执行步骤**：

1. 创建目录结构：
```bash
cd /mnt/d/VibeCoding_pgm/MD_Audit
mkdir -p md_audit/{parsers,engines,models,utils}
touch md_audit/__init__.py
touch md_audit/{config.py,analyzer.py,reporter.py,main.py}
touch md_audit/parsers/{__init__.py,markdown_parser.py}
touch md_audit/engines/{__init__.py,rules_engine.py,ai_engine.py}
touch md_audit/models/{__init__.py,data_models.py}
mkdir -p tests/{fixtures,unit}
touch tests/__init__.py
```

2. 创建依赖文件 `requirements.txt`：
```txt
pydantic>=2.0.0
python-frontmatter>=1.0.0
markdown>=3.4.0
beautifulsoup4>=4.12.0
openai>=1.0.0
pyyaml>=6.0
```

3. 创建默认配置文件 `config/default_config.json`：
```bash
mkdir -p config
```

内容参考技术设计文档中的配置JSON示例，包含：
- `title_rules`: min_length=30, max_length=60
- `description_rules`: min_length=120, max_length=160
- `keyword_rules`: min_density=0.01, max_density=0.03, max_auto_keywords=5
- `content_rules`: min_length=500, min_h1_count=1, max_h1_count=1
- `llm_api_key`: 留空（通过环境变量设置）
- `llm_base_url`: "https://newapi.deepwisdom.ai/v1"
- `llm_model`: "gpt-4o"

**验证检查点**：
- [ ] 运行 `tree md_audit` 确认目录结构正确
- [ ] 运行 `pip install -r requirements.txt` 成功安装依赖
- [ ] `config/default_config.json` 格式正确（用 `python -m json.tool` 验证）

### Phase 1: 数据模型（30分钟）

**目标**：定义类型安全的数据结构，确保整个系统的数据流是可预测的。

**实现文件**：`md_audit/models/data_models.py`

**关键点**：
- 使用Pydantic v2的 `BaseModel` 和 `Field` 进行验证
- 所有可选字段必须有明确的默认值（避免 `None` 歧义）
- 枚举类型用于固定选项（如 `severity`）

**核心代码模板**：

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict

class SeverityLevel(str, Enum):
    """诊断问题严重程度"""
    CRITICAL = "critical"  # 严重影响SEO
    WARNING = "warning"    # 需要改进
    INFO = "info"         # 建议优化
    SUCCESS = "success"   # 符合最佳实践

class DiagnosticItem(BaseModel):
    """单个诊断项"""
    category: str = Field(..., description="类别：metadata/structure/keywords/ai_semantics")
    check_name: str = Field(..., description="检查项名称，如'title_length'")
    severity: SeverityLevel
    score: float = Field(..., ge=0, le=100, description="该项得分（0-100）")
    message: str = Field(..., description="问题描述或成功信息")
    suggestion: str = Field(default="", description="改进建议")
    current_value: Optional[str] = Field(default=None, description="当前值")
    expected_value: Optional[str] = Field(default=None, description="期望值")

class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    relevance_score: float = Field(..., ge=0, le=100, description="内容相关性（0-100）")
    depth_score: float = Field(..., ge=0, le=100, description="内容深度（0-100）")
    readability_score: float = Field(..., ge=0, le=100, description="可读性（0-100）")
    overall_feedback: str = Field(default="", description="综合评价")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议列表")

class SEOReport(BaseModel):
    """完整SEO诊断报告"""
    file_path: str
    total_score: float = Field(..., ge=0, le=100)

    # 分项得分
    metadata_score: float = Field(default=0, ge=0, le=30, description="元数据得分（满分30）")
    structure_score: float = Field(default=0, ge=0, le=25, description="结构得分（满分25）")
    keyword_score: float = Field(default=0, ge=0, le=20, description="关键词得分（满分20）")
    ai_score: float = Field(default=0, ge=0, le=25, description="AI语义得分（满分25）")

    # 详细诊断
    diagnostics: List[DiagnosticItem] = Field(default_factory=list)
    ai_analysis: Optional[AIAnalysisResult] = None

    # 提取的元数据
    extracted_keywords: List[str] = Field(default_factory=list, description="自动提取的关键词")
    user_keywords: List[str] = Field(default_factory=list, description="用户提供的关键词")

class ParsedMarkdown(BaseModel):
    """解析后的Markdown内容"""
    frontmatter: Dict[str, any] = Field(default_factory=dict, description="YAML frontmatter")
    raw_content: str = Field(default="", description="去除frontmatter的Markdown正文")
    html_content: str = Field(default="", description="转换后的HTML")
    title: str = Field(default="", description="从frontmatter或H1提取的标题")
    description: str = Field(default="", description="从frontmatter提取的描述")
    h1_tags: List[str] = Field(default_factory=list, description="所有H1标签内容")
    h2_tags: List[str] = Field(default_factory=list, description="所有H2标签内容")
    images: List[Dict[str, str]] = Field(default_factory=list, description="图片列表，格式：[{'src': '...', 'alt': '...'}]")
    links: List[Dict[str, str]] = Field(default_factory=list, description="链接列表，格式：[{'href': '...', 'text': '...'}]")
    word_count: int = Field(default=0, description="正文字数")
```

**验证检查点**：
- [ ] 运行 `python -c "from md_audit.models.data_models import SEOReport; print(SEOReport.model_json_schema())"` 输出合法的JSON Schema
- [ ] 创建测试实例：`report = SEOReport(file_path="test.md", total_score=85.5)` 不报错
- [ ] 测试验证：`DiagnosticItem(category="test", check_name="test", severity="critical", score=101)` 应该抛出ValidationError

### Phase 2: 配置系统（30分钟）

**目标**：实现灵活的配置管理系统，支持JSON文件 + 环境变量覆盖。

**实现文件**：`md_audit/config.py`

**设计原则**：
- 配置加载优先级：环境变量 > 自定义配置文件 > 默认配置
- 所有阈值都可配置，不允许魔法数字
- LLM API密钥必须通过环境变量设置（安全考虑）

**核心代码**：

```python
import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

@dataclass
class TitleRules:
    """标题规则配置"""
    min_length: int = 30
    max_length: int = 60
    weight: float = 15.0  # 在30分元数据中的权重

@dataclass
class DescriptionRules:
    """描述规则配置"""
    min_length: int = 120
    max_length: int = 160
    weight: float = 15.0

@dataclass
class KeywordRules:
    """关键词规则配置"""
    min_density: float = 0.01  # 最小密度1%
    max_density: float = 0.03  # 最大密度3%
    max_auto_keywords: int = 5  # 自动提取关键词数量
    weight: float = 20.0

@dataclass
class ContentRules:
    """内容结构规则配置"""
    min_length: int = 500     # 最小字数
    min_h1_count: int = 1
    max_h1_count: int = 1
    min_image_alt_ratio: float = 0.8  # 80%的图片需要alt
    structure_weight: float = 25.0

@dataclass
class MarkdownSEOConfig:
    """Markdown SEO配置主类"""
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
        """初始化默认子配置"""
        if self.title is None:
            self.title = TitleRules()
        if self.description is None:
            self.description = DescriptionRules()
        if self.keywords is None:
            self.keywords = KeywordRules()
        if self.content is None:
            self.content = ContentRules()

    @classmethod
    def from_json(cls, json_path: str) -> 'MarkdownSEOConfig':
        """从JSON文件加载配置"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 递归实例化嵌套dataclass
        config = cls(
            title=TitleRules(**data.get('title_rules', {})),
            description=DescriptionRules(**data.get('description_rules', {})),
            keywords=KeywordRules(**data.get('keyword_rules', {})),
            content=ContentRules(**data.get('content_rules', {})),
            llm_api_key=data.get('llm_api_key', ''),
            llm_base_url=data.get('llm_base_url', 'https://newapi.deepwisdom.ai/v1'),
            llm_model=data.get('llm_model', 'gpt-4o'),
            llm_timeout=data.get('llm_timeout', 30),
            llm_max_retries=data.get('llm_max_retries', 3),
            enable_ai_analysis=data.get('enable_ai_analysis', True),
        )

        # 环境变量覆盖
        if os.getenv('MD_AUDIT_LLM_API_KEY'):
            config.llm_api_key = os.getenv('MD_AUDIT_LLM_API_KEY')
        if os.getenv('MD_AUDIT_LLM_MODEL'):
            config.llm_model = os.getenv('MD_AUDIT_LLM_MODEL')

        return config

    def to_json(self, json_path: str):
        """保存配置到JSON文件"""
        data = {
            'title_rules': asdict(self.title),
            'description_rules': asdict(self.description),
            'keyword_rules': asdict(self.keywords),
            'content_rules': asdict(self.content),
            'llm_api_key': '',  # 不保存敏感信息
            'llm_base_url': self.llm_base_url,
            'llm_model': self.llm_model,
            'llm_timeout': self.llm_timeout,
            'llm_max_retries': self.llm_max_retries,
            'enable_ai_analysis': self.enable_ai_analysis,
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def load_config(config_path: Optional[str] = None) -> MarkdownSEOConfig:
    """
    加载配置（优先级：自定义路径 > 默认路径）

    Args:
        config_path: 自定义配置文件路径

    Returns:
        配置实例
    """
    if config_path and Path(config_path).exists():
        return MarkdownSEOConfig.from_json(config_path)

    # 默认配置路径
    default_path = Path(__file__).parent.parent / "config" / "default_config.json"
    if default_path.exists():
        return MarkdownSEOConfig.from_json(str(default_path))

    # 使用硬编码默认值
    return MarkdownSEOConfig()
```

**验证检查点**：
- [ ] 创建测试配置文件，修改 `min_length`，加载后验证值是否正确
- [ ] 设置环境变量 `export MD_AUDIT_LLM_API_KEY=test_key`，加载配置后验证是否覆盖
- [ ] 运行 `python -c "from md_audit.config import load_config; c=load_config(); print(c.llm_base_url)"` 输出正确URL

### Phase 3: Markdown解析器（45分钟）

**目标**：解析Markdown文件，提取frontmatter、标题、描述、结构元素，并实现智能关键词提取。

**实现文件**：`md_audit/parsers/markdown_parser.py`

**核心功能**：
1. 解析YAML frontmatter（标题、描述、关键词）
2. 转换Markdown为HTML（用于结构分析）
3. 提取H1/H2标签、图片、链接
4. 智能关键词提取（基于n-gram + 质量过滤）

**关键词提取逻辑**（参考 `analyzer.py:16-94, 185-235`）：
- 计算unigrams（单词）、bigrams（两词组合）、trigrams（三词组合）的词频
- 过滤低质量词：URL片段、HTML/CSS代码、技术术语、停用词
- 按词频排序，返回Top N

**核心代码**：

```python
import re
from typing import List, Dict, Tuple
from pathlib import Path
import frontmatter
import markdown
from bs4 import BeautifulSoup
from md_audit.models.data_models import ParsedMarkdown

class MarkdownParser:
    """Markdown文件解析器"""

    # 关键词质量过滤规则（参考analyzer.py:16-94）
    LOW_QUALITY_PATTERNS = [
        r'^https?://',          # URL
        r'\.(com|org|net|io)',  # 域名
        r'<[^>]+>',            # HTML标签
        r'\{[^}]+\}',          # CSS/代码
        r'^\d+$',              # 纯数字
        r'^[^a-zA-Z\u4e00-\u9fa5]+$',  # 非字母/汉字
    ]

    # 停用词（简化版，生产环境需要更完整的停用词表）
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
        '这', '那', '你', '我', '他', '她', '它'
    }

    def __init__(self):
        self.md_parser = markdown.Markdown(extensions=['extra', 'codehilite'])

    def parse(self, file_path: str) -> ParsedMarkdown:
        """
        解析Markdown文件

        Args:
            file_path: Markdown文件路径

        Returns:
            解析后的结构化数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # 提取frontmatter
        fm = post.metadata
        raw_content = post.content

        # 转换为HTML
        html_content = self.md_parser.convert(raw_content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取标题（优先从frontmatter，否则从第一个H1）
        title = fm.get('title', '')
        if not title:
            h1 = soup.find('h1')
            title = h1.get_text(strip=True) if h1 else ''

        # 提取描述
        description = fm.get('description', '') or fm.get('excerpt', '')

        # 提取H1和H2标签
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]

        # 提取图片
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', '')
            })

        # 提取链接
        links = []
        for a in soup.find_all('a'):
            links.append({
                'href': a.get('href', ''),
                'text': a.get_text(strip=True)
            })

        # 计算字数（移除HTML标签后）
        text_content = soup.get_text()
        word_count = len(text_content.split())

        return ParsedMarkdown(
            frontmatter=fm,
            raw_content=raw_content,
            html_content=html_content,
            title=title,
            description=description,
            h1_tags=h1_tags,
            h2_tags=h2_tags,
            images=images,
            links=links,
            word_count=word_count
        )

    def extract_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """
        自动提取关键词（基于n-gram + 质量过滤）

        参考：analyzer.py:185-235

        Args:
            content: 文本内容
            max_keywords: 返回关键词数量

        Returns:
            关键词列表（按词频降序）
        """
        # 清理文本
        text = self._clean_text(content)
        words = text.split()

        # 计算n-gram词频
        keyword_freq: Dict[str, int] = {}

        # Unigrams
        for word in words:
            if self._is_quality_keyword(word):
                keyword_freq[word] = keyword_freq.get(word, 0) + 1

        # Bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if self._is_quality_keyword(bigram):
                keyword_freq[bigram] = keyword_freq.get(bigram, 0) + 1

        # Trigrams
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if self._is_quality_keyword(trigram):
                keyword_freq[trigram] = keyword_freq.get(trigram, 0) + 1

        # 按词频排序
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:max_keywords]]

    def _clean_text(self, text: str) -> str:
        """清理文本（移除代码块、HTML标签等）"""
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 标准化空白符
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _is_quality_keyword(self, keyword: str) -> bool:
        """
        判断关键词质量（参考analyzer.py:16-94）

        拒绝：URL片段、HTML/CSS代码、纯数字、停用词、过短/过长
        """
        keyword = keyword.strip().lower()

        # 长度检查
        if len(keyword) < 2 or len(keyword) > 50:
            return False

        # 停用词检查
        if keyword in self.STOP_WORDS:
            return False

        # 模式匹配检查
        for pattern in self.LOW_QUALITY_PATTERNS:
            if re.search(pattern, keyword):
                return False

        return True
```

**验证检查点**：
- [ ] 创建测试Markdown文件 `tests/fixtures/sample.md`（包含frontmatter、H1、H2、图片、链接）
- [ ] 运行解析：`parser = MarkdownParser(); result = parser.parse('tests/fixtures/sample.md')`
- [ ] 验证 `result.title` 不为空
- [ ] 验证 `result.h1_tags` 长度正确
- [ ] 测试关键词提取：`keywords = parser.extract_keywords("Python SEO optimization guide")`，验证返回合理的关键词

### Phase 4: 规则引擎（45分钟）

**目标**：实现基于配置的规则检查引擎，验证元数据、结构、关键词。

**实现文件**：`md_audit/engines/rules_engine.py`

**评分逻辑**（参考PRD评分表）：
- **元数据（30分）**：标题15分 + 描述15分
- **结构（25分）**：H1标签5分 + 图片alt 10分 + 内部链接10分
- **关键词（20分）**：密度10分 + 位置10分

**核心代码**：

```python
from typing import List
from md_audit.models.data_models import ParsedMarkdown, DiagnosticItem, SeverityLevel
from md_audit.config import MarkdownSEOConfig

class RulesEngine:
    """规则检查引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config

    def check_all(self, parsed: ParsedMarkdown, keywords: List[str]) -> tuple[float, List[DiagnosticItem]]:
        """
        执行所有规则检查

        Args:
            parsed: 解析后的Markdown数据
            keywords: 关键词列表（用户提供或自动提取）

        Returns:
            (总分, 诊断项列表)
        """
        diagnostics: List[DiagnosticItem] = []

        # 元数据检查（30分）
        metadata_score = self._check_metadata(parsed, diagnostics)

        # 结构检查（25分）
        structure_score = self._check_structure(parsed, diagnostics)

        # 关键词检查（20分）
        keyword_score = self._check_keywords(parsed, keywords, diagnostics)

        total_score = metadata_score + structure_score + keyword_score
        return total_score, diagnostics

    def _check_metadata(self, parsed: ParsedMarkdown, diagnostics: List[DiagnosticItem]) -> float:
        """检查元数据（标题 + 描述）"""
        score = 0.0

        # 标题检查（15分）
        title = parsed.title
        title_len = len(title)
        rules = self.config.title

        if not title:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="title_exists",
                severity=SeverityLevel.CRITICAL,
                score=0,
                message="缺少标题",
                suggestion="在frontmatter中添加title字段或使用H1标签",
                current_value="无",
                expected_value="必须存在"
            ))
        elif title_len < rules.min_length:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="title_length",
                severity=SeverityLevel.WARNING,
                score=7.5,  # 50%分数
                message=f"标题过短（{title_len}字符）",
                suggestion=f"标题建议在{rules.min_length}-{rules.max_length}字符之间",
                current_value=str(title_len),
                expected_value=f"{rules.min_length}-{rules.max_length}"
            ))
            score += 7.5
        elif title_len > rules.max_length:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="title_length",
                severity=SeverityLevel.WARNING,
                score=10,  # 67%分数
                message=f"标题过长（{title_len}字符）",
                suggestion=f"标题建议在{rules.min_length}-{rules.max_length}字符之间，过长可能被搜索引擎截断",
                current_value=str(title_len),
                expected_value=f"{rules.min_length}-{rules.max_length}"
            ))
            score += 10
        else:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="title_length",
                severity=SeverityLevel.SUCCESS,
                score=15,
                message=f"标题长度合适（{title_len}字符）",
                current_value=str(title_len),
                expected_value=f"{rules.min_length}-{rules.max_length}"
            ))
            score += 15

        # 描述检查（15分）
        desc = parsed.description
        desc_len = len(desc)
        desc_rules = self.config.description

        if not desc:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="description_exists",
                severity=SeverityLevel.CRITICAL,
                score=0,
                message="缺少描述",
                suggestion="在frontmatter中添加description字段",
                current_value="无",
                expected_value="必须存在"
            ))
        elif desc_len < desc_rules.min_length:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="description_length",
                severity=SeverityLevel.WARNING,
                score=7.5,
                message=f"描述过短（{desc_len}字符）",
                suggestion=f"描述建议在{desc_rules.min_length}-{desc_rules.max_length}字符之间",
                current_value=str(desc_len),
                expected_value=f"{desc_rules.min_length}-{desc_rules.max_length}"
            ))
            score += 7.5
        elif desc_len > desc_rules.max_length:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="description_length",
                severity=SeverityLevel.WARNING,
                score=10,
                message=f"描述过长（{desc_len}字符）",
                suggestion=f"描述建议在{desc_rules.min_length}-{desc_rules.max_length}字符之间，过长会被搜索引擎截断",
                current_value=str(desc_len),
                expected_value=f"{desc_rules.min_length}-{desc_rules.max_length}"
            ))
            score += 10
        else:
            diagnostics.append(DiagnosticItem(
                category="metadata",
                check_name="description_length",
                severity=SeverityLevel.SUCCESS,
                score=15,
                message=f"描述长度合适（{desc_len}字符）",
                current_value=str(desc_len),
                expected_value=f"{desc_rules.min_length}-{desc_rules.max_length}"
            ))
            score += 15

        return score

    def _check_structure(self, parsed: ParsedMarkdown, diagnostics: List[DiagnosticItem]) -> float:
        """检查结构（H1 + 图片alt + 内部链接）"""
        score = 0.0
        rules = self.config.content

        # H1标签检查（5分）
        h1_count = len(parsed.h1_tags)
        if h1_count < rules.min_h1_count:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="h1_count",
                severity=SeverityLevel.CRITICAL,
                score=0,
                message=f"缺少H1标签（当前{h1_count}个）",
                suggestion="每个页面应该有且仅有1个H1标签",
                current_value=str(h1_count),
                expected_value="1"
            ))
        elif h1_count > rules.max_h1_count:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="h1_count",
                severity=SeverityLevel.WARNING,
                score=2.5,
                message=f"H1标签过多（当前{h1_count}个）",
                suggestion="每个页面应该有且仅有1个H1标签，多个H1会分散页面主题",
                current_value=str(h1_count),
                expected_value="1"
            ))
            score += 2.5
        else:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="h1_count",
                severity=SeverityLevel.SUCCESS,
                score=5,
                message=f"H1标签数量正确（{h1_count}个）",
                current_value=str(h1_count),
                expected_value="1"
            ))
            score += 5

        # 图片alt检查（10分）
        total_images = len(parsed.images)
        images_with_alt = sum(1 for img in parsed.images if img['alt'])
        alt_ratio = images_with_alt / total_images if total_images > 0 else 1.0

        if total_images == 0:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="image_alt",
                severity=SeverityLevel.INFO,
                score=10,
                message="页面无图片，跳过alt检查",
            ))
            score += 10
        elif alt_ratio < rules.min_image_alt_ratio:
            alt_score = 10 * alt_ratio
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="image_alt",
                severity=SeverityLevel.WARNING,
                score=alt_score,
                message=f"图片alt覆盖率不足（{images_with_alt}/{total_images}）",
                suggestion="所有图片都应该添加描述性的alt属性以提升可访问性和SEO",
                current_value=f"{alt_ratio:.1%}",
                expected_value=f">={rules.min_image_alt_ratio:.0%}"
            ))
            score += alt_score
        else:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="image_alt",
                severity=SeverityLevel.SUCCESS,
                score=10,
                message=f"图片alt覆盖率良好（{images_with_alt}/{total_images}）",
                current_value=f"{alt_ratio:.1%}"
            ))
            score += 10

        # 内部链接检查（10分）
        # 简化逻辑：只检查是否存在链接
        link_count = len(parsed.links)
        if link_count == 0:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="internal_links",
                severity=SeverityLevel.WARNING,
                score=0,
                message="页面无内部链接",
                suggestion="添加相关文章的内部链接可以提升用户体验和SEO"
            ))
        elif link_count < 3:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="internal_links",
                severity=SeverityLevel.INFO,
                score=5,
                message=f"内部链接较少（{link_count}个）",
                suggestion="建议增加2-5个相关文章链接",
                current_value=str(link_count),
                expected_value="2-5"
            ))
            score += 5
        else:
            diagnostics.append(DiagnosticItem(
                category="structure",
                check_name="internal_links",
                severity=SeverityLevel.SUCCESS,
                score=10,
                message=f"内部链接数量合理（{link_count}个）",
                current_value=str(link_count)
            ))
            score += 10

        return score

    def _check_keywords(self, parsed: ParsedMarkdown, keywords: List[str], diagnostics: List[DiagnosticItem]) -> float:
        """检查关键词（密度 + 位置）"""
        if not keywords:
            diagnostics.append(DiagnosticItem(
                category="keywords",
                check_name="keywords_exist",
                severity=SeverityLevel.INFO,
                score=10,  # 没有关键词给基础分
                message="未提供关键词，跳过关键词检查"
            ))
            return 10.0

        score = 0.0
        content = parsed.raw_content.lower()
        total_words = len(content.split())

        # 关键词密度检查（10分）
        keyword_occurrences = sum(content.count(kw.lower()) for kw in keywords)
        density = keyword_occurrences / total_words if total_words > 0 else 0

        rules = self.config.keywords
        if density < rules.min_density:
            diagnostics.append(DiagnosticItem(
                category="keywords",
                check_name="keyword_density",
                severity=SeverityLevel.WARNING,
                score=5,
                message=f"关键词密度过低（{density:.2%}）",
                suggestion=f"建议关键词密度在{rules.min_density:.1%}-{rules.max_density:.1%}之间",
                current_value=f"{density:.2%}",
                expected_value=f"{rules.min_density:.1%}-{rules.max_density:.1%}"
            ))
            score += 5
        elif density > rules.max_density:
            diagnostics.append(DiagnosticItem(
                category="keywords",
                check_name="keyword_density",
                severity=SeverityLevel.WARNING,
                score=7,
                message=f"关键词密度过高（{density:.2%}），可能被判定为关键词堆砌",
                suggestion=f"建议关键词密度在{rules.min_density:.1%}-{rules.max_density:.1%}之间",
                current_value=f"{density:.2%}",
                expected_value=f"{rules.min_density:.1%}-{rules.max_density:.1%}"
            ))
            score += 7
        else:
            diagnostics.append(DiagnosticItem(
                category="keywords",
                check_name="keyword_density",
                severity=SeverityLevel.SUCCESS,
                score=10,
                message=f"关键词密度合理（{density:.2%}）",
                current_value=f"{density:.2%}"
            ))
            score += 10

        # 关键词位置检查（10分）
        # 检查关键词是否出现在标题、描述、H1
        kw_in_title = any(kw.lower() in parsed.title.lower() for kw in keywords)
        kw_in_desc = any(kw.lower() in parsed.description.lower() for kw in keywords)
        kw_in_h1 = any(kw.lower() in h1.lower() for h1 in parsed.h1_tags for kw in keywords)

        position_score = 0
        position_details = []

        if kw_in_title:
            position_score += 4
            position_details.append("标题✓")
        else:
            position_details.append("标题✗")

        if kw_in_desc:
            position_score += 3
            position_details.append("描述✓")
        else:
            position_details.append("描述✗")

        if kw_in_h1:
            position_score += 3
            position_details.append("H1✓")
        else:
            position_details.append("H1✗")

        severity = SeverityLevel.SUCCESS if position_score >= 7 else (
            SeverityLevel.WARNING if position_score >= 4 else SeverityLevel.CRITICAL
        )

        diagnostics.append(DiagnosticItem(
            category="keywords",
            check_name="keyword_position",
            severity=severity,
            score=position_score,
            message=f"关键词位置覆盖：{' | '.join(position_details)}",
            suggestion="关键词应该出现在标题、描述和H1中以获得最佳SEO效果" if position_score < 10 else "",
            current_value=' | '.join(position_details)
        ))
        score += position_score

        return score
```

**验证检查点**：
- [ ] 创建测试Markdown文件，故意设置标题过短（如"Test"）
- [ ] 运行规则引擎：`engine = RulesEngine(config); score, diags = engine.check_all(parsed, [])`
- [ ] 验证 `score < 100` 且诊断列表包含标题长度警告
- [ ] 测试关键词检查：提供关键词列表 `["Python", "SEO"]`，验证密度和位置检查正常

### Phase 5: AI引擎（45分钟）

**目标**：集成OpenAI API，实现语义分析（内容相关性、深度、可读性）+ 重试机制 + 优雅降级。

**实现文件**：`md_audit/engines/ai_engine.py`

**关键设计**：
- 使用 `openai` 库调用API
- 3次重试机制（网络错误、API限流）
- LLM返回JSON格式的评分和建议
- 失败时返回 `None`（由主分析器处理降级）

**核心代码**：

```python
import os
import time
import json
from typing import Optional
from openai import OpenAI
from md_audit.models.data_models import AIAnalysisResult, ParsedMarkdown
from md_audit.config import MarkdownSEOConfig

class AIEngine:
    """AI语义分析引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config

        if not config.llm_api_key:
            raise ValueError("LLM API Key未设置，请通过环境变量MD_AUDIT_LLM_API_KEY提供")

        self.client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            timeout=config.llm_timeout
        )

    def analyze(self, parsed: ParsedMarkdown, keywords: list[str]) -> Optional[AIAnalysisResult]:
        """
        AI语义分析（内容相关性、深度、可读性）

        Args:
            parsed: 解析后的Markdown数据
            keywords: 关键词列表

        Returns:
            AI分析结果，失败时返回None
        """
        if not self.config.enable_ai_analysis:
            return None

        # 构造prompt
        keyword_str = "、".join(keywords) if keywords else "未提供"
        prompt = f"""
你是一个SEO专家，请分析以下Markdown文章的质量。

**文章标题**：{parsed.title}
**文章描述**：{parsed.description}
**目标关键词**：{keyword_str}
**字数**：{parsed.word_count}

**文章内容**（前1000字）：
{parsed.raw_content[:1000]}

请从以下三个维度评分（0-100分）：

1. **内容相关性（relevance_score）**：文章内容与目标关键词的匹配度
2. **内容深度（depth_score）**：内容是否深入、是否提供实用价值
3. **可读性（readability_score）**：结构是否清晰、语言是否流畅

同时提供：
- **overall_feedback**：50字以内的综合评价
- **improvement_suggestions**：2-3条具体改进建议

**输出格式**（JSON）：
{{
  "relevance_score": 85,
  "depth_score": 75,
  "readability_score": 90,
  "overall_feedback": "文章与关键词相关性强，但缺乏实战案例",
  "improvement_suggestions": [
    "添加更多代码示例",
    "增加实际应用场景"
  ]
}}
"""

        # 重试机制
        for attempt in range(self.config.llm_max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的SEO分析专家，擅长评估内容质量。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # 低温度保证输出稳定
                    response_format={"type": "json_object"}  # 强制JSON输出
                )

                # 解析响应
                result_text = response.choices[0].message.content
                result_data = json.loads(result_text)

                # 验证并返回
                return AIAnalysisResult(
                    relevance_score=float(result_data.get('relevance_score', 0)),
                    depth_score=float(result_data.get('depth_score', 0)),
                    readability_score=float(result_data.get('readability_score', 0)),
                    overall_feedback=result_data.get('overall_feedback', ''),
                    improvement_suggestions=result_data.get('improvement_suggestions', [])
                )

            except json.JSONDecodeError as e:
                print(f"[警告] AI返回结果解析失败（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                continue

            except Exception as e:
                print(f"[警告] AI分析失败（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

        # 所有重试都失败
        print("[错误] AI分析失败，已达到最大重试次数，将跳过AI评分")
        return None

    def calculate_ai_score(self, ai_result: Optional[AIAnalysisResult]) -> float:
        """
        计算AI语义得分（满分25分）

        Args:
            ai_result: AI分析结果

        Returns:
            AI得分（0-25）
        """
        if not ai_result:
            return 0.0

        # 加权平均：相关性40% + 深度30% + 可读性30%
        weighted_score = (
            ai_result.relevance_score * 0.4 +
            ai_result.depth_score * 0.3 +
            ai_result.readability_score * 0.3
        )

        # 转换为25分制
        return weighted_score * 0.25
```

**验证检查点**：
- [ ] 设置环境变量：`export MD_AUDIT_LLM_API_KEY=sk-tVlvoM4GZwWVT7GQWWcU8aD7J0pGguWBGiPFd6l4uF4JVMRM`
- [ ] 创建测试：`engine = AIEngine(config); result = engine.analyze(parsed, ["Python"])`
- [ ] 验证 `result` 不为None 且包含 `relevance_score`, `depth_score`, `readability_score`
- [ ] 测试失败降级：故意设置错误的API key，验证返回None而不是抛出异常

### Phase 6: 分析器协调器 + 报告生成（45分钟）

**目标**：整合所有模块，协调规则引擎和AI引擎，生成Markdown诊断报告。

**实现文件**：
- `md_audit/analyzer.py`：主分析协调器
- `md_audit/reporter.py`：Markdown报告生成

**分析器核心逻辑**：
1. 解析Markdown文件
2. 提取或使用用户提供的关键词
3. 运行规则引擎（获得75分）
4. 运行AI引擎（获得25分）
5. 合并结果，生成报告

**核心代码（analyzer.py）**：

```python
from md_audit.parsers.markdown_parser import MarkdownParser
from md_audit.engines.rules_engine import RulesEngine
from md_audit.engines.ai_engine import AIEngine
from md_audit.models.data_models import SEOReport
from md_audit.config import MarkdownSEOConfig

class MarkdownSEOAnalyzer:
    """Markdown SEO分析协调器"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config
        self.parser = MarkdownParser()
        self.rules_engine = RulesEngine(config)

        # AI引擎可选（如果配置禁用或API key未设置）
        self.ai_engine = None
        if config.enable_ai_analysis and config.llm_api_key:
            try:
                self.ai_engine = AIEngine(config)
            except ValueError as e:
                print(f"[警告] AI引擎初始化失败：{e}")

    def analyze(self, file_path: str, user_keywords: list[str] = None) -> SEOReport:
        """
        分析Markdown文件

        Args:
            file_path: Markdown文件路径
            user_keywords: 用户提供的关键词（可选）

        Returns:
            完整的SEO诊断报告
        """
        # Step 1: 解析Markdown
        parsed = self.parser.parse(file_path)

        # Step 2: 确定关键词
        if user_keywords:
            keywords = user_keywords
            extracted = []
        else:
            # 自动提取
            keywords = self.parser.extract_keywords(
                parsed.raw_content,
                max_keywords=self.config.keywords.max_auto_keywords
            )
            extracted = keywords

        # Step 3: 运行规则引擎（最多75分）
        rules_score, diagnostics = self.rules_engine.check_all(parsed, keywords)

        # Step 4: 运行AI引擎（最多25分）
        ai_result = None
        ai_score = 0.0
        if self.ai_engine:
            ai_result = self.ai_engine.analyze(parsed, keywords)
            ai_score = self.ai_engine.calculate_ai_score(ai_result)

        # Step 5: 计算总分
        total_score = rules_score + ai_score

        # Step 6: 分类得分（用于报告展示）
        metadata_score = sum(d.score for d in diagnostics if d.category == "metadata")
        structure_score = sum(d.score for d in diagnostics if d.category == "structure")
        keyword_score = sum(d.score for d in diagnostics if d.category == "keywords")

        # Step 7: 构建报告
        return SEOReport(
            file_path=file_path,
            total_score=round(total_score, 1),
            metadata_score=round(metadata_score, 1),
            structure_score=round(structure_score, 1),
            keyword_score=round(keyword_score, 1),
            ai_score=round(ai_score, 1),
            diagnostics=diagnostics,
            ai_analysis=ai_result,
            extracted_keywords=extracted,
            user_keywords=user_keywords or []
        )
```

**报告生成器核心代码（reporter.py）**：

```python
from md_audit.models.data_models import SEOReport, SeverityLevel

class MarkdownReporter:
    """Markdown诊断报告生成器"""

    SEVERITY_EMOJI = {
        SeverityLevel.CRITICAL: "🔴",
        SeverityLevel.WARNING: "🟠",
        SeverityLevel.INFO: "🟡",
        SeverityLevel.SUCCESS: "🟢"
    }

    def generate(self, report: SEOReport) -> str:
        """
        生成Markdown格式的诊断报告

        Args:
            report: SEO诊断报告数据

        Returns:
            Markdown格式的报告文本
        """
        lines = []

        # 标题
        lines.append(f"# SEO诊断报告\n")
        lines.append(f"**文件**: `{report.file_path}`\n")
        lines.append(f"**总分**: {report.total_score:.1f}/100\n")

        # 分项得分
        lines.append("## 评分详情\n")
        lines.append(f"- **元数据**: {report.metadata_score:.1f}/30")
        lines.append(f"- **结构**: {report.structure_score:.1f}/25")
        lines.append(f"- **关键词**: {report.keyword_score:.1f}/20")
        lines.append(f"- **AI语义**: {report.ai_score:.1f}/25\n")

        # 关键词信息
        if report.user_keywords:
            lines.append(f"**目标关键词**: {', '.join(report.user_keywords)}")
        if report.extracted_keywords:
            lines.append(f"**自动提取关键词**: {', '.join(report.extracted_keywords)}\n")

        # 诊断详情（按类别分组）
        lines.append("## 诊断详情\n")

        for category_name, category_key in [
            ("元数据检查", "metadata"),
            ("结构检查", "structure"),
            ("关键词检查", "keywords")
        ]:
            category_items = [d for d in report.diagnostics if d.category == category_key]
            if category_items:
                lines.append(f"### {category_name}\n")
                for item in category_items:
                    emoji = self.SEVERITY_EMOJI[item.severity]
                    lines.append(f"{emoji} **{item.check_name}** ({item.score:.1f}分)")
                    lines.append(f"   - {item.message}")
                    if item.suggestion:
                        lines.append(f"   - 💡 建议: {item.suggestion}")
                    if item.current_value and item.expected_value:
                        lines.append(f"   - 当前值: `{item.current_value}` | 期望值: `{item.expected_value}`")
                    lines.append("")

        # AI分析结果
        if report.ai_analysis:
            lines.append("## AI语义分析\n")
            ai = report.ai_analysis
            lines.append(f"**综合评价**: {ai.overall_feedback}\n")
            lines.append(f"- 内容相关性: {ai.relevance_score:.1f}/100")
            lines.append(f"- 内容深度: {ai.depth_score:.1f}/100")
            lines.append(f"- 可读性: {ai.readability_score:.1f}/100\n")

            if ai.improvement_suggestions:
                lines.append("**改进建议**:\n")
                for i, suggestion in enumerate(ai.improvement_suggestions, 1):
                    lines.append(f"{i}. {suggestion}")
                lines.append("")

        # 总结
        lines.append("## 总结\n")
        if report.total_score >= 90:
            lines.append("✅ SEO质量优秀，继续保持！")
        elif report.total_score >= 70:
            lines.append("⚠️ SEO质量良好，但仍有优化空间。")
        else:
            lines.append("❌ SEO质量需要显著改进，请重点关注上述诊断问题。")

        return "\n".join(lines)
```

**验证检查点**：
- [ ] 创建完整的测试Markdown文件（包含所有元素）
- [ ] 运行完整分析：`analyzer = MarkdownSEOAnalyzer(config); report = analyzer.analyze('test.md')`
- [ ] 验证 `report.total_score` 在0-100之间
- [ ] 生成报告：`reporter = MarkdownReporter(); md_report = reporter.generate(report)`
- [ ] 验证报告包含所有section（评分详情、诊断详情、AI分析、总结）

### Phase 7: CLI入口（30分钟）

**目标**：实现命令行界面，支持多种使用场景。

**实现文件**：`md_audit/main.py`

**支持的命令**：
```bash
# 基础用法（自动提取关键词）
md-audit analyze docs/article.md

# 指定关键词
md-audit analyze docs/article.md -k "Python" "SEO" "优化"

# 指定配置文件
md-audit analyze docs/article.md --config custom_config.json

# 输出报告到文件
md-audit analyze docs/article.md -o report.md

# 禁用AI分析（仅规则检查）
md-audit analyze docs/article.md --no-ai
```

**核心代码**：

```python
import argparse
from pathlib import Path
from md_audit.config import load_config
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.reporter import MarkdownReporter

def main():
    parser = argparse.ArgumentParser(
        description="Markdown SEO诊断工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  md-audit analyze article.md
  md-audit analyze article.md -k "Python" "SEO"
  md-audit analyze article.md --config custom.json -o report.md
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # analyze子命令
    analyze_parser = subparsers.add_parser('analyze', help='分析Markdown文件')
    analyze_parser.add_argument('file', type=str, help='Markdown文件路径')
    analyze_parser.add_argument('-k', '--keywords', nargs='+', help='目标关键词（可选）')
    analyze_parser.add_argument('--config', type=str, help='配置文件路径（可选）')
    analyze_parser.add_argument('-o', '--output', type=str, help='输出报告文件路径（可选）')
    analyze_parser.add_argument('--no-ai', action='store_true', help='禁用AI分析')

    args = parser.parse_args()

    if args.command == 'analyze':
        # 加载配置
        config = load_config(args.config)

        # 覆盖AI开关
        if args.no_ai:
            config.enable_ai_analysis = False

        # 验证文件存在
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"错误：文件不存在 {args.file}")
            return 1

        # 运行分析
        print(f"正在分析 {args.file} ...")
        analyzer = MarkdownSEOAnalyzer(config)
        report = analyzer.analyze(str(file_path), user_keywords=args.keywords)

        # 生成报告
        reporter = MarkdownReporter()
        report_md = reporter.generate(report)

        # 输出
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report_md)
            print(f"✅ 报告已保存到 {args.output}")
        else:
            print("\n" + report_md)

        # 返回状态码（基于得分）
        return 0 if report.total_score >= 70 else 1

    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    exit(main())
```

**setup.py配置**（支持 `pip install` 安装）：

```python
from setuptools import setup, find_packages

setup(
    name='md-audit',
    version='1.0.0',
    description='Markdown SEO诊断工具',
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.0.0',
        'python-frontmatter>=1.0.0',
        'markdown>=3.4.0',
        'beautifulsoup4>=4.12.0',
        'openai>=1.0.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'md-audit=md_audit.main:main',
        ],
    },
    python_requires='>=3.8',
)
```

**验证检查点**：
- [ ] 运行 `pip install -e .` 安装包
- [ ] 测试命令：`md-audit analyze tests/fixtures/sample.md`
- [ ] 验证输出包含完整报告
- [ ] 测试参数：`md-audit analyze sample.md -k "test" -o output.md --no-ai`
- [ ] 验证 `output.md` 文件正确生成

## 测试要求

每个阶段完成后必须验证：

1. **单元测试覆盖**：
   - `tests/unit/test_parser.py`：测试关键词提取、Markdown解析
   - `tests/unit/test_rules_engine.py`：测试所有规则检查逻辑
   - `tests/unit/test_ai_engine.py`：测试AI调用和降级逻辑
   - `tests/unit/test_analyzer.py`：测试端到端分析流程

2. **集成测试**：
   - 创建 `tests/fixtures/` 目录，包含多个测试Markdown文件：
     - `good_example.md`：高质量文章（期望得分>85）
     - `bad_example.md`：低质量文章（期望得分<50）
     - `medium_example.md`：中等质量（期望得分60-80）

3. **手动验证**：
   - 运行 `md-audit analyze` 对实际博客文章进行分析
   - 验证AI分析结果是否合理
   - 验证Markdown报告格式是否清晰

## 常见问题排查

### 问题1：LLM调用失败

**症状**：AI分析始终返回None

**排查步骤**：
1. 验证API key是否正确：`echo $MD_AUDIT_LLM_API_KEY`
2. 验证API endpoint可访问：`curl https://newapi.deepwisdom.ai/v1/models`
3. 检查网络代理设置
4. 查看详细错误日志（在 `ai_engine.py` 中添加 `print` 语句）

### 问题2：关键词提取质量差

**症状**：自动提取的关键词全是无意义的词

**排查步骤**：
1. 检查 `LOW_QUALITY_PATTERNS` 是否覆盖常见噪声
2. 扩充停用词表（参考jieba分词的停用词表）
3. 调整n-gram权重（优先bigram和trigram）

### 问题3：评分不合理

**症状**：明显高质量文章得分很低

**排查步骤**：
1. 检查配置文件的阈值是否合理（如标题长度范围）
2. 验证规则引擎的权重分配
3. 对比诊断详情，找出扣分项

### 问题4：中文分词不准确

**症状**：中文关键词提取效果差

**解决方案**：
集成jieba分词库：
```python
import jieba

def extract_keywords_chinese(self, content: str, max_keywords: int = 5) -> List[str]:
    words = jieba.cut(content)
    # 后续逻辑同英文版
```

## 优化建议（可选，不在MVP范围）

1. **缓存机制**：缓存LLM分析结果，避免重复调用
2. **批量分析**：支持 `md-audit analyze docs/*.md` 批量处理
3. **Web界面**：使用Streamlit创建交互式界面
4. **CI/CD集成**：提供GitHub Action，自动检查PR中的Markdown文件
5. **自定义规则**：允许用户编写Python插件扩展规则引擎

## 交付清单

完成后，项目应包含：

- [x] 完整的代码实现（7个模块）
- [x] 单元测试和集成测试
- [x] `README.md`（包含安装、使用、配置说明）
- [x] `requirements.txt` 和 `setup.py`
- [x] `config/default_config.json` 默认配置
- [x] `tests/fixtures/` 测试用Markdown文件
- [x] 示例输出报告 `examples/sample_report.md`

## 验收标准

1. 运行 `md-audit analyze tests/fixtures/good_example.md` 得分>85
2. 运行 `md-audit analyze tests/fixtures/bad_example.md` 得分<50
3. AI分析功能正常（或优雅降级到规则引擎）
4. 报告格式清晰，包含具体改进建议
5. 所有单元测试通过

## 最后提醒

- **不要照搬参考代码**，理解其设计模式后重新实现
- **优先保证核心功能**，不要过度优化边缘情况
- **测试驱动开发**，先写测试再实现功能
- **遇到问题先查日志**，添加足够的 `print` 或 `logging` 语句
- **API key安全**，永远不要硬编码在代码中

开始编码吧！有问题随时参考PRD和技术设计文档。
