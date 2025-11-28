"""
基础单元测试 - 验证核心功能
"""
import pytest
from md_audit.parsers.markdown_parser import MarkdownParser
from md_audit.engines.rules_engine import RulesEngine
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.config import MarkdownSEOConfig, load_config
from md_audit.models.data_models import ParsedMarkdown, SeverityLevel


class TestMarkdownParser:
    """测试Markdown解析器"""

    def test_parse_with_frontmatter(self):
        """测试解析包含frontmatter的Markdown"""
        parser = MarkdownParser()
        result = parser.parse('tests/fixtures/high_quality.md')

        assert result.title != ""
        assert result.description != ""
        assert len(result.h1_tags) > 0
        assert result.word_count > 0

    def test_keyword_extraction(self):
        """测试关键词提取"""
        parser = MarkdownParser()
        text = "Python web scraping tutorial for beginners Python Python"
        keywords = parser.extract_keywords(text, max_keywords=3)

        assert len(keywords) > 0
        # 验证不包含低质量关键词
        assert not any('http://' in kw.lower() for kw in keywords)

    def test_quality_keyword_filtering(self):
        """测试关键词质量过滤"""
        parser = MarkdownParser()

        # 应该拒绝URL
        assert not parser._is_quality_keyword("https://example.com")

        # 应该拒绝HTML标签
        assert not parser._is_quality_keyword("<div>")

        # 应该拒绝停用词
        assert not parser._is_quality_keyword("the")

        # 应该接受正常关键词
        assert parser._is_quality_keyword("Python SEO")


class TestRulesEngine:
    """测试规则引擎"""

    def test_title_length_scoring(self):
        """测试标题长度评分"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        # 测试合适长度的标题（30-60字符）
        # 使用英文以确保准确的字符计数
        parsed = ParsedMarkdown(
            title="This is a Good Title for SEO Testing Purpose",  # 46字符
            description="测试描述" * 20,
            raw_content="test content"
        )
        score, diagnostics = engine.check_all(parsed, [])

        title_item = next((d for d in diagnostics if d.check_name == "title_length"), None)
        assert title_item is not None
        assert title_item.score == 15.0
        assert title_item.severity == SeverityLevel.SUCCESS

    def test_missing_title(self):
        """测试缺失标题的情况"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        parsed = ParsedMarkdown(
            title="",
            description="测试描述" * 20,
            raw_content="test content"
        )
        score, diagnostics = engine.check_all(parsed, [])

        title_item = next((d for d in diagnostics if "title" in d.check_name), None)
        assert title_item is not None
        assert title_item.severity == SeverityLevel.CRITICAL
        assert title_item.score == 0

    def test_h1_count_check(self):
        """测试H1标签数量检查"""
        config = MarkdownSEOConfig()
        engine = RulesEngine(config)

        # 测试唯一H1
        parsed = ParsedMarkdown(
            title="Test",
            description="Test" * 20,
            h1_tags=["Main Title"],
            raw_content="test"
        )
        score, diagnostics = engine.check_all(parsed, [])

        h1_item = next((d for d in diagnostics if d.check_name == "h1_count"), None)
        assert h1_item is not None
        assert h1_item.score == 5.0
        assert h1_item.severity == SeverityLevel.SUCCESS


class TestConfig:
    """测试配置系统"""

    def test_load_default_config(self):
        """测试加载默认配置"""
        config = load_config()

        assert config is not None
        assert config.title.min_length == 30
        assert config.title.max_length == 60
        assert config.description.min_length == 120

    def test_config_from_json(self):
        """测试从JSON加载配置"""
        config = MarkdownSEOConfig.from_json('config/default_config.json')

        assert config.llm_model == "gpt-4o"
        assert config.llm_timeout == 30
        assert config.llm_max_retries == 3


class TestAnalyzer:
    """测试分析器"""

    def test_analyze_without_ai(self, monkeypatch):
        """测试不使用AI的分析"""
        # 清除环境变量避免.env文件干扰
        monkeypatch.delenv("MD_AUDIT_LLM_API_KEY", raising=False)
        monkeypatch.delenv("MD_AUDIT_ENABLE_AI", raising=False)

        config = MarkdownSEOConfig(enable_ai_analysis=False)
        # 强制禁用AI（绕过__post_init__）
        config.enable_ai_analysis = False
        config.llm_api_key = ""
        analyzer = MarkdownSEOAnalyzer(config)

        report = analyzer.analyze('tests/fixtures/medium_quality.md')

        # 验证总分在合理范围内
        assert 0 <= report.total_score <= 75  # 不含AI最多75分
        assert report.ai_score == 0
        assert report.ai_analysis is None

        # 验证诊断项存在
        assert len(report.diagnostics) > 0

    def test_high_quality_scoring(self):
        """测试高质量文件评分"""
        config = MarkdownSEOConfig(enable_ai_analysis=False)
        analyzer = MarkdownSEOAnalyzer(config)

        report = analyzer.analyze('tests/fixtures/high_quality.md')

        # 高质量文件应该得到较高分数
        assert report.total_score >= 50  # 至少及格分

        # 验证报告结构
        assert report.file_path == 'tests/fixtures/high_quality.md'
        assert report.metadata_score >= 0
        assert report.structure_score >= 0

    def test_low_quality_scoring(self):
        """测试低质量文件评分"""
        config = MarkdownSEOConfig(enable_ai_analysis=False)
        analyzer = MarkdownSEOAnalyzer(config)

        report = analyzer.analyze('tests/fixtures/low_quality.md')

        # 低质量文件应该得到较低分数
        assert report.total_score < 50

        # 验证有critical问题
        critical_issues = [d for d in report.diagnostics if d.severity == SeverityLevel.CRITICAL]
        assert len(critical_issues) > 0


# 运行测试：pytest tests/unit/test_basic.py -v
