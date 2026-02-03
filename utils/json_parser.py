# utils/json_parser.py
"""JSON解析工具 - 从LLM响应中提取JSON"""
import json
import re
from typing import Any, Optional


def extract_json(text: str) -> Optional[Any]:
    """
    从LLM响应中提取JSON数据

    Args:
        text: LLM返回的文本

    Returns:
        解析后的JSON对象，如果失败返回None
    """
    if not text:
        return None

    # 1. 尝试直接解析整个文本
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 2. 尝试提取markdown代码块中的JSON
    markdown_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    markdown_matches = re.findall(markdown_pattern, text, re.DOTALL | re.IGNORECASE)
    for match in markdown_matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # 3. 尝试提取 {...} 格式的JSON对象
    # 使用更智能的方法匹配最外层的 { }
    brace_count = 0
    start_idx = -1

    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                # 找到完整的对象
                json_str = text[start_idx:i+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

    # 4. 尝试提取数组 [...]
    bracket_count = 0
    start_idx = -1

    for i, char in enumerate(text):
        if char == '[':
            if bracket_count == 0:
                start_idx = i
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0 and start_idx != -1:
                # 找到完整的数组
                json_str = text[start_idx:i+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

    # 5. 最后尝试：使用宽松的正则表达式匹配
    # 查找可能的JSON对象
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    json_matches = re.findall(json_pattern, text, re.DOTALL)
    for match in json_matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # 所有尝试都失败
    return None


def clean_json_string(text: str) -> str:
    """
    清理JSON字符串中的常见问题

    Args:
        text: 原始文本

    Returns:
        清理后的JSON字符串
    """
    # 移除BOM标记
    text = text.replace('\ufeff', '')

    # 移除控制字符（保留换行和制表符）
    text = ''.join(char for char in text if char == '\n' or char == '\t' or ord(char) >= 32)

    # 修复JSON字符串中的未转义换行符
    # 问题：LLM可能返回 {"field": "第一行\n第二行"} 而不是 {"field": "第一行\\n第二行"}
    # 解决方案：使用状态机遍历文本，识别字符串内容并转义

    result = []
    in_string = False
    escape_next = False
    string_start = 0

    for i, char in enumerate(text):
        if escape_next:
            # 当前字符是转义序列的一部分，直接保留
            result.append(char)
            escape_next = False
        elif char == '\\' and in_string:
            # 在字符串中遇到反斜杠，下一个字符需要转义
            result.append(char)
            escape_next = True
        elif char == '"' and not in_string:
            # 字符串开始
            in_string = True
            string_start = i
            result.append(char)
        elif char == '"' and in_string:
            # 字符串结束
            in_string = False
            result.append(char)
        elif in_string:
            # 在字符串内部，检查是否需要转义
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            elif char == '\b':
                result.append('\\b')
            elif char == '\f':
                result.append('\\f')
            elif char == '\\' and not escape_next:
                result.append('\\\\')
            else:
                result.append(char)
        else:
            # 在JSON结构中，直接保留
            result.append(char)

    text = ''.join(result)

    return text.strip()
