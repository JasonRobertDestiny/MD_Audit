# 测试计划：Markdown SEO 诊断 Agent

## 测试哲学

这个项目的测试不是为了堆砌覆盖率数字，而是要回答三个问题：

1. **规则引擎是否准确**？给定一个Markdown文件，评分逻辑是否符合SEO最佳实践？
2. **AI引擎是否可靠**？LLM调用失败时，系统是否优雅降级而不是崩溃？
3. **端到端是否完整**？从CLI输入到Markdown报告输出，整个链路是否无断点？

测试的重点不是覆盖所有分支，而是验证核心假设：这个工具能否帮助真实用户改进SEO质量。

## 测试策略

### 三层测试金字塔

```
        /\
       /  \  E2E测试（3个场景）
      /----\
     /      \ 集成测试（5个模块交互）
    /--------\
   /          \ 单元测试（20+用例）
  /------------\
```

**原因**：
- 单元测试保证每个规则逻辑正确（如标题长度检查）
- 集成测试保证模块协作无误（如规则引擎+AI引擎）
- E2E测试保证真实用户场景可用（如CLI命令到报告输出）

### 测试数据设计原则

不要创建虚假的"完美测试数据"，而是使用真实博客文章的变体：

- **高质量样本**：从优秀技术博客（如阮一峰的博客）摘录，期望得分>85
- **低质量样本**：故意制造的反面案例（无标题、无描述、关键词堆砌），期望得分<50
- **边界案例**：标题刚好60字符、描述刚好160字符，测试边界判断

避免"为了测试而测试"的数据，每个测试用例都应该反映真实SEO问题。

## 单元测试计划

### 模块1: MarkdownParser (`tests/unit/test_parser.py`)

**测试目标**：验证Markdown解析和关键词提取的正确性。

#### 测试用例1.1: Frontmatter解析

**输入**：
```markdown
---
title: Python SEO优化指南
description: 本文介绍如何使用Python优化网站SEO
keywords: [Python, SEO, 优化]
---
# 正文内容
```

**期望输出**：
- `parsed.title == "Python SEO优化指南"`
- `parsed.description == "本文介绍如何使用Python优化网站SEO"`
- `parsed.frontmatter['keywords'] == ['Python', 'SEO', '优化']`

**验证方法**：
```python
def test_frontmatter_parsing():
    parser = MarkdownParser()
    result = parser.parse('tests/fixtures/with_frontmatter.md')
    assert result.title == "Python SEO优化指南"
    assert len(result.description) > 0
```

#### 测试用例1.2: H1标签提取

**输入**：
```markdown
# 主标题

## 副标题1
## 副标题2
```

**期望输出**：
- `parsed.h1_tags == ["主标题"]`
- `parsed.h2_tags == ["副标题1", "副标题2"]`

**为什么重要**：H1数量是SEO的关键指标，多个H1会被扣分。

#### 测试用例1.3: 图片Alt提取

**输入**：
```markdown
![有alt的图片](image1.jpg)
![](image2.jpg)
```

**期望输出**：
- `parsed.images[0]['alt'] == "有alt的图片"`
- `parsed.images[1]['alt'] == ""`

**验证逻辑**：
计算alt覆盖率 = 1/2 = 50%，应该触发警告。

#### 测试用例1.4: 关键词提取（质量过滤）

**输入文本**：
```
Python SEO optimization https://example.com <div class="container">
Python best practices for SEO optimization
```

**期望输出**：
- 提取的关键词应包含 "Python SEO optimization", "Python best practices"
- 不应包含 "https://example.com", "<div class="container">"（URL和HTML）

**验证方法**：
```python
def test_keyword_quality_filtering():
    parser = MarkdownParser()
    text = "Python SEO https://example.com <div>"
    keywords = parser.extract_keywords(text, max_keywords=5)

    # 应该提取有效关键词
    assert any('Python' in kw for kw in keywords)

    # 不应该提取URL和HTML
    assert not any('https://' in kw for kw in keywords)
    assert not any('<div>' in kw for kw in keywords)
```

#### 测试用例1.5: 中英文混合关键词

**输入**：
```
Python编程 机器学习 deep learning 神经网络
```

**期望输出**：
关键词列表应该包含中文词和英文词（测试分词逻辑）

**边界情况**：
- 全中文内容
- 全英文内容
- 代码片段（应被过滤）

### 模块2: RulesEngine (`tests/unit/test_rules_engine.py`)

**测试目标**：验证评分逻辑的准确性和公平性。

#### 测试用例2.1: 标题长度评分

**测试矩阵**：

| 标题长度 | 期望得分 | 严重程度 | 原因 |
|---------|---------|---------|------|
| 0字符 | 0/15 | CRITICAL | 缺少标题 |
| 20字符 | 7.5/15 | WARNING | 过短 |
| 45字符 | 15/15 | SUCCESS | 合适 |
| 70字符 | 10/15 | WARNING | 过长 |

**验证方法**：
```python
@pytest.mark.parametrize("title,expected_score,expected_severity", [
    ("", 0, SeverityLevel.CRITICAL),
    ("短标题", 7.5, SeverityLevel.WARNING),
    ("这是一个长度合适的标题大约在30到60字符之间", 15, SeverityLevel.SUCCESS),
    ("这是一个非常非常非常长的标题超过了60字符的限制会被搜索引擎截断显示不完整", 10, SeverityLevel.WARNING),
])
def test_title_scoring(title, expected_score, expected_severity):
    config = MarkdownSEOConfig()
    engine = RulesEngine(config)

    parsed = ParsedMarkdown(title=title, ...)
    score, diagnostics = engine.check_all(parsed, [])

    title_item = next(d for d in diagnostics if d.check_name == "title_length")
    assert title_item.score == expected_score
    assert title_item.severity == expected_severity
```

#### 测试用例2.2: 描述长度评分

同标题逻辑，但范围是120-160字符。

#### 测试用例2.3: H1标签数量评分

**测试矩阵**：

| H1数量 | 期望得分 | 原因 |
|-------|---------|------|
| 0 | 0/5 | 缺少主标题 |
| 1 | 5/5 | 完美 |
| 2 | 2.5/5 | 分散主题 |

#### 测试用例2.4: 图片Alt覆盖率评分

**场景1**：5张图片，3张有alt → 覆盖率60% → 得分6/10
**场景2**：0张图片 → 跳过检查 → 得分10/10（不扣分）
**场景3**：5张图片，全部有alt → 覆盖率100% → 得分10/10

**关键逻辑**：
```python
alt_ratio = images_with_alt / total_images if total_images > 0 else 1.0
score = 10 * alt_ratio
```

#### 测试用例2.5: 关键词密度评分

**测试矩阵**：

| 关键词密度 | 期望得分 | 原因 |
|-----------|---------|------|
| 0.5% | 5/10 | 过低 |
| 2.0% | 10/10 | 合理 |
| 5.0% | 7/10 | 过高（关键词堆砌） |

**验证方法**：
```python
def test_keyword_density():
    content = " ".join(["word"] * 100)  # 100个词
    content += " ".join(["keyword"] * 2)  # 2个关键词
    # 密度 = 2/102 ≈ 1.96%

    parsed = ParsedMarkdown(raw_content=content, ...)
    score, diags = engine.check_all(parsed, ["keyword"])

    density_item = next(d for d in diags if d.check_name == "keyword_density")
    assert density_item.score == 10  # 在1%-3%范围内
```

#### 测试用例2.6: 关键词位置评分

**评分规则**：
- 出现在标题：+4分
- 出现在描述：+3分
- 出现在H1：+3分

**测试场景**：
```python
def test_keyword_position():
    # 场景1：关键词在标题和描述中
    parsed1 = ParsedMarkdown(
        title="Python SEO Guide",
        description="Learn Python for SEO",
        h1_tags=["Introduction"],
        ...
    )
    score1, diags1 = engine.check_all(parsed1, ["Python"])
    position_item1 = next(d for d in diags1 if d.check_name == "keyword_position")
    assert position_item1.score == 7  # 4(标题) + 3(描述)

    # 场景2：关键词仅在H1中
    parsed2 = ParsedMarkdown(
        title="Guide",
        description="Learn basics",
        h1_tags=["Python Tutorial"],
        ...
    )
    score2, diags2 = engine.check_all(parsed2, ["Python"])
    position_item2 = next(d for d in diags2 if d.check_name == "keyword_position")
    assert position_item2.score == 3  # 仅H1
```

### 模块3: AIEngine (`tests/unit/test_ai_engine.py`)

**测试目标**：验证LLM调用和错误处理的健壮性。

#### 测试用例3.1: 成功调用LLM

**Mock策略**：使用 `unittest.mock` 模拟OpenAI响应

```python
from unittest.mock import Mock, patch

def test_ai_analysis_success():
    config = MarkdownSEOConfig(llm_api_key="test_key")
    engine = AIEngine(config)

    # Mock OpenAI响应
    mock_response = Mock()
    mock_response.choices[0].message.content = json.dumps({
        "relevance_score": 85,
        "depth_score": 75,
        "readability_score": 90,
        "overall_feedback": "内容质量高",
        "improvement_suggestions": ["添加代码示例"]
    })

    with patch.object(engine.client.chat.completions, 'create', return_value=mock_response):
        parsed = ParsedMarkdown(title="Test", raw_content="Content", ...)
        result = engine.analyze(parsed, ["Python"])

    assert result is not None
    assert result.relevance_score == 85
    assert result.depth_score == 75
    assert len(result.improvement_suggestions) == 1
```

#### 测试用例3.2: LLM返回格式错误

**场景**：LLM返回非JSON格式的文本

**期望行为**：重试3次后返回None（不抛出异常）

```python
def test_ai_analysis_json_error():
    config = MarkdownSEOConfig(llm_api_key="test_key", llm_max_retries=3)
    engine = AIEngine(config)

    # Mock返回非JSON
    mock_response = Mock()
    mock_response.choices[0].message.content = "这不是JSON格式"

    with patch.object(engine.client.chat.completions, 'create', return_value=mock_response):
        parsed = ParsedMarkdown(...)
        result = engine.analyze(parsed, ["test"])

    assert result is None  # 应该优雅降级
```

#### 测试用例3.3: 网络超时

**场景**：API调用超时

**期望行为**：重试3次（指数退避），最终返回None

```python
def test_ai_analysis_timeout():
    config = MarkdownSEOConfig(llm_api_key="test_key", llm_max_retries=3)
    engine = AIEngine(config)

    with patch.object(engine.client.chat.completions, 'create', side_effect=TimeoutError):
        result = engine.analyze(ParsedMarkdown(...), ["test"])

    assert result is None
```

#### 测试用例3.4: AI评分计算

**场景**：给定AI分析结果，验证加权评分

**公式**：
```
ai_score = (relevance * 0.4 + depth * 0.3 + readability * 0.3) * 0.25
```

**测试**：
```python
def test_calculate_ai_score():
    engine = AIEngine(config)

    ai_result = AIAnalysisResult(
        relevance_score=80,
        depth_score=60,
        readability_score=90,
        overall_feedback="",
        improvement_suggestions=[]
    )

    score = engine.calculate_ai_score(ai_result)
    expected = (80*0.4 + 60*0.3 + 90*0.3) * 0.25
    assert abs(score - expected) < 0.01
```

### 模块4: MarkdownSEOAnalyzer (`tests/unit/test_analyzer.py`)

**测试目标**：验证模块协调和总分计算。

#### 测试用例4.1: 端到端分析（无AI）

**场景**：禁用AI，纯规则引擎分析

```python
def test_analyze_without_ai():
    config = MarkdownSEOConfig(enable_ai_analysis=False)
    analyzer = MarkdownSEOAnalyzer(config)

    report = analyzer.analyze('tests/fixtures/medium_quality.md')

    # 验证总分 = 规则引擎得分（最多75分）
    assert report.total_score <= 75
    assert report.ai_score == 0
    assert report.ai_analysis is None
```

#### 测试用例4.2: 端到端分析（含AI）

**场景**：启用AI，验证总分 = 规则分 + AI分

```python
def test_analyze_with_ai():
    config = MarkdownSEOConfig(enable_ai_analysis=True, llm_api_key="test_key")
    analyzer = MarkdownSEOAnalyzer(config)

    # Mock AI引擎
    with patch.object(analyzer.ai_engine, 'analyze') as mock_analyze:
        mock_analyze.return_value = AIAnalysisResult(
            relevance_score=80,
            depth_score=70,
            readability_score=85,
            overall_feedback="Good",
            improvement_suggestions=[]
        )

        report = analyzer.analyze('tests/fixtures/good_quality.md')

    # 验证总分包含AI分数
    assert report.total_score > 75  # 规则分 + AI分
    assert report.ai_score > 0
```

#### 测试用例4.3: 自动关键词提取

**场景**：用户未提供关键词，系统自动提取

```python
def test_auto_keyword_extraction():
    analyzer = MarkdownSEOAnalyzer(config)
    report = analyzer.analyze('tests/fixtures/tech_article.md', user_keywords=None)

    # 验证自动提取了关键词
    assert len(report.extracted_keywords) > 0
    assert len(report.user_keywords) == 0
```

#### 测试用例4.4: 用户提供关键词

**场景**：用户提供关键词，不自动提取

```python
def test_user_provided_keywords():
    analyzer = MarkdownSEOAnalyzer(config)
    report = analyzer.analyze('tests/fixtures/tech_article.md', user_keywords=["Python", "SEO"])

    # 验证使用了用户关键词
    assert report.user_keywords == ["Python", "SEO"]
    assert len(report.extracted_keywords) == 0
```

## 集成测试计划

### 集成测试1: 规则引擎 + 解析器

**目标**：验证解析器输出能被规则引擎正确处理

**测试步骤**：
1. 创建Markdown文件 `tests/fixtures/integration_test.md`
2. 使用 `MarkdownParser` 解析
3. 将结果传递给 `RulesEngine`
4. 验证所有诊断项都有合理的分数

```python
def test_parser_rules_integration():
    parser = MarkdownParser()
    config = MarkdownSEOConfig()
    engine = RulesEngine(config)

    parsed = parser.parse('tests/fixtures/integration_test.md')
    score, diagnostics = engine.check_all(parsed, [])

    # 验证每个类别都有诊断项
    categories = {d.category for d in diagnostics}
    assert 'metadata' in categories
    assert 'structure' in categories

    # 验证总分在合理范围内
    assert 0 <= score <= 75
```

### 集成测试2: 配置系统 + 规则引擎

**目标**：验证配置修改能正确影响评分逻辑

**测试步骤**：
1. 创建自定义配置文件（修改标题长度范围）
2. 加载配置并创建规则引擎
3. 验证评分逻辑使用了新配置

```python
def test_config_rules_integration():
    # 自定义配置：标题长度40-80
    custom_config = MarkdownSEOConfig()
    custom_config.title.min_length = 40
    custom_config.title.max_length = 80

    engine = RulesEngine(custom_config)

    # 标题长度45（在新范围内，应该满分）
    parsed = ParsedMarkdown(title="这是一个45字符左右的标题符合新配置的要求", ...)
    score, diags = engine.check_all(parsed, [])

    title_item = next(d for d in diags if d.check_name == "title_length")
    assert title_item.score == 15  # 满分
```

### 集成测试3: 分析器 + 报告生成器

**目标**：验证分析结果能正确转换为Markdown报告

**测试步骤**：
1. 运行完整分析
2. 生成Markdown报告
3. 验证报告包含所有必需section

```python
def test_analyzer_reporter_integration():
    analyzer = MarkdownSEOAnalyzer(config)
    reporter = MarkdownReporter()

    report = analyzer.analyze('tests/fixtures/good_quality.md')
    markdown = reporter.generate(report)

    # 验证报告包含关键信息
    assert "SEO诊断报告" in markdown
    assert "总分" in markdown
    assert "元数据检查" in markdown
    assert "结构检查" in markdown
    assert "诊断详情" in markdown
```

### 集成测试4: CLI + 完整流程

**目标**：验证CLI命令能触发完整分析流程

**测试步骤**：
```python
import subprocess

def test_cli_integration():
    # 运行CLI命令
    result = subprocess.run(
        ['md-audit', 'analyze', 'tests/fixtures/good_quality.md', '-o', 'output.md'],
        capture_output=True,
        text=True
    )

    # 验证命令成功
    assert result.returncode == 0
    assert Path('output.md').exists()

    # 验证输出文件内容
    with open('output.md', 'r') as f:
        content = f.read()
        assert "SEO诊断报告" in content
```

### 集成测试5: 错误处理链路

**目标**：验证各模块的错误处理能协同工作

**场景1**：文件不存在
```python
def test_file_not_found():
    analyzer = MarkdownSEOAnalyzer(config)
    with pytest.raises(FileNotFoundError):
        analyzer.analyze('nonexistent.md')
```

**场景2**：配置文件损坏
```python
def test_corrupted_config():
    # 创建损坏的JSON配置
    with open('bad_config.json', 'w') as f:
        f.write("{invalid json")

    with pytest.raises(json.JSONDecodeError):
        load_config('bad_config.json')
```

**场景3**：LLM失败但分析继续
```python
def test_llm_failure_graceful_degradation():
    analyzer = MarkdownSEOAnalyzer(config)

    # Mock AI引擎失败
    with patch.object(analyzer.ai_engine, 'analyze', return_value=None):
        report = analyzer.analyze('tests/fixtures/good_quality.md')

    # 验证分析继续，但AI分数为0
    assert report.ai_score == 0
    assert report.total_score > 0  # 规则分数仍然有效
```

## 端到端测试（E2E）

### E2E场景1: 高质量文章分析

**目标**：验证工具能正确识别高质量内容

**测试数据**：`tests/fixtures/high_quality_article.md`

**内容特征**：
- 标题长度45字符（合适）
- 描述长度140字符（合适）
- 1个H1标签
- 5张图片，全部有alt
- 3个内部链接
- 关键词密度2%（合理）
- 关键词出现在标题、描述、H1

**期望结果**：
- 总分 >= 85
- 所有关键检查项都是SUCCESS状态
- AI分析结果（如果启用）应该是正面评价

**验证方法**：
```python
def test_e2e_high_quality():
    analyzer = MarkdownSEOAnalyzer(config)
    report = analyzer.analyze('tests/fixtures/high_quality_article.md', user_keywords=["Python", "SEO"])

    # 验证总分
    assert report.total_score >= 85, f"Expected >=85, got {report.total_score}"

    # 验证所有关键项都通过
    critical_items = [d for d in report.diagnostics if d.severity == SeverityLevel.CRITICAL]
    assert len(critical_items) == 0, f"Found critical issues: {critical_items}"

    # 验证AI分析（如果启用）
    if report.ai_analysis:
        assert report.ai_analysis.relevance_score >= 70
```

### E2E场景2: 低质量文章分析

**目标**：验证工具能正确识别SEO问题

**测试数据**：`tests/fixtures/low_quality_article.md`

**内容特征**：
- 无标题（frontmatter和H1都缺失）
- 无描述
- 3个H1标签（过多）
- 5张图片，0个alt
- 无内部链接
- 关键词密度0%（未使用）

**期望结果**：
- 总分 <= 50
- 包含多个CRITICAL严重度的诊断项
- 报告应包含具体改进建议

**验证方法**：
```python
def test_e2e_low_quality():
    analyzer = MarkdownSEOAnalyzer(config)
    report = analyzer.analyze('tests/fixtures/low_quality_article.md')

    # 验证总分
    assert report.total_score <= 50, f"Expected <=50, got {report.total_score}"

    # 验证存在严重问题
    critical_items = [d for d in report.diagnostics if d.severity == SeverityLevel.CRITICAL]
    assert len(critical_items) >= 3, f"Expected >=3 critical issues, got {len(critical_items)}"

    # 验证报告包含改进建议
    items_with_suggestions = [d for d in report.diagnostics if d.suggestion]
    assert len(items_with_suggestions) >= 5
```

### E2E场景3: 真实博客文章

**目标**：在真实数据上验证工具的实用性

**测试数据**：从公开博客（如Medium、Dev.to）下载的真实Markdown文章

**验证方法**：
```python
def test_e2e_real_blog_article():
    analyzer = MarkdownSEOAnalyzer(config)

    # 假设我们有一篇真实的技术博客
    report = analyzer.analyze('tests/fixtures/real_tech_blog.md')

    # 验证分析完成（不崩溃）
    assert report is not None

    # 验证得分在合理范围
    assert 0 <= report.total_score <= 100

    # 验证报告可读
    reporter = MarkdownReporter()
    markdown = reporter.generate(report)
    assert len(markdown) > 100  # 报告不是空的

    # 打印报告供人工审查
    print("\n" + markdown)
```

## 测试数据准备

### 测试Fixture文件清单

在 `tests/fixtures/` 目录下创建以下文件：

#### 1. `high_quality_article.md`
```markdown
---
title: Python Web Scraping完全指南：从入门到实战
description: 本文详细介绍如何使用Python进行网页抓取，涵盖requests、BeautifulSoup、Scrapy等主流工具，并提供5个实战案例帮助你快速掌握爬虫技术。
---

# Python Web Scraping完全指南：从入门到实战

Web scraping（网页抓取）是数据科学和自动化领域的核心技能。本文将带你从零开始掌握Python爬虫。

## 为什么选择Python进行Web Scraping

Python拥有丰富的爬虫库生态，包括requests、BeautifulSoup、Scrapy等...

![Python爬虫架构图](architecture.png)

更多相关文章：
- [Python异步编程指南](./async-guide.md)
- [数据清洗最佳实践](./data-cleaning.md)

（总字数约1000字，包含5张图片均有alt，内部链接3个，关键词"Python"、"Web Scraping"出现8次）
```

#### 2. `low_quality_article.md`
```markdown
这是一篇文章。

# 标题1
# 标题2
# 标题3

![](image1.jpg)
![](image2.jpg)

没有描述，没有关键词，内容很少。
```

#### 3. `medium_quality_article.md`
```markdown
---
title: 技术博客写作指南
description: 如何写好技术博客
---

# 技术博客写作指南

内容适中，有基本结构但缺少细节...

（字数约600字，标题和描述长度边界，部分图片有alt）
```

#### 4. `with_frontmatter.md`（单元测试用）
```markdown
---
title: 测试标题
description: 测试描述
keywords: [Python, SEO]
custom_field: custom_value
---

# 正文内容
```

#### 5. `without_frontmatter.md`（单元测试用）
```markdown
# 仅有H1标题

没有frontmatter的纯Markdown内容。
```

### 配置文件

#### `tests/fixtures/custom_config.json`
```json
{
  "title_rules": {
    "min_length": 40,
    "max_length": 80
  },
  "description_rules": {
    "min_length": 100,
    "max_length": 200
  },
  "keyword_rules": {
    "min_density": 0.02,
    "max_density": 0.04
  }
}
```

## 测试执行

### 本地开发测试

**运行所有测试**：
```bash
cd /mnt/d/VibeCoding_pgm/MD_Audit
pytest tests/ -v
```

**运行特定模块测试**：
```bash
pytest tests/unit/test_parser.py -v
pytest tests/unit/test_rules_engine.py -v
```

**查看覆盖率**：
```bash
pytest tests/ --cov=md_audit --cov-report=html
open htmlcov/index.html
```

**覆盖率目标**：
- 核心模块（Parser, RulesEngine, AIEngine, Analyzer）：>= 85%
- 工具模块（Reporter, Config）：>= 70%
- 总体覆盖率：>= 80%

### CI/CD集成（可选）

**GitHub Actions配置** (`.github/workflows/test.yml`):
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=md_audit
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 回归测试策略

每次代码修改后，必须确保：

### 黄金测试集

创建 `tests/golden/` 目录，存放5篇真实博客文章的快照：

```
tests/golden/
├── article1.md
├── article1_expected_report.md
├── article2.md
├── article2_expected_report.md
...
```

**回归测试流程**：
1. 运行分析：`md-audit analyze tests/golden/article1.md -o report.md`
2. 对比输出：`diff report.md tests/golden/article1_expected_report.md`
3. 如果分数波动超过±5分，需要人工审查原因

**自动化脚本**：
```bash
#!/bin/bash
# tests/regression_test.sh

for article in tests/golden/*.md; do
  if [[ ! "$article" =~ expected ]]; then
    md-audit analyze "$article" -o "${article%.md}_output.md"
    diff "${article%.md}_output.md" "${article%.md}_expected_report.md"
    if [ $? -ne 0 ]; then
      echo "Regression detected in $article"
      exit 1
    fi
  fi
done
```

### 性能基准测试

**目标**：确保工具响应速度不退化

**基准测试**：
```python
import time

def test_performance_benchmark():
    analyzer = MarkdownSEOAnalyzer(config)

    start = time.time()
    report = analyzer.analyze('tests/fixtures/medium_quality_article.md')
    duration = time.time() - start

    # 不含AI：应该在1秒内完成
    assert duration < 1.0, f"Analysis took {duration:.2f}s, expected <1s"
```

**AI调用基准**：
```python
def test_ai_performance_benchmark():
    analyzer = MarkdownSEOAnalyzer(config)

    start = time.time()
    report = analyzer.analyze('tests/fixtures/medium_quality_article.md')
    duration = time.time() - start

    # 含AI：应该在5秒内完成（取决于LLM响应速度）
    assert duration < 5.0, f"Analysis with AI took {duration:.2f}s, expected <5s"
```

## 测试反模式（避免）

### 反模式1: 过度Mock

**错误示例**：
```python
# 不好：Mock了所有依赖，测试变成了Mock的测试
def test_analyzer_bad():
    with patch('md_audit.parsers.MarkdownParser') as mock_parser:
        with patch('md_audit.engines.RulesEngine') as mock_engine:
            with patch('md_audit.engines.AIEngine') as mock_ai:
                analyzer = MarkdownSEOAnalyzer(config)
                # 这个测试什么都没验证
```

**正确做法**：
只Mock外部依赖（如OpenAI API），内部模块使用真实实现。

### 反模式2: 测试实现细节

**错误示例**：
```python
# 不好：测试内部变量名
def test_parser_bad():
    parser = MarkdownParser()
    result = parser.parse('test.md')
    assert hasattr(result, '_internal_cache')  # 耦合实现细节
```

**正确做法**：
测试公开API和行为，不测试私有变量。

### 反模式3: 脆弱的断言

**错误示例**：
```python
# 不好：期望精确的字符串匹配
def test_report_bad():
    markdown = reporter.generate(report)
    assert markdown == "SEO诊断报告\n文件: test.md\n总分: 85.5\n..."  # 太脆弱
```

**正确做法**：
```python
# 好：验证关键信息存在
def test_report_good():
    markdown = reporter.generate(report)
    assert "SEO诊断报告" in markdown
    assert "总分" in markdown
    assert "85.5" in markdown
```

## 测试清单

在提交代码前，确认：

- [ ] 所有单元测试通过（`pytest tests/unit/`）
- [ ] 所有集成测试通过（`pytest tests/integration/`）
- [ ] 至少运行了3个E2E场景（高质量、低质量、真实博客）
- [ ] 代码覆盖率 >= 80%
- [ ] 黄金测试集无回归（分数波动 < ±5）
- [ ] 性能基准测试通过（分析时间 < 1s不含AI，< 5s含AI）
- [ ] 手动运行CLI命令验证用户体验
- [ ] 生成的Markdown报告人类可读

## 测试文档维护

### 何时更新测试

- **新增功能**：添加对应的单元测试和集成测试
- **修复Bug**：先写重现Bug的测试，再修复（TDD）
- **修改评分逻辑**：更新测试矩阵和期望分数
- **更新配置**：验证新配置能正确影响评分

### 测试代码审查清单

- [ ] 测试名称清晰描述测试场景（`test_title_scoring_when_too_short`）
- [ ] 每个测试只验证一个行为（单一职责）
- [ ] 使用 `pytest.mark.parametrize` 减少重复代码
- [ ] 失败时提供有意义的错误信息（`assert score == 15, f"Expected 15, got {score}"`）
- [ ] 清理测试数据（使用 `pytest fixtures` 和 `tmpdir`）

## 总结

这个测试计划不是为了追求100%覆盖率，而是确保：

1. **规则引擎准确**：每个评分逻辑都有对应的测试矩阵
2. **错误处理健壮**：LLM失败、文件缺失、配置错误都能优雅处理
3. **真实场景可用**：在真实博客文章上验证工具的实用性

测试的核心是验证这个工具能否帮助用户改进SEO质量，而不是堆砌用例数量。每个测试都应该回答一个真实的问题："这个工具在这个场景下会给出正确的建议吗？"
