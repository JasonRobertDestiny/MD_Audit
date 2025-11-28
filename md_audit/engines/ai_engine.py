import os
import time
import json
from typing import Optional
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, APIConnectionError
from md_audit.models.data_models import AIAnalysisResult, ParsedMarkdown
from md_audit.config import MarkdownSEOConfig


class AIEngine:
    """AI语义分析引擎"""

    def __init__(self, config: MarkdownSEOConfig):
        self.config = config

        if not config.llm_api_key:
            raise ValueError("LLM API Key未设置，请通过环境变量MD_AUDIT_LLM_API_KEY提供")

        self.client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            timeout=config.llm_timeout
        )

    def analyze(self, parsed: ParsedMarkdown, keywords: list[str]) -> Optional[AIAnalysisResult]:
        """
        AI语义分析（内容相关性、深度、可读性）

        Args:
            parsed: 解析后的Markdown数据
            keywords: 关键词列表

        Returns:
            AI分析结果，失败时返回None
        """
        if not self.config.enable_ai_analysis:
            return None

        # 构造prompt
        keyword_str = "、".join(keywords) if keywords else "未提供"
        prompt = f"""
你是一个SEO专家，请分析以下Markdown文章的质量。

**文章标题**：{parsed.title}
**文章描述**：{parsed.description}
**目标关键词**：{keyword_str}
**字数**：{parsed.word_count}

**文章内容**（前1000字）：
{parsed.raw_content[:1000]}

请从以下三个维度评分（0-100分）：

1. **内容相关性（relevance_score）**：文章内容与目标关键词的匹配度
2. **内容深度（depth_score）**：内容是否深入、是否提供实用价值
3. **可读性（readability_score）**：结构是否清晰、语言是否流畅

同时提供：
- **overall_feedback**：50字以内的综合评价
- **improvement_suggestions**：2-3条具体改进建议

**输出格式**（JSON）：
{{
  "relevance_score": 85,
  "depth_score": 75,
  "readability_score": 90,
  "overall_feedback": "文章与关键词相关性强，但缺乏实战案例",
  "improvement_suggestions": [
    "添加更多代码示例",
    "增加实际应用场景"
  ]
}}
"""

        # 重试机制
        for attempt in range(self.config.llm_max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的SEO分析专家，擅长评估内容质量。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # 低温度保证输出稳定
                    response_format={"type": "json_object"}  # 强制JSON输出
                )

                # 解析响应
                result_text = response.choices[0].message.content
                result_data = json.loads(result_text)

                # 验证并返回
                return AIAnalysisResult(
                    relevance_score=float(result_data.get('relevance_score', 0)),
                    depth_score=float(result_data.get('depth_score', 0)),
                    readability_score=float(result_data.get('readability_score', 0)),
                    overall_feedback=result_data.get('overall_feedback', ''),
                    improvement_suggestions=result_data.get('improvement_suggestions', [])
                )

            except json.JSONDecodeError as e:
                print(f"[警告] AI返回结果解析失败（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                continue

            except RateLimitError as e:
                print(f"[警告] API限流（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(5 * (2 ** attempt))  # 限流时更长等待
                continue

            except APITimeoutError as e:
                print(f"[警告] API超时（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except APIConnectionError as e:
                print(f"[警告] API连接失败（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except APIError as e:
                print(f"[警告] API错误（尝试 {attempt+1}/{self.config.llm_max_retries}）：{e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except Exception as e:
                print(f"[错误] 未知异常（尝试 {attempt+1}/{self.config.llm_max_retries}）：{type(e).__name__}: {e}")
                if attempt < self.config.llm_max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

        # 所有重试都失败
        print("[错误] AI分析失败，已达到最大重试次数，将跳过AI评分")
        return None

    def calculate_ai_score(self, ai_result: Optional[AIAnalysisResult]) -> float:
        """
        计算AI语义得分（满分25分）

        Args:
            ai_result: AI分析结果

        Returns:
            AI得分（0-25）
        """
        if not ai_result:
            return 0.0

        # 加权平均：相关性40% + 深度30% + 可读性30%
        weighted_score = (
            ai_result.relevance_score * 0.4 +
            ai_result.depth_score * 0.3 +
            ai_result.readability_score * 0.3
        )

        # 转换为25分制
        return weighted_score * 0.25
