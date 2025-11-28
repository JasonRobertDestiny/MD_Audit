from typing import List, Tuple
from md_audit.models.data_models import ParsedMarkdown, DiagnosticItem, SeverityLevel
from md_audit.config import MarkdownSEOConfig


class RulesEngine:
    """规则检查引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config

    def check_all(self, parsed: ParsedMarkdown, keywords: List[str]) -> Tuple[float, List[DiagnosticItem]]:
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
