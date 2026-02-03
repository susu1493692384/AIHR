# agents/base.py
"""Agent基类定义"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.language_models import BaseChatModel


class BaseAgent(ABC):
    """Agent抽象基类"""

    def __init__(
        self,
        llm: BaseChatModel,
        tools: list = None,
        verbose: bool = False
    ):
        """
        初始化Agent

        Args:
            llm: 语言模型
            tools: 工具列表（预留）
            verbose: 是否输出详细信息
        """
        self.llm = llm
        self.tools = tools or []
        self.verbose = verbose

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        获取系统Prompt

        Returns:
            系统Prompt字符串
        """
        pass

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务

        Args:
            input_data: 输入数据

        Returns:
            执行结果
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            是否有效
        """
        return input_data is not None and isinstance(input_data, dict)

    def format_output(self, result: Any) -> Dict[str, Any]:
        """
        格式化输出结果

        Args:
            result: 原始结果

        Returns:
            格式化后的结果
        """
        if isinstance(result, dict):
            return result
        return {"result": str(result)}

    async def invoke_llm(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Any:
        """
        调用LLM的辅助方法

        Args:
            system_prompt: 系统Prompt
            user_prompt: 用户Prompt

        Returns:
            LLM响应
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        return await self.llm.ainvoke(messages)

    def parse_json_response(self, response: Any, raise_on_error: bool = False) -> Any:
        """
        解析LLM的JSON响应

        Args:
            response: LLM响应对象
            raise_on_error: 解析失败时是否抛出异常

        Returns:
            解析后的JSON对象，失败时返回None或抛出异常
        """
        from utils.json_parser import extract_json, clean_json_string

        # 获取响应文本
        response_text = response.content if hasattr(response, 'content') else str(response)

        print(f"[DEBUG] base.py - 准备解析JSON，响应长度: {len(response_text)}")

        # 清理和解析
        cleaned_text = clean_json_string(response_text)
        result = extract_json(cleaned_text)

        if result is None and raise_on_error:
            # 提供更详细的错误信息
            error_details = []
            error_details.append(f"响应长度: {len(response_text)} 字符")
            error_details.append(f"响应前200字符:\n{response_text[:200]}")
            error_details.append(f"响应后200字符:\n{response_text[-200:]}")

            # 检查是否包含JSON标记
            if '{' in response_text:
                first_brace = response_text.index('{')
                error_details.append(f"第一个 {{ 位置: {first_brace}")
                error_details.append(f"从 {{ 开始的内容:\n{response_text[first_brace:first_brace+300]}")
            else:
                error_details.append("响应中未找到 '{' 字符")

            error_msg = "无法从LLM响应中提取JSON\n" + "\n".join(error_details)
            print(f"[DEBUG] base.py - JSON解析失败:\n{error_msg}")
            raise ValueError(error_msg)

        print(f"[DEBUG] base.py - JSON解析成功")
        return result
