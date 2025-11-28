import re
from typing import List, Dict
from pathlib import Path
from collections import Counter
import frontmatter
import markdown
from bs4 import BeautifulSoup
from md_audit.models.data_models import ParsedMarkdown

# 中文分词支持
try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False


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
        '这', '那', '你', '我', '他', '她', '它', 'this', 'that', 'it', 'will',
        'can', 'have', 'has', 'had', 'if', 'when', 'where', 'which', 'who',
    }

    def __init__(self):
        self.md_parser = markdown.Markdown(extensions=['extra', 'codehilite', 'tables'])

    def parse(self, file_path: str) -> ParsedMarkdown:
        """
        解析Markdown文件

        Args:
            file_path: Markdown文件路径

        Returns:
            解析后的结构化数据

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码错误
            PermissionError: 无文件读取权限
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {file_path}")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"文件编码错误（需要UTF-8编码）: {file_path}"
            )
        except PermissionError:
            raise PermissionError(f"无权限读取文件: {file_path}")

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

        # 重置解析器状态以避免状态污染
        self.md_parser.reset()

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

        支持中英文混合文本，中文使用jieba分词

        Args:
            content: 文本内容
            max_keywords: 返回关键词数量

        Returns:
            关键词列表（按词频降序）
        """
        # 清理文本
        text = self._clean_text(content)

        # 分词（中文用jieba，英文用空格）
        words = self._tokenize(text)

        # 计算n-gram词频
        keyword_freq: Dict[str, int] = {}

        # Unigrams（单词）
        for word in words:
            if self._is_quality_keyword(word):
                keyword_freq[word] = keyword_freq.get(word, 0) + 1

        # Bigrams（双词组合）
        for i in range(len(words) - 1):
            bigram = f"{words[i]}{words[i+1]}"
            if self._is_quality_keyword(bigram):
                keyword_freq[bigram] = keyword_freq.get(bigram, 0) + 1

        # 按词频排序
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:max_keywords]]

    def _tokenize(self, text: str) -> List[str]:
        """
        分词：中文用jieba，英文用空格分割
        """
        if HAS_JIEBA:
            # 使用jieba分词（精确模式）
            words = list(jieba.cut(text, cut_all=False))
            # 过滤空白和标点
            return [w.strip() for w in words if w.strip() and len(w.strip()) > 1]
        else:
            # 降级：简单按空格和标点分割
            return [w for w in re.split(r'[\s\u3000]+', text) if w and len(w) > 1]

    def _clean_text(self, text: str) -> str:
        """清理文本（移除代码块、HTML标签、Markdown语法等）"""
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        # 移除Markdown图片语法 ![alt](url "title")
        text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
        # 移除Markdown链接语法 [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除Markdown标题标记
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 移除frontmatter分隔符
        text = re.sub(r'^---[\s\S]*?---', '', text)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除特殊字符但保留中文和字母
        text = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', text)
        # 标准化空白符
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _is_quality_keyword(self, keyword: str) -> bool:
        """
        判断关键词质量（参考analyzer.py:16-94）

        拒绝：URL片段、HTML/CSS代码、纯数字、停用词、过短/过长
        """
        keyword = keyword.strip().lower()

        # 长度检查（关键词不应过长，限制20字符）
        if len(keyword) < 2 or len(keyword) > 20:
            return False

        # 词数检查（最多3个词组成的短语）
        word_count = len(keyword.split())
        if word_count > 3:
            return False

        # 停用词检查（单词完全匹配或短语中大部分是停用词）
        words = keyword.split()
        stopword_count = sum(1 for w in words if w in self.STOP_WORDS)
        if word_count == 1 and keyword in self.STOP_WORDS:
            return False
        if word_count > 1 and stopword_count > word_count // 2:
            return False

        # 模式匹配检查
        for pattern in self.LOW_QUALITY_PATTERNS:
            if re.search(pattern, keyword):
                return False

        return True
