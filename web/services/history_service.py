# 历史记录服务
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class HistoryService:
    """历史记录管理服务（JSON文件存储）"""

    def __init__(self, history_file: Path = None):
        self.history_file = history_file or (Path.home() / ".md-audit/history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # 初始化历史文件
        if not self.history_file.exists():
            self._save_history({})

    def save_report(self, report: dict, file_name: str) -> str:
        """
        保存诊断报告到历史记录

        Args:
            report: SEOReport字典（Pydantic序列化后）
            file_name: 原始文件名

        Returns:
            记录ID
        """
        # 生成唯一ID（时间戳 + 哈希）
        timestamp = datetime.now()
        record_id = f"{timestamp.strftime('%Y%m%d%H%M%S')}_{hash(file_name)}"

        # 加载现有历史
        history = self._load_history()

        # 计算严重程度统计
        severity_counts = {"error": 0, "warning": 0, "success": 0}
        for diag in report.get("diagnostics", []):
            severity = diag.get("severity", "success")
            if severity in severity_counts:
                severity_counts[severity] += 1

        # 添加新记录
        history[record_id] = {
            "id": record_id,
            "timestamp": timestamp.isoformat(),
            "file_name": file_name,
            "total_score": report.get("total_score", 0),
            "severity_counts": severity_counts,
            "report": report,  # 保存完整报告
        }

        # 保存（最多保留100条）
        self._save_history(dict(list(history.items())[-100:]))

        return record_id

    def get_history_list(
        self,
        page: int = 1,
        page_size: int = 20,
        severity_filter: str = "all"
    ) -> dict:
        """
        获取历史记录列表（分页）

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            severity_filter: 严重程度筛选（all/error/warning）

        Returns:
            包含items、total、page、page_size的字典
        """
        history = self._load_history()

        # 筛选
        items = []
        for record in history.values():
            if severity_filter != "all":
                if record["severity_counts"].get(severity_filter, 0) == 0:
                    continue
            items.append(record)

        # 排序（时间倒序）
        items.sort(key=lambda x: x["timestamp"], reverse=True)

        # 分页
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        items_page = items[start:end]

        # 移除完整报告（列表不需要）
        for item in items_page:
            item.pop("report", None)

        return {
            "items": items_page,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_report(self, record_id: str) -> Optional[dict]:
        """
        获取单个历史记录的完整报告

        Args:
            record_id: 记录ID

        Returns:
            完整报告字典（包含report字段）

        Raises:
            ValueError: 记录不存在
        """
        history = self._load_history()

        if record_id not in history:
            raise ValueError(f"历史记录不存在：{record_id}")

        return history[record_id]

    def _load_history(self) -> dict:
        """加载历史记录"""
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_history(self, history: dict):
        """保存历史记录"""
        self.history_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
