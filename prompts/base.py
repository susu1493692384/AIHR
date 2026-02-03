# prompts/base.py
"""Prompt模板基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class BasePrompt(ABC):
    """Prompt模板基类"""

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        pass

    @abstractmethod
    def get_user_prompt(self) -> str:
        """获取用户Prompt"""
        pass

    def to_chat_prompt(self) -> ChatPromptTemplate:
        """
        转换为ChatPromptTemplate

        Returns:
            ChatPromptTemplate实例
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", self.get_user_prompt())
        ])

    def format(self, **kwargs) -> str:
        """
        格式化Prompt

        Args:
            **kwargs: 格式化参数

        Returns:
            格式化后的Prompt字符串
        """
        return self.get_system_prompt() + "\n\n" + self.get_user_prompt().format(**kwargs)


class PromptTemplate:
    """Prompt模板工具类"""

    @staticmethod
    def create_few_shot_prompt(
        system_prompt: str,
        examples: list[Dict[str, str]],
        input_template: str = "Input: {input}\nOutput: {output}"
    ) -> str:
        """
        创建Few-Shot Prompt

        Args:
            system_prompt: 系统Prompt
            examples: 示例列表
            input_template: 输入模板

        Returns:
            Few-Shot Prompt字符串
        """
        examples_text = "\n\n".join([
            input_template.format(**example)
            for example in examples
        ])

        return f"{system_prompt}\n\n以下是几个示例:\n\n{examples_text}"

    @staticmethod
    def create_cot_prompt(
        task_description: str,
        steps: list[str]
    ) -> str:
        """
        创建思维链(CoT) Prompt

        Args:
            task_description: 任务描述
            steps: 思维步骤

        Returns:
            CoT Prompt字符串
        """
        steps_text = "\n".join([
            f"{i+1}. {step}"
            for i, step in enumerate(steps)
        ])

        return f"""任务: {task_description}

请按以下步骤思考:
{steps_text}

请逐步推理并给出最终答案。"""

    @staticmethod
    def create_structured_prompt(
        role: str,
        task: str,
        constraints: list[str] = None,
        output_format: str = None
    ) -> str:
        """
        创建结构化Prompt

        Args:
            role: 角色
            task: 任务
            constraints: 约束条件列表
            output_format: 输出格式说明

        Returns:
            结构化Prompt字符串
        """
        prompt_parts = [
            f"# 角色\n{role}",
            f"\n# 任务\n{task}"
        ]

        if constraints:
            constraints_text = "\n".join([
                f"- {c}"
                for c in constraints
            ])
            prompt_parts.append(f"\n# 约束条件\n{constraints_text}")

        if output_format:
            prompt_parts.append(f"\n# 输出格式\n{output_format}")

        return "\n".join(prompt_parts)
