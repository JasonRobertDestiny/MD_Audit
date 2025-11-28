"""
AI引擎单元测试 - 验证LLM集成和降级机制
"""
import pytest
from unittest.mock import Mock, patch
from md_audit.engines.ai_engine import AIEngine
from md_audit.config import MarkdownSEOConfig
from md_audit.models.data_models import ParsedMarkdown, AIAnalysisResult


class TestAIEngine:
    """测试AI引擎"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return MarkdownSEOConfig(
            llm_api_key="test-key",
            llm_model="gpt-4o",
            llm_timeout=30,
            llm_max_retries=3,
            enable_ai_analysis=True
        )

    @pytest.fixture
    def sample_parsed(self):
        """示例解析结果"""
        return ParsedMarkdown(
            title="Python Web Scraping Tutorial",
            description="Learn web scraping with Python" * 10,
            raw_content="Content about Python web scraping" * 20,
            h1_tags=["Python Web Scraping Tutorial"],
            word_count=100
        )

    def test_ai_disabled(self, config):
        """测试禁用AI分析"""
        config.enable_ai_analysis = False
        engine = AIEngine(config)

        parsed = ParsedMarkdown(
            title="Test",
            description="Test" * 20,
            raw_content="test content"
        )

        result = engine.analyze(parsed, ["test"])
        assert result is None

    @patch('md_audit.engines.ai_engine.OpenAI')
    def test_successful_analysis(self, mock_openai, config, sample_parsed):
        """测试成功的AI分析"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "relevance_score": 85,
            "depth_score": 75,
            "readability_score": 90,
            "overall_feedback": "Good content quality",
            "improvement_suggestions": ["Add more examples", "Include code snippets"]
        }
        """
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        engine = AIEngine(config)
        result = engine.analyze(sample_parsed, ["Python", "Web Scraping"])

        assert result is not None
        assert isinstance(result, AIAnalysisResult)
        assert 0 <= result.relevance_score <= 100
        assert 0 <= result.depth_score <= 100
        assert 0 <= result.readability_score <= 100
        assert len(result.improvement_suggestions) > 0

    @patch('md_audit.engines.ai_engine.OpenAI')
    def test_api_failure_returns_none(self, mock_openai, config, sample_parsed):
        """测试API失败时返回None"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        engine = AIEngine(config)
        result = engine.analyze(sample_parsed, ["test"])

        # 应该降级返回None而不是崩溃
        assert result is None

    @patch('md_audit.engines.ai_engine.OpenAI')
    def test_invalid_json_response(self, mock_openai, config, sample_parsed):
        """测试无效JSON响应"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        engine = AIEngine(config)
        result = engine.analyze(sample_parsed, ["test"])

        # 无效JSON应该降级
        assert result is None

    def test_calculate_ai_score_valid_result(self, config):
        """测试计算AI分数"""
        engine = AIEngine(config)

        ai_result = AIAnalysisResult(
            relevance_score=80.0,
            depth_score=70.0,
            readability_score=90.0,
            overall_feedback="Good",
            improvement_suggestions=["Test"]
        )

        score = engine.calculate_ai_score(ai_result)

        # 应该在0-25分范围内
        assert 0 <= score <= 25
        # 验证加权计算：80*0.4 + 70*0.3 + 90*0.3 = 80
        # 转换为25分制：80 * 0.25 = 20
        expected = (80.0 * 0.4 + 70.0 * 0.3 + 90.0 * 0.3) * 0.25
        assert abs(score - expected) < 0.01

    def test_calculate_ai_score_none_result(self, config):
        """测试计算AI分数 - None输入"""
        engine = AIEngine(config)
        score = engine.calculate_ai_score(None)
        assert score == 0.0

    def test_missing_api_key(self, monkeypatch):
        """测试缺少API密钥"""
        # 清除环境变量避免.env文件干扰
        monkeypatch.delenv("MD_AUDIT_LLM_API_KEY", raising=False)

        config = MarkdownSEOConfig(
            llm_api_key="",
            enable_ai_analysis=True
        )
        # 强制清空（绕过__post_init__）
        config.llm_api_key = ""

        # 缺少API密钥应该在初始化时抛出异常
        with pytest.raises(ValueError, match="LLM API Key未设置"):
            engine = AIEngine(config)


# 运行测试：pytest tests/unit/test_ai_engine.py -v
