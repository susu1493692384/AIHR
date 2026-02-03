# agents/parsing_agent.py
"""简历解析Agent"""
from typing import Dict, Any, Optional
from agents.base import BaseAgent
from prompts import prompt_manager
from langchain_core.tools import Tool
from langchain_core.language_models import BaseChatModel


class ParsingAgent(BaseAgent):
    """简历解析Agent - 负责解析简历文件并提取结构化信息"""

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化解析Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("parsing")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行简历解析任务

        Args:
            input_data: 输入数据，包含：
                - file_path: 简历文件路径（可选）
                - file_content: 文件内容（可选）
                - text: 简历文本（可选）
                - parse_type: 解析类型 ("file" | "text")

        Returns:
            解析结果，包含：
                - success: 是否成功
                - parsed_data: 解析出的结构化数据
                - raw_text: 原始文本（如果有）
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            # 获取简历文本
            resume_text = input_data.get("text") or input_data.get("file_content")

            if not resume_text and input_data.get("file_path"):
                # 如果提供了文件路径，使用工具解析
                file_path = input_data["file_path"]
                parse_result = self.parse_file(file_path)

                if not parse_result.get("success"):
                    return {
                        "success": False,
                        "error": parse_result.get("error", "Failed to parse file"),
                        "agent_name": "ParsingAgent"
                    }

                resume_text = parse_result.get("content")

            if not resume_text:
                print(f"[FILE] 错误: 没有简历文本或文件")
                return {
                    "success": False,
                    "error": "No resume text or file provided"
                }

            print(f"[FILE] 简历文本提取成功，长度: {len(resume_text)} 字符")
            print(f"[FILE] 简历文本前100字符: {resume_text[:100]}")

            try:
                # 构造Prompt
                user_prompt = prompt_manager.get_user_prompt("parsing")
                print(f"[FILE] 获取user_prompt成功，类型: {type(user_prompt)}")

                # 截断简历文本以避免超过token限制（glm-4-flash最大输出8k tokens）
                # 保留前4000字符，确保JSON能完整输出
                max_resume_length = 4000
                truncated_resume = resume_text[:max_resume_length]
                if len(resume_text) > max_resume_length:
                    if self.verbose:
                        print(f"[WARNING] 简历文本过长({len(resume_text)}字符)，截断至{max_resume_length}字符")
                    truncated_resume += "\n\n[注：简历文本已截断，仅保留前4000字符以确保完整解析]"

                # 直接使用字符串替换，不使用format()
                # 避免format()解析简历文本中的花括号导致的KeyError
                formatted_prompt = user_prompt.replace('{resume_text}', truncated_resume)
                print(f"[FILE] 格式化prompt成功，长度: {len(formatted_prompt)}")
            except Exception as prompt_error:
                import traceback
                error_msg = f"Prompt构造失败: {type(prompt_error).__name__}: {str(prompt_error)}\n详细错误:\n{traceback.format_exc()}"
                print(f"[FILE] {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "agent_name": "ParsingAgent"
                }

            # 检查API Key配置
            import os
            api_key = os.getenv("ZHIPU_API_KEY")
            if not api_key:
                print(f"[FILE] 错误: ZHIPU_API_KEY环境变量未配置")
                return {
                    "success": False,
                    "error": "ZHIPU_API_KEY环境变量未配置，请在侧边栏输入API Key"
                }
            # 安全地显示API Key前4位
            try:
                api_key_prefix = str(api_key)[:4] if api_key else "None"
                print(f"[FILE] API Key已配置（前4位: {api_key_prefix}****）")
            except Exception as e:
                print(f"[FILE] API Key类型异常: {type(api_key)}, 值: {repr(api_key)}")
                return {
                    "success": False,
                    "error": f"ZHIPU_API_KEY配置异常: {type(api_key)}"
                }

            # 调用LLM
            try:
                print(f"[FILE] 开始调用LLM API...")
                print(f"[FILE] System prompt长度: {len(self.get_system_prompt())}")
                print(f"[FILE] User prompt长度: {len(formatted_prompt)}")

                response = await self.llm.ainvoke([
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": formatted_prompt}
                ])
                print(f"[FILE] LLM API调用成功，响应类型: {type(response)}")
                print(f"[FILE] 响应对象属性: {dir(response)[:10]}")  # 只显示前10个属性
            except Exception as llm_error:
                import traceback
                error_msg = f"LLM API调用失败: {type(llm_error).__name__}: {str(llm_error)}\n"
                error_msg += f"可能的原因：\n1. API Key配置错误或已过期\n2. API配额不足\n3. 网络连接问题\n4. 请求过于频繁\n\n详细错误:\n{traceback.format_exc()}"
                print(f"[FILE] {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "agent_name": "ParsingAgent"
                }

            # 获取响应内容
            response_text = None
            if hasattr(response, 'content'):
                response_text = response.content
                print(f"[FILE] 从response.content获取响应内容")
            elif isinstance(response, dict) and 'content' in response:
                response_text = response['content']
                print(f"[FILE] 从字典content键获取响应内容")
            elif isinstance(response, str):
                response_text = response
                print(f"[FILE] 响应本身是字符串")
            else:
                response_text = str(response)
                print(f"[FILE] 通过str()转换获取响应内容")

            print(f"[FILE] 响应文本长度: {len(response_text) if response_text else 0} 字符")
            print(f"[FILE] 响应前150字符: {response_text[:150] if response_text else 'None'}")

            # 快速检查：响应是否明显不完整
            if response_text and len(response_text) < 100:
                error_msg = f"LLM响应异常短（{len(response_text)}字符），可能是API调用失败\n"
                error_msg += f"响应内容: {repr(response_text)}\n"
                error_msg += f"可能原因：\n1. API Key配置错误或已过期\n2. API配额不足\n3. 网络连接问题\n4. 请求过于频繁触发限流"
                print(f"[FILE] 错误: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "agent_name": "ParsingAgent"
                }

            # 解析响应（使用改进的JSON解析器）
            parsed_data = self.parse_json_response(response, raise_on_error=True)

            return {
                "success": True,
                "parsed_data": parsed_data,
                "raw_text": resume_text,
                "agent_name": "ParsingAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "ParsingAgent"
            }

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件（同步版本）

        Args:
            file_path: 文件路径

        Returns:
            解析结果
        """
        # 导入文件解析工具
        from tools.parsing.file_parser import FileParserTool

        parser = FileParserTool()
        try:
            file_content = parser.parse(file_path)
            return {
                "success": True,
                "content": file_content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def extract_structure(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取结构化数据

        Args:
            parsed_data: 解析出的原始数据

        Returns:
            标准化的结构化数据
        """
        # 使用结构映射Prompt进行二次处理
        structure_prompt = prompt_manager.get("structure_mapping")

        if not structure_prompt:
            return parsed_data

        # 这里可以添加额外的结构映射逻辑
        # 目前直接返回解析数据
        return parsed_data


class StructureMappingAgent(BaseAgent):
    """结构映射Agent - 将解析结果映射到标准数据模型"""

    def __init__(
        self,
        llm: BaseChatModel,
        verbose: bool = False
    ):
        """
        初始化结构映射Agent

        Args:
            llm: 语言模型
            verbose: 是否输出详细信息
        """
        super().__init__(llm, verbose=verbose)

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt("structure_mapping")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行结构映射任务（使用规则映射，不调用LLM）

        Args:
            input_data: 输入数据，包含：
                - parsed_data: 解析出的原始数据

        Returns:
            映射结果，包含：
                - success: 是否成功
                - mapped_data: 映射后的标准数据
                - error: 错误信息（如果失败）
        """
        if not self.validate_input(input_data):
            return {
                "success": False,
                "error": "Invalid input data"
            }

        try:
            parsed_data = input_data.get("parsed_data")

            if not parsed_data:
                return {
                    "success": False,
                    "error": "No parsed data provided"
                }

            # 使用规则映射，不调用LLM
            mapped_data = self._apply_field_mapping(parsed_data)

            return {
                "success": True,
                "mapped_data": mapped_data,
                "agent_name": "StructureMappingAgent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": "StructureMappingAgent"
            }

    def _apply_field_mapping(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用字段映射规则（将中文/不规则字段名映射到标准字段名）

        Args:
            parsed_data: 解析出的原始数据

        Returns:
            映射后的标准数据
        """
        from tools.parsing import StructureMapperTool

        # 使用增强的结构映射工具
        normalized_data = StructureMapperTool.normalize_parsed_data(parsed_data)

        return normalized_data
