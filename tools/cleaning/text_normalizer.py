# tools/cleaning/text_normalizer.py
"""文本标准化工具"""
import re
from typing import Optional


class TextNormalizer:
    """文本标准化工具类"""

    @staticmethod
    def normalize(text: Optional[str], remove_special: bool = False) -> str:
        """
        标准化文本内容

        Args:
            text: 原始文本
            remove_special: 是否移除特殊字符

        Returns:
            str: 标准化后的文本
        """
        if text is None:
            return ""

        if not isinstance(text, str):
            return str(text)

        # 移除首尾空白
        text = text.strip()

        # 标准化换行符
        text = TextNormalizer._normalize_newlines(text)

        # 移除多余空格
        text = TextNormalizer._remove_extra_spaces(text)

        # 移除特殊字符（可选）
        if remove_special:
            text = TextNormalizer._remove_special_characters(text)

        return text

    @staticmethod
    def _normalize_newlines(text: str) -> str:
        """标准化换行符为 \\n"""
        # 将 \r\n 和 \r 替换为 \n
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # 移除连续的空行
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    @staticmethod
    def _remove_extra_spaces(text: str) -> str:
        """移除多余的空格"""
        # 将多个连续空格替换为单个空格
        text = re.sub(r" +", " ", text)

        # 移除制表符
        text = text.replace("\t", " ")

        return text

    @staticmethod
    def _remove_special_characters(text: str) -> str:
        """移除特殊字符，保留中文、英文、数字和常用标点"""
        # 保留：中文字符、英文字符、数字、空格、常用标点
        pattern = r"[^\u4e00-\u9fa5a-zA-Z0-9\s\.,;:!?()（）\[\]【】、。，；：！？]"
        text = re.sub(pattern, "", text)

        return text

    @staticmethod
    def clean_phone(phone: str) -> Optional[str]:
        """
        清理手机号码

        Args:
            phone: 原始手机号

        Returns:
            str: 清理后的11位手机号，或 None
        """
        if not phone:
            return None

        # 移除所有非数字字符
        phone_digits = re.sub(r"\D", "", phone)

        # 验证是否为11位且以1开头
        if len(phone_digits) == 11 and phone_digits.startswith("1"):
            return phone_digits

        return None

    @staticmethod
    def clean_email(email: str) -> Optional[str]:
        """
        清理邮箱地址

        Args:
            email: 原始邮箱

        Returns:
            str: 清理后的邮箱（小写），或 None
        """
        if not email:
            return None

        email = email.strip().lower()

        # 简单验证邮箱格式
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_pattern, email):
            return email

        return None

    @staticmethod
    def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
        """
        截断过长的文本

        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 截断后添加的后缀

        Returns:
            str: 截断后的文本
        """
        if not text:
            return ""

        if len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix
