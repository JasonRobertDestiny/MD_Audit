# 分析服务（封装现有analyzer）
from pathlib import Path
from functools import lru_cache
import logging
from md_audit.analyzer import MarkdownSEOAnalyzer
from md_audit.config import MarkdownSEOConfig

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_analyzer():
    """
    获取单例analyzer实例（复用，避免重复初始化）

    Returns:
        MarkdownSEOAnalyzer实例
    """
    config = MarkdownSEOConfig()
    return MarkdownSEOAnalyzer(config)


class AnalyzerService:
    """分析服务（100%复用现有analyzer逻辑）"""

    def __init__(self):
        self.analyzer = get_analyzer()

    def analyze_file(self, file_path: str, keywords: list[str] = None):
        """
        分析单个文件

        Args:
            file_path: 文件路径
            keywords: 用户关键词（可选）

        Returns:
            SEOReport对象
        """
        return self.analyzer.analyze(file_path, user_keywords=keywords or [])

    def analyze_content(self, content: str, keywords: list[str] = None):
        """
        分析文本内容（不保存文件）

        Args:
            content: Markdown内容
            keywords: 用户关键词（可选）

        Returns:
            SEOReport对象
        """
        # 创建临时文件
        temp_file = Path("/tmp/md_audit_temp.md")
        temp_file.write_text(content, encoding="utf-8")

        try:
            return self.analyze_file(str(temp_file), keywords)
        finally:
            # 清理临时文件（添加异常处理，避免清理失败导致500错误）
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError as e:
                logger.warning(f"临时文件清理失败（{temp_file}）: {e}")
