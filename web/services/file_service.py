# 文件处理服务
import re
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile


class FileService:
    """文件上传和校验服务"""

    ALLOWED_EXTENSIONS = {".md", ".txt", ".markdown"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MALICIOUS_PATTERNS = [
        r"<script[^>]*>",  # JavaScript脚本
        r"javascript:",  # JavaScript协议
        r"on\w+\s*=",  # 事件处理器
    ]

    def __init__(self, temp_dir: Path = None):
        self.temp_dir = temp_dir or Path("/tmp/md_audit_uploads")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Path:
        """
        保存上传文件到临时目录

        Args:
            file: FastAPI上传文件对象

        Returns:
            临时文件路径

        Raises:
            ValueError: 文件校验失败
        """
        # 1. 扩展名白名单检查
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式：{file_ext}")

        # 2. 读取并检查文件大小
        content = await file.read()
        if len(content) == 0:
            raise ValueError("文件为空（0字节）")

        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"文件超过10MB限制（{len(content) / 1024 / 1024:.1f}MB）"
            )

        # 3. 恶意代码检测
        try:
            text = content.decode("utf-8", errors="ignore")
            for pattern in self.MALICIOUS_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    raise ValueError("文件包含潜在恶意代码")
        except UnicodeDecodeError:
            raise ValueError("文件编码无效（请使用UTF-8）")

        # 4. 文件名路径穿越防护
        safe_filename = Path(file.filename).name  # 仅保留文件名部分
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            raise ValueError("非法文件名")

        # 5. 保存到临时目录（时间戳前缀避免冲突）
        timestamp = int(datetime.now().timestamp() * 1000)
        temp_file = self.temp_dir / f"{timestamp}_{safe_filename}"
        temp_file.write_bytes(content)

        return temp_file

    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        清理超过指定时间的临时文件

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        for file in self.temp_dir.iterdir():
            if file.is_file() and file.stat().st_mtime < cutoff:
                file.unlink()
