# tools/cleaning/date_normalizer.py
"""日期标准化工具"""
import re
from datetime import datetime
from typing import Optional


class DateNormalizer:
    """日期标准化工具类"""

    # 日期格式模式
    PATTERNS = {
        # 标准格式 YYYY-MM
        "standard": r"^(\d{4})-(0?[1-9]|1[0-2])$",
        # 中文格式 YYYY年MM月
        "chinese": r"^(\d{4})年(\d{1,2})月$",
        # 点分隔格式 YYYY.MM
        "dot": r"^(\d{4})\.(\d{1,2})$",
        # 斜杠分隔格式 YYYY/MM
        "slash": r"^(\d{4})/(\d{1,2})$",
    }

    # "至今"相关关键词
    PRESENT_KEYWORDS = ["至今", "Present", "present", "当前", "在职"]

    @staticmethod
    def normalize(date_str: str) -> Optional[str]:
        """
        标准化日期格式为 YYYY-MM

        Args:
            date_str: 原始日期字符串

        Returns:
            str: 标准化后的日期 (YYYY-MM)，或 "至今"，或 None
        """
        if not date_str or not date_str.strip():
            return None

        date_str = date_str.strip()

        # 检查是否为"至今"等关键词
        if date_str in DateNormalizer.PRESENT_KEYWORDS:
            return "至今"

        # 尝试匹配各种格式
        # 1. 标准格式 YYYY-MM
        match = re.match(DateNormalizer.PATTERNS["standard"], date_str)
        if match:
            year, month = match.groups()
            return f"{year}-{month.zfill(2)}"

        # 2. 中文格式 YYYY年MM月
        match = re.match(DateNormalizer.PATTERNS["chinese"], date_str)
        if match:
            year, month = match.groups()
            return f"{year}-{month.zfill(2)}"

        # 3. 点分隔格式 YYYY.MM
        match = re.match(DateNormalizer.PATTERNS["dot"], date_str)
        if match:
            year, month = match.groups()
            return f"{year}-{month.zfill(2)}"

        # 4. 斜杠分隔格式 YYYY/MM
        match = re.match(DateNormalizer.PATTERNS["slash"], date_str)
        if match:
            year, month = match.groups()
            return f"{year}-{month.zfill(2)}"

        # 无法识别的格式
        return None

    @staticmethod
    def calculate_duration(start_date: str, end_date: str) -> Optional[str]:
        """
        计算两个日期之间的时长

        Args:
            start_date: 开始日期 (YYYY-MM 或 "至今")
            end_date: 结束日期 (YYYY-MM 或 "至今")

        Returns:
            str: 时长描述 (如 "2年", "6个月")，或 None
        """
        if not start_date or not end_date:
            return None

        if end_date == "至今":
            # 使用当前日期计算
            end_date = datetime.now().strftime("%Y-%m")

        if start_date == "至今":
            return None

        try:
            # 解析日期
            start_parts = start_date.split("-")
            end_parts = end_date.split("-")

            start_year = int(start_parts[0])
            start_month = int(start_parts[1])
            end_year = int(end_parts[0])
            end_month = int(end_parts[1])

            # 计算月数差
            total_months = (end_year - start_year) * 12 + (end_month - start_month)

            if total_months < 0:
                return None

            # 格式化输出
            if total_months >= 12:
                years = total_months // 12
                remaining_months = total_months % 12
                if remaining_months > 0:
                    return f"{years}年{remaining_months}个月"
                return f"{years}年"
            else:
                return f"{total_months}个月"

        except (ValueError, IndexError):
            return None

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """
        验证日期是否有效

        Args:
            date_str: 日期字符串

        Returns:
            bool: 是否有效
        """
        if not date_str:
            return False

        if date_str == "至今":
            return True

        normalized = DateNormalizer.normalize(date_str)
        if not normalized:
            return False

        # 验证日期是否合理
        try:
            parts = normalized.split("-")
            year = int(parts[0])
            month = int(parts[1])

            # 年份在 1900-2100 之间
            if not 1900 <= year <= 2100:
                return False

            # 月份在 1-12 之间
            if not 1 <= month <= 12:
                return False

            return True
        except (ValueError, IndexError):
            return False
