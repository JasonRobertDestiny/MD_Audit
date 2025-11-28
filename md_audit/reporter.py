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
        lines.append(f"**总分**: {report.total_score:.1f}/100 {report.emoji_badge}\n")

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
