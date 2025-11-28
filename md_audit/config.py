import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv不是必需依赖


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
    max_density: float = 0.025  # 最大密度2.5%
    max_auto_keywords: int = 5  # 自动提取关键词数量
    weight: float = 20.0


@dataclass
class ContentRules:
    """内容结构规则配置"""
    min_length: int = 300     # 最小字数
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
        """初始化默认子配置和环境变量覆盖"""
        if self.title is None:
            self.title = TitleRules()
        if self.description is None:
            self.description = DescriptionRules()
        if self.keywords is None:
            self.keywords = KeywordRules()
        if self.content is None:
            self.content = ContentRules()

        # 环境变量覆盖（支持直接实例化时的配置）
        if os.getenv('MD_AUDIT_LLM_API_KEY'):
            self.llm_api_key = os.getenv('MD_AUDIT_LLM_API_KEY')
        if os.getenv('MD_AUDIT_LLM_BASE_URL'):
            self.llm_base_url = os.getenv('MD_AUDIT_LLM_BASE_URL')
        if os.getenv('MD_AUDIT_LLM_MODEL'):
            self.llm_model = os.getenv('MD_AUDIT_LLM_MODEL')
        if os.getenv('MD_AUDIT_ENABLE_AI'):
            self.enable_ai_analysis = os.getenv('MD_AUDIT_ENABLE_AI', '').lower() in ('true', '1', 'yes')

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
        if os.getenv('MD_AUDIT_LLM_BASE_URL'):
            config.llm_base_url = os.getenv('MD_AUDIT_LLM_BASE_URL')
        if os.getenv('MD_AUDIT_LLM_MODEL'):
            config.llm_model = os.getenv('MD_AUDIT_LLM_MODEL')
        if os.getenv('MD_AUDIT_ENABLE_AI'):
            config.enable_ai_analysis = os.getenv('MD_AUDIT_ENABLE_AI', '').lower() in ('true', '1', 'yes')

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
