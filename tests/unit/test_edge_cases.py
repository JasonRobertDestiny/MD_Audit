"""
边缘情况单元测试 - 验证异常处理和边界条件
"""
import pytest
import tempfile
import os
from pathlib import Path
from md_audit.parsers.markdown_parser import MarkdownParser
from md_audit.engines.rules_engine import RulesEngine
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.config import MarkdownSEOConfig
from md_audit.models.data_models import ParsedMarkdown


class TestEdgeCases:
    """测试边缘情况和错误处理"""

    def test_empty_markdown_file(self):
        """测试空Markdown文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)

            # 应该能解析但内容为空
            assert result.title == ""
            assert result.description == ""
            assert result.word_count == 0
            assert len(result.h1_tags) == 0
        finally:
            os.unlink(temp_path)

    def test_markdown_without_frontmatter(self):
        """测试没有frontmatter的Markdown"""
        content = """
# Test Title

This is a test content without frontmatter.

## Section 1

Some content here.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)

            # 应该能解析，title从第一个H1提取，description为空
            assert result.title == "Test Title"
            assert result.description == ""
            assert len(result.h1_tags) > 0
            assert result.word_count > 0
        finally:
            os.unlink(temp_path)

    def test_malformed_frontmatter(self):
        """测试格式错误的frontmatter"""
        content = """---
title: Test
description: This is broken
  invalid yaml
---

# Content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = MarkdownParser()
            # 应该能容错处理
            result = parser.parse(temp_path)
            # 可能无法解析frontmatter，但不应崩溃
            assert result is not None
        finally:
            os.unlink(temp_path)

    def test_nonexistent_file(self):
        """测试不存在的文件"""
        parser = MarkdownParser()

        with pytest.raises(Exception):
            parser.parse("/nonexistent/path/to/file.md")

    def test_very_long_title(self):
        """测试超长标题"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        long_title = "A" * 200  # 200字符标题

        parsed = ParsedMarkdown(
            title=long_title,
            description="Test description" * 10,
            raw_content="test"
        )

        score, diagnostics = engine.check_all(parsed, [])

        # 应该检测到标题过长
        title_item = next((d for d in diagnostics if "title" in d.check_name), None)
        assert title_item is not None
        assert title_item.score < 15.0  # 不应该得满分

    def test_unicode_content(self):
        """测试Unicode内容（中文、emoji等）"""
        content = """---
title: 测试标题🎉
description: 这是一个包含中文和emoji的描述，用于测试Unicode处理能力。
---

# 测试标题🎉

这是中文内容，包含emoji 😀 和各种特殊字符：™️ © ®

## 第二部分

更多中文内容测试。
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)

            # 应该正确处理Unicode
            assert "测试标题" in result.title
            assert "中文" in result.description
            assert result.word_count > 0
        finally:
            os.unlink(temp_path)

    def test_empty_keyword_list(self):
        """测试空关键词列表"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        parsed = ParsedMarkdown(
            title="Test Title",
            description="Test description" * 10,
            raw_content="test content" * 20
        )

        # 传入空关键词列表
        score, diagnostics = engine.check_all(parsed, [])

        # 应该能正常执行，关键词检查返回0分
        keyword_items = [d for d in diagnostics if "keyword" in d.check_name]
        assert len(keyword_items) > 0

    def test_special_characters_in_content(self):
        """测试特殊字符内容"""
        parser = MarkdownParser()
        text = "Test <script>alert('xss')</script> content & special chars"

        # 应该能处理HTML标签和特殊字符
        keywords = parser.extract_keywords(text, max_keywords=5)

        # 不应该提取HTML标签作为关键词
        assert not any('<' in kw or '>' in kw for kw in keywords)

    def test_very_short_content(self, monkeypatch):
        """测试极短内容"""
        # 清除环境变量避免.env文件干扰
        monkeypatch.delenv("MD_AUDIT_LLM_API_KEY", raising=False)
        monkeypatch.delenv("MD_AUDIT_ENABLE_AI", raising=False)

        config = MarkdownSEOConfig(enable_ai_analysis=False)
        # 强制禁用AI（绕过__post_init__）
        config.enable_ai_analysis = False
        config.llm_api_key = ""
        analyzer = MarkdownSEOAnalyzer(config)

        content = """---
title: Hi
description: Test
---

# Hi

OK
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            report = analyzer.analyze(temp_path)

            # 应该能分析，但得分很低
            assert report.total_score < 50
            # 应该检测到内容过短
            assert any("过短" in d.message or "不足" in d.message for d in report.diagnostics)
        finally:
            os.unlink(temp_path)

    def test_multiple_h1_tags(self):
        """测试多个H1标签"""
        content = """---
title: Test
description: Test description for SEO analysis
---

# First H1

Content here.

# Second H1

More content.

# Third H1

Even more content.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)

            # 应该检测到多个H1
            assert len(result.h1_tags) == 3
        finally:
            os.unlink(temp_path)

    def test_images_without_alt(self):
        """测试无alt属性的图片"""
        content = """---
title: Test Images
description: Testing images without alt attributes
---

# Images Test

![](image1.jpg)
![](image2.jpg)
![Alt text](image3.jpg)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)

            # 应该检测到3张图片
            assert len(result.images) == 3

            # 检查alt覆盖率
            images_with_alt = sum(1 for img in result.images if img.get('alt'))
            assert images_with_alt == 1  # 只有image3有alt
        finally:
            os.unlink(temp_path)

    def test_keyword_extraction_from_short_text(self):
        """测试从短文本提取关键词"""
        parser = MarkdownParser()

        # 测试只有3个词的文本
        text = "Python SEO optimization"
        keywords = parser.extract_keywords(text, max_keywords=5)

        # 应该能提取，即使文本很短
        assert len(keywords) <= 5
        assert len(keywords) > 0

    def test_keyword_extraction_all_stopwords(self):
        """测试全是停用词的文本"""
        parser = MarkdownParser()

        # 全是英文停用词
        text = "the a an and or but is are was were"
        keywords = parser.extract_keywords(text, max_keywords=5)

        # 应该返回空列表或过滤后的结果
        assert isinstance(keywords, list)
        # 不应该包含停用词
        assert not any(kw.lower() in ['the', 'and', 'or', 'but'] for kw in keywords)

    def test_invalid_config_path(self):
        """测试无效配置文件路径"""
        from md_audit.config import load_config

        # 传入不存在的配置路径应该降级到默认配置
        config = load_config("/nonexistent/config.json")

        # 应该返回默认配置
        assert config is not None
        assert config.title.min_length == 30

    def test_zero_length_description(self):
        """测试零长度描述"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        parsed = ParsedMarkdown(
            title="Test Title",
            description="",
            raw_content="test content"
        )

        score, diagnostics = engine.check_all(parsed, ["test"])

        # 应该检测到缺少描述
        desc_item = next((d for d in diagnostics if "description" in d.check_name), None)
        assert desc_item is not None
        assert desc_item.score == 0


class TestConcurrentAnalysis:
    """测试并发分析场景"""

    def test_analyze_multiple_files_sequentially(self, monkeypatch):
        """测试顺序分析多个文件"""
        # 清除环境变量避免.env文件干扰
        monkeypatch.delenv("MD_AUDIT_LLM_API_KEY", raising=False)
        monkeypatch.delenv("MD_AUDIT_ENABLE_AI", raising=False)

        config = MarkdownSEOConfig(enable_ai_analysis=False)
        # 强制禁用AI
        config.enable_ai_analysis = False
        config.llm_api_key = ""
        analyzer = MarkdownSEOAnalyzer(config)

        # 使用现有测试fixture
        files = [
            'tests/fixtures/high_quality.md',
            'tests/fixtures/medium_quality.md',
            'tests/fixtures/low_quality.md'
        ]

        reports = []
        for file_path in files:
            if os.path.exists(file_path):
                report = analyzer.analyze(file_path)
                reports.append(report)

        # 应该能成功分析所有文件
        assert len(reports) > 0
        # 每个报告应该有不同的分数
        scores = [r.total_score for r in reports]
        assert len(set(scores)) > 1  # 至少有不同的分数


# 运行测试：pytest tests/unit/test_edge_cases.py -v
