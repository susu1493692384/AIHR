# utils/validation.py
"""数据验证器"""
import os
from utils.error_handler import DataValidationError, ScoringError


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """验证文件路径"""
        if not file_path:
            raise DataValidationError("文件路径为空")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        return True

    @staticmethod
    def validate_file_type(file_path: str, allowed_types: list) -> bool:
        """验证文件类型"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_types:
            raise DataValidationError(
                f"不支持的文件类型: {ext}，"
                f"支持的类型: {', '.join(allowed_types)}"
            )
        return True

    @staticmethod
    def validate_score(score: float, dimension: str) -> bool:
        """验证分数有效性"""
        if not isinstance(score, (int, float)):
            raise ScoringError(f"{dimension}分数必须是数字")
        if not 0 <= score <= 100:
            raise ScoringError(f"{dimension}分数必须在0-100之间")
        return True
