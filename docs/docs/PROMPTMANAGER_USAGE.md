# PromptManager 使用指南

**创建时间**: 2026-01-28
**目的**: 详细说明 PromptManager 的使用方式和完整调用链

---

## 📋 目录

1. [PromptManager 是什么](#what)
2. [如何初始化](#init)
3. [在Agent中的使用方式](#usage)
4. [完整调用示例](#example)
5. [使用流程图](#flow)

---

## 1️⃣ PromptManager 是什么 {#what}

`PromptManager` 是一个**全局单例**，负责统一管理系统中所有的Prompt模板。

### 定义位置

**文件**: [prompts/__init__.py](prompts/__init__.py#L33-L201)

```python
class PromptManager:
    """Prompt模板管理器"""

    def __init__(self):
        """初始化Prompt管理器"""
        self._prompts: Dict[str, BasePrompt] = {}
        self._register_default_prompts()  # 自动注册14个Prompt

    def _register_default_prompts(self):
        """注册默认的Prompt模板"""
        # 解析相关 (2个)
        self.register("parsing", ParsingPrompts())
        self.register("structure_mapping", StructureMappingPrompt())

        # 清洗相关 (2个)
        self.register("cleaning", CleaningPrompts())
        self.register("deduplication", DeduplicationPrompt())

        # 分析相关 (4个) ⭐
        self.register("technical_analysis", TechnicalAnalysisPrompt())
        self.register("experience_analysis", ExperienceAnalysisPrompt())
        self.register("project_analysis", ProjectAnalysisPrompt())
        self.register("soft_skill_analysis", SoftSkillAnalysisPrompt())

        # 优化相关 (2个)
        self.register("optimization", OptimizationPrompts())
        self.register("priority_optimization", PriorityOptimizationPrompt())

        # 报告相关 (4个)
        self.register("report_generation", ReportGenerationPrompt())
        self.register("hr_summary", HRSummaryPrompt())
        self.register("candidate_summary", CandidateSummaryPrompt())
        self.register("score_explanation", ScoreExplanationPrompt())

# 全局单例
prompt_manager = PromptManager()
```

---

## 2️⃣ 如何初始化 {#init}

### 自动初始化（推荐）

```python
# 在任何地方导入即可使用，无需手动创建实例
from prompts import prompt_manager

# prompt_manager 已经是初始化好的全局单例
# 包含14个已注册的Prompt模板
```

### 查看已注册的Prompt

```python
from prompts import prompt_manager

# 列出所有Prompt名称
prompts = prompt_manager.list_prompts()
print(prompts)
# 输出: ['parsing', 'structure_mapping', 'cleaning', 'deduplication',
#        'technical_analysis', 'experience_analysis', 'project_analysis',
#        'soft_skill_analysis', 'optimization', 'priority_optimization',
#        'report_generation', 'hr_summary', 'candidate_summary', 'score_explanation']
```

---

## 3️⃣ 在Agent中的使用方式 {#usage}

### 使用模式

所有Agent都遵循相同的使用模式：

```python
from agents.base import BaseAgent
from prompts import prompt_manager

class MyAgent(BaseAgent):

    # 模式1: 通过name获取Prompt
    def get_system_prompt(self, analysis_type: str) -> str:
        """获取系统Prompt"""
        return prompt_manager.get_system_prompt(f"{analysis_type}_analysis")

    # 模式2: 在方法中使用
    async def _analyze(self, data: dict) -> dict:
        # 步骤1: 获取Prompt模板
        user_prompt_template = prompt_manager.get_user_prompt("my_analysis")

        # 步骤2: 格式化Prompt（填充数据）
        formatted_prompt = user_prompt_template.format(
            data=json.dumps(data, ensure_ascii=False),
            param2="value"
        )

        # 步骤3: 调用LLM
        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ])

        # 步骤4: 解析结果
        return json.loads(response.content)
```

---

## 4️⃣ 完整调用示例 {#example}

### 示例1: AnalysisAgent 技术分析

**文件**: [agents/analysis_agent.py](agents/analysis_agent.py#L138-L165)

```python
from agents.base import BaseAgent
from prompts import prompt_manager
import json

class AnalysisAgent(BaseAgent):

    async def _analyze_technical(
        self,
        resume_data: Dict[str, Any],
        job_requirements: str
    ) -> Dict[str, Any]:
        """分析技术能力"""

        # ========================================
        # 步骤1: 从PromptManager获取User Prompt模板
        # ========================================
        user_prompt_template = prompt_manager.get_user_prompt("technical_analysis")

        # user_prompt_template 的内容:
        # """
        # 请分析以下简历的技术能力：
        #
        # {resume_data}
        #
        # 目标岗位要求：
        # {job_requirements}
        #
        # 请以JSON格式输出分析结果。
        # """

        # ========================================
        # 步骤2: 格式化Prompt，填充实际数据
        # ========================================
        formatted_prompt = user_prompt_template.format(
            resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "未提供特定岗位要求"
        )

        # formatted_prompt 的内容:
        # """
        # 请分析以下简历的技术能力：
        #
        # {
        #   "personal_info": {
        #     "name": "张三",
        #     "phone": "13800138000"
        #   },
        #   "skills": [
        #     {"name": "Python", "level": "熟练"}
        #   ]
        # }
        #
        # 目标岗位要求：
        # 5年以上Python开发经验，熟悉Django/Flask框架
        #
        # 请以JSON格式输出分析结果。
        # """

        # ========================================
        # 步骤3: 获取System Prompt
        # ========================================
        system_prompt = self.get_system_prompt("technical")

        # 或者直接从PromptManager获取:
        # system_prompt = prompt_manager.get_system_prompt("technical_analysis")

        # system_prompt 的内容:
        # """
        # 你是一位资深技术面试官，擅长评估候选人的技术能力。
        #
        # 你的任务是从以下维度分析候选人的技术能力：
        # 1. **技能广度**（30分）
        #    - 技术栈覆盖面
        #    ...
        #
        # 评分标准：
        # - 90-100分：技术专家，全面且深入
        # ...
        # """

        # ========================================
        # 步骤4: 构造消息并调用LLM
        # ========================================
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ]

        response = await self.llm.ainvoke(messages)

        # ========================================
        # 步骤5: 解析LLM响应
        # ========================================
        response_text = response.content if hasattr(response, 'content') else str(response)

        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # 提取JSON（处理可能的额外文本）
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"score": 60, "note": "解析失败，返回默认分数"}
```

### 示例2: ParsingAgent 解析Agent

**文件**: [agents/parsing_agent.py](agents/parsing_agent.py#L28-L30)

```python
from agents.base import BaseAgent
from prompts import prompt_manager

class ParsingAgent(BaseAgent):

    def get_system_prompt(self) -> str:
        """获取系统Prompt"""
        # 直接从PromptManager获取
        return prompt_manager.get_system_prompt("parsing")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行简历解析任务"""

        # 获取System Prompt
        system_prompt = self.get_system_prompt()

        # 获取User Prompt模板并格式化
        user_prompt_template = prompt_manager.get_user_prompt("parsing")
        formatted_prompt = user_prompt_template.format(
            text=resume_text,
            parse_type="结构化提取"
        )

        # 调用LLM
        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ])

        # 解析结果
        return self._parse_response(response)
```

---

## 5️⃣ 使用流程图 {#flow}

### 完整的数据流动

```
┌─────────────────────────────────────────────────────────────────┐
│                     1. Agent 初始化                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent.__init__(llm, verbose)                                     │
│                                                                  │
│  from prompts import prompt_manager  # 导入全局单例             │
│                                                                  │
│  self.llm = llm                                                  │
│  self.verbose = verbose                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     2. Agent 执行                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agent.run(input_data)                                           │
│                                                                  │
│  # 获取Prompt模板                                               │
│  user_prompt = prompt_manager.get_user_prompt("analysis")      │
│  system_prompt = prompt_manager.get_system_prompt("analysis")  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  3. 格式化Prompt（填充数据）                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  formatted = user_prompt.format(                                 │
│      resume_data=json.dumps(data),  # ← 简历数据转JSON          │
│      job_requirements="..."           # ← 岗位要求               │
│  )                                                                │
│                                                                  │
│  结果: "请分析以下简历：\n\n{...简历JSON...}\n\n目标：..."     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. 调用LLM                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  await llm.ainvoke([                                             │
│      {"role": "system", "content": system_prompt},              │
│      {"role": "user", "content": formatted}                     │
│  ])                                                               │
│                                                                  │
│  发送给ChatZhipuAI (GLM-4)                                       │
│  - System: "你是一位资深技术面试官..."                          │
│  - User:   "请分析以下简历：\n{...JSON数据...}"                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  5. 解析响应                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  response.content = '{"score": 85, "insights": [...]}'          │
│                                                                  │
│  result = json.loads(response.content)                          │
│                                                                  │
│  返回: {                                                         │
│    "score": 85,                                                 │
│    "insights": [...],                                           │
│    "highlights": [...]                                         │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 关键要点

### 1. PromptManager 是全局单例

```python
# prompts/__init__.py (最后几行)
prompt_manager = PromptManager()  # 创建全局唯一实例

# 使用时只需导入
from prompts import prompt_manager
```

### 2. 所有Agent共享同一个PromptManager

```python
# 在任何Agent中都可以使用
class AnalysisAgent(BaseAgent):
    def __init__(self, llm, verbose):
        super().__init__(llm, verbose)

class ParsingAgent(BaseAgent):
    def __init__(self, llm, verbose):
        super().__init__(llm, verbose)

# 两者都使用同一个 prompt_manager
```

### 3. Prompt模板支持参数化

```python
# Prompt模板定义
class TechnicalAnalysisPrompt(BasePrompt):
    def get_user_prompt(self) -> str:
        return """请分析以下简历：
        {resume_data}

        目标：{job_requirements}"""

# 使用时填充
formatted = user_prompt.format(
    resume_data=json.dumps(data),
    job_requirements="Python开发"
)
```

### 4. System Prompt 和 User Prompt 分离

```python
# System Prompt: 定义AI的角色和任务
system_prompt = "你是一位资深技术面试官..."

# User Prompt: 提供具体的数据和上下文
user_prompt = "请分析这份简历：\n{简历数据}"

# 两者组合发送给LLM
llm.ainvoke([
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
])
```

---

## 📊 API速查表

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get(name)` | prompt名称 | Prompt实例 | 获取Prompt对象 |
| `get_system_prompt(name)` | prompt名称 | 字符串 | 获取System Prompt |
| `get_user_prompt(name)` | prompt名称 | 字符串 | 获取User Prompt模板 |
| `format_prompt(name, **kwargs)` | 名称+参数 | 字符串 | 格式化Prompt |
| `list_prompts()` | 无 | 列表 | 列出所有Prompt名称 |
| `register(name, prompt)` | 名称+Prompt | 无 | 注册新Prompt |

---

## 🎯 实际使用示例

### 示例：创建自定义Prompt

```python
from prompts import prompt_manager, BasePrompt

class MyCustomPrompt(BasePrompt):
    """自定义Prompt"""

    def get_system_prompt(self) -> str:
        return "你是一位专业的简历分析师"

    def get_user_prompt(self) -> str:
        return """请分析简历：{resume}"""

# 注册到PromptManager
my_prompt = MyCustomPrompt()
prompt_manager.register("my_analysis", my_prompt)

# 使用
system_prompt = prompt_manager.get_system_prompt("my_analysis")
user_prompt = prompt_manager.get_user_prompt("my_analysis")

formatted = user_prompt.format(resume="简历内容...")
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| [prompts/__init__.py](prompts/__init__.py) | PromptManager定义 |
| [prompts/base.py](prompts/base.py) | BasePrompt基类 |
| [prompts/analysis_prompts.py](prompts/analysis_prompts.py) | 分析Prompt实现 |
| [agents/analysis_agent.py](agents/analysis_agent.py) | Agent使用示例 |

---

**文档版本**: v1.0
**最后更新**: 2026-01-28
