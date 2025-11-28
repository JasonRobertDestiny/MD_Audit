"""
报告生成器单元测试 - 验证Markdown报告格式
"""
import pytest
from md_audit.reporter import MarkdownReporter
from md_audit.models.data_models import (
    SEOReport, DiagnosticItem, AIAnalysisResult, SeverityLevel
)


class TestMarkdownReporter:
    """测试Markdown报告生成器"""

    def test_generate_complete_report(self):
        """测试生成完整报告（含AI分析）"""
        reporter = MarkdownReporter()

        report = SEOReport(
            file_path="tests/fixtures/test.md",
            total_score=85.5,
            metadata_score=28.0,
            structure_score=22.0,
            keyword_score=18.0,
            ai_score=17.5,
            diagnostics=[
                DiagnosticItem(
                    category="metadata",  # 使用实际的category值
                    check_name="title_length",
                    severity=SeverityLevel.SUCCESS,
                    score=15.0,
                    message="标题长度合适（42字符）",
                    suggestion="",
                    current_value="42",
                    expected_value="30-60"
                ),
                DiagnosticItem(
                    category="structure",  # 使用实际的category值
                    check_name="h1_count",
                    severity=SeverityLevel.WARNING,
                    score=2.5,
                    message="H1标签过多（3个）",
                    suggestion="每个页面应该有且仅有1个H1标签",
                    current_value="3",
                    expected_value="1"
                )
            ],
            ai_analysis=AIAnalysisResult(
                relevance_score=85.0,
                depth_score=70.0,
                readability_score=90.0,
                overall_feedback="内容质量良好",
                improvement_suggestions=["添加更多示例", "补充代码片段"]
            ),
            extracted_keywords=["Python", "SEO", "优化"],
            user_keywords=["Python", "Web"]
        )

        markdown = reporter.generate(report)

        # 验证报告结构
        assert "# SEO诊断报告" in markdown
        assert "tests/fixtures/test.md" in markdown
        assert "85.5/100" in markdown

        # 验证评分详情
        assert "元数据" in markdown
        assert "28.0/30" in markdown

        # 验证emoji严重程度标记 - 总分85.5应该是🟢
        assert "🟢" in markdown

        # 验证关键词显示
        assert "Python" in markdown
        assert "SEO" in markdown

        # 验证AI分析部分
        assert "AI语义分析" in markdown
        assert "内容质量良好" in markdown
        assert "添加更多示例" in markdown

    def test_generate_report_without_ai(self):
        """测试生成无AI分析的报告"""
        reporter = MarkdownReporter()

        report = SEOReport(
            file_path="tests/fixtures/test.md",
            total_score=60.0,
            metadata_score=20.0,
            structure_score=20.0,
            keyword_score=20.0,
            ai_score=0.0,
            diagnostics=[
                DiagnosticItem(
                    category="元数据检查",
                    check_name="title_length",
                    severity=SeverityLevel.SUCCESS,
                    score=15.0,
                    message="标题长度合适",
                    suggestion="",
                    current_value="45",
                    expected_value="30-60"
                )
            ],
            ai_analysis=None,
            extracted_keywords=["test"],
            user_keywords=[]
        )

        markdown = reporter.generate(report)

        # 验证基本结构
        assert "# SEO诊断报告" in markdown
        assert "60.0/100" in markdown

        # 验证没有AI分析部分
        assert "AI语义分析" not in markdown

    def test_severity_emoji_mapping(self):
        """测试严重程度emoji映射"""
        reporter = MarkdownReporter()

        test_cases = [
            (SeverityLevel.CRITICAL, "🔴"),
            (SeverityLevel.WARNING, "🟠"),
            (SeverityLevel.INFO, "🟡"),
            (SeverityLevel.SUCCESS, "🟢")
        ]

        for severity, expected_emoji in test_cases:
            report = SEOReport(
                file_path="test.md",
                total_score=50.0,
                diagnostics=[
                    DiagnosticItem(
                        category="metadata",  # 必须是有效的category
                        check_name="test_check",
                        severity=severity,
                        score=10.0,
                        message="测试消息",
                        suggestion="测试建议"
                    )
                ],
                ai_analysis=None,
                extracted_keywords=[],
                user_keywords=[]
            )

            markdown = reporter.generate(report)
            # emoji应该出现在诊断项中
            assert expected_emoji in markdown

    def test_score_status_indicator(self):
        """测试分数状态指示器"""
        reporter = MarkdownReporter()

        # 测试优秀评分（≥80）- 根据emoji_badge属性
        report_excellent = SEOReport(
            file_path="test.md",
            total_score=90.0,
            diagnostics=[],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )
        markdown = reporter.generate(report_excellent)
        assert "🟢" in markdown  # 90分应该是绿色

        # 测试良好评分（60-79）
        report_good = SEOReport(
            file_path="test.md",
            total_score=70.0,
            diagnostics=[],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )
        markdown = reporter.generate(report_good)
        assert "🟡" in markdown  # 70分应该是黄色

        # 测试需改进评分（40-59）
        report_fair = SEOReport(
            file_path="test.md",
            total_score=50.0,
            diagnostics=[],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )
        markdown = reporter.generate(report_fair)
        assert "🟠" in markdown  # 50分应该是橙色

        # 测试较差评分（<40）
        report_poor = SEOReport(
            file_path="test.md",
            total_score=30.0,
            diagnostics=[],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )
        markdown = reporter.generate(report_poor)
        assert "🔴" in markdown  # 30分应该是红色

    def test_diagnostic_grouping_by_category(self):
        """测试诊断项按类别分组"""
        reporter = MarkdownReporter()

        report = SEOReport(
            file_path="test.md",
            total_score=50.0,
            diagnostics=[
                DiagnosticItem(
                    category="metadata",  # 使用实际的category值
                    check_name="title_length",
                    severity=SeverityLevel.SUCCESS,
                    score=15.0,
                    message="标题长度合适",
                    suggestion=""
                ),
                DiagnosticItem(
                    category="metadata",
                    check_name="description_length",
                    severity=SeverityLevel.WARNING,
                    score=10.0,
                    message="描述过短",
                    suggestion="建议描述在120-160字符之间"
                ),
                DiagnosticItem(
                    category="structure",  # 使用实际的category值
                    check_name="h1_count",
                    severity=SeverityLevel.SUCCESS,
                    score=5.0,
                    message="H1标签数量正确",
                    suggestion=""
                )
            ],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )

        markdown = reporter.generate(report)

        # 验证类别标题存在
        assert "### 元数据检查" in markdown
        assert "### 结构检查" in markdown

        # 验证同一类别的项在一起
        metadata_pos = markdown.find("### 元数据检查")
        structure_pos = markdown.find("### 结构检查")
        title_pos = markdown.find("title_length")
        desc_pos = markdown.find("description_length")
        h1_pos = markdown.find("h1_count")

        # 元数据检查的两项应该在结构检查之前
        assert metadata_pos < structure_pos
        assert metadata_pos < title_pos < structure_pos
        assert metadata_pos < desc_pos < structure_pos
        assert structure_pos < h1_pos

    def test_empty_diagnostics(self):
        """测试无诊断项的报告"""
        reporter = MarkdownReporter()

        report = SEOReport(
            file_path="test.md",
            total_score=100.0,
            diagnostics=[],
            ai_analysis=None,
            extracted_keywords=[],
            user_keywords=[]
        )

        markdown = reporter.generate(report)

        # 应该仍能生成有效报告
        assert "# SEO诊断报告" in markdown
        assert "100.0/100" in markdown


# 运行测试：pytest tests/unit/test_reporter.py -v
