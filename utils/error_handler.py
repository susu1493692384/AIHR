# utils/error_handler.py
"""统一错误处理器"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ResumeAnalyzerError(Exception):
    """简历分析器基础异常"""
    pass


class FileParseError(ResumeAnalyzerError):
    """文件解析异常"""
    pass


class DataValidationError(ResumeAnalyzerError):
    """数据验证异常"""
    pass


class LLMError(ResumeAnalyzerError):
    """LLM调用异常"""
    pass


class ScoringError(ResumeAnalyzerError):
    """评分异常"""
    pass


class ErrorHandler:
    """错误处理器"""

    ERROR_MAPPING = {
        FileNotFoundError: ("文件不存在", "文件未找到"),
        ValueError: ("数据格式错误", "输入数据格式不正确"),
        KeyError: ("缺少必需字段", "数据中缺少必需的字段"),
        TypeError: ("类型错误", "数据类型不匹配"),
    }

    @classmethod
    def handle_error(
        cls,
        error: Exception,
        context: str = ""
    ) -> Dict[str, Any]:
        """统一处理错误"""
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)

        error_type = type(error)
        error_info = cls.ERROR_MAPPING.get(
            error_type,
            ("未知错误", str(error))
        )

        return {
            "error_type": error_type.__name__,
            "error_message": str(error),
            "user_message": error_info[0],
            "detail_message": error_info[1],
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
