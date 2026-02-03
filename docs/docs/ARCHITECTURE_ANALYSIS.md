# AI简历分析系统 - 架构分析文档

**生成时间**: 2026-01-28
**分析目的**: 解答Agent架构、数据流、Prompt配置等关键问题

---

## 📋 问题索引

1. [Agent是否使用了LangChain框架？](#q1)
2. [数据流是怎样的？](#q2)
3. [Prompt如何配置和传递给LLM？](#q3)
4. [完整的调用链路是什么？](#q4)

---

## 1️⃣ Agent是否使用了LangChain框架？ {#q1}

### 答案：**部分使用，但不是完整的LangChain Agent框架**

#### ✅ 使用的LangChain组件

```python
# 1. LLM抽象层
from langchain_core.language_models import BaseChatModel

# 2. 消息类型
from langchain_core.messages import HumanMessage, SystemMessage

# 3. Prompt模板（可选）
from langchain_core.prompts import ChatPromptTemplate
```

#### ❌ 没有使用的LangChain组件

```python
# 这些都没有使用：
from langchain.agents import AgentExecutor  # ❌
from langchain.agents import create_react_agent  # ❌
from langchain.chains import LLMChain  # ❌
from langchain.schema import AgentAction, AgentFinish  # ❌
```

#### 📊 架构对比

| 特性 | LangChain Agent框架 | 本项目实现 |
|------|---------------------|-----------|
| **Agent定义** | 使用AgentExecutor | 自定义BaseAgent |
| **工具调用** | ReAct/Thought模式 | 直接LLM调用 |
| **状态管理** | LangGraph | 自定义state字典 |
| **Prompt管理** | LangChain Prompts | 自定义PromptManager |
| **LLM调用** | `.ainvoke()` | `.ainvoke()` (相同) |

#### 💡 核心代码：[agents/base.py](agents/base.py#L78-L100)

```python
async def invoke_llm(
    self,
    system_prompt: str,
    user_prompt: str
) -> Any:
    """
    调用LLM的辅助方法
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    return await self.llm.ainvoke(messages)
```

**结论**: 项目使用了LangChain的**LLM抽象层**，但没有使用**Agent框架**。采用自定义的Agent编排方式。

---

## 2️⃣ 数据流是怎样的？ {#q2}

### 完整数据流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                         输入阶段                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1️⃣ 解析阶段 (ParsingAgent)                                     │
│                                                                  │
│  输入: file_path (PDF/DOCX) 或 text (纯文本)                     │
│  输出: {                                                         │
│    "parsed_data": {                                              │
│      "raw_text": "张三\n电话：138-0013-8000\n...",              │
│      "file_type": "pdf",                                         │
│      "pages": 2                                                  │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2️⃣ 结构映射 (StructureMappingAgent)                             │
│                                                                  │
│  输入: parsed_data                                               │
│  输出: {                                                         │
│    "mapped_data": {                                              │
│      "personal_info": {                                          │
│        "name": "张三",                                            │
│        "phone": "13800138000",                                   │
│        "email": "zhangsan@example.com"                           │
│      },                                                           │
│      "education": [...],                                         │
│      "work_experience": [...],                                   │
│      "projects": [...],                                          │
│      "skills": [...]                                             │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3️⃣ 数据清洗 (CleaningAgent)                                     │
│                                                                  │
│  输入: mapped_data                                               │
│  输出: {                                                         │
│    "cleaned_data": {                                             │
│      "personal_info": {                                          │
│        "name": "张三",                                            │
│        "phone": "13800138000",  # 标准化后                       │
│        "email": "zhangsan@example.com"  # 去除空格               │
│      },                                                           │
│      "work_experience": [                                         │
│        {                                                          │
│          "company": "ABC公司",                                    │
│          "start_date": "2020-01",  # 日期标准化                  │
│          "end_date": "至今"                                       │
│        }                                                          │
│      ],                                                           │
│      "skills": [                                                 │
│        {"name": "Python", "level": "熟练"}  # 补全缺失字段        │
│      ]                                                            │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4️⃣ 数据去重 (DeduplicationAgent)                                │
│                                                                  │
│  输入: cleaned_data                                              │
│  输出: {                                                         │
│    "deduplicated_data": {                                        │
│      "skills": [  # 去重后的技能列表                              │
│        {"name": "Python", "level": "熟练"},                      │
│        {"name": "Java", "level": "熟悉"}                         │
│      ],                                                           │
│      ...                                                          │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5️⃣ 多维度分析 (AnalysisAgent)                                    │
│                                                                  │
│  输入: deduplicated_data + job_requirements                      │
│  输出: {                                                         │
│    "analysis_results": {                                         │
│      "technical_analysis": {                                     │
│        "score": 85,                                               │
│        "detail_scores": {                                        │
│          "技能广度": 28,                                          │
│          "技能深度": 27,                                          │
│          "技能相关性": 18,                                        │
│          "技术验证度": 12                                         │
│        },                                                         │
│        "insights": [                                             │
│          "熟练掌握Python和Java",                                 │
│          "有Django项目经验"                                       │
│        ],                                                         │
│        "highlights": [                                           │
│          "技术栈全面",                                            │
│          "项目经验丰富"                                           │
│        ],                                                         │
│        "weaknesses": [                                            │
│          "前端经验较少"                                           │
│        ]                                                          │
│      },                                                           │
│      "experience_analysis": { "score": 75, ... },                │
│      "project_analysis": { "score": 90, ... },                   │
│      "soft_skill_analysis": { "score": 70, ... },                │
│      "total_score": 82.5,  # 加权总分                            │
│      "score_breakdown": {                                         │
│        "technical": {"score": 85, "weight": 0.25},                │
│        "experience": {"score": 75, "weight": 0.20},               │
│        "project": {"score": 90, "weight": 0.40},                 │
│        "soft_skill": {"score": 70, "weight": 0.15}                │
│      }                                                            │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6️⃣ 优化建议 (OptimizationAgent)                                  │
│                                                                  │
│  输入: analysis_results + resume_data                             │
│  输出: {                                                         │
│    "optimization_suggestions": [                                 │
│      {                                                            │
│        "category": "技术能力",                                    │
│        "suggestion": "建议增加前端技术栈的学习",                  │
│        "priority": "高",                                          │
│        "example": "可以学习React或Vue框架"                        │
│      },                                                           │
│      ...                                                          │
│    ]                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7️⃣ 报告生成 (ReportAgent)                                       │
│                                                                  │
│  输入: analysis_results + optimization_suggestions              │
│  输出: {                                                         │
│    "reports": {                                                  │
│      "full": {  # 完整报告                                        │
│        "summary": "...",                                          │
│        "detailed_analysis": { ... },                              │
│        "recommendations": [...]                                   │
│      },                                                           │
│      "hr_summary": {  # HR摘要                                   │
│        "candidate_name": "张三",                                   │
│        "total_score": 82.5,                                       │
│        "key_highlights": [...],                                   │
│        "recommendation": "建议面试"                               │
│      },                                                           │
│      "candidate_summary": {  # 求职者摘要                         │
│        "strengths": [...],                                        │
│        "improvement_areas": [...]                                 │
│      }                                                            │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 数据格式示例

#### 📄 解析后 (Parsed)
```json
{
  "raw_text": "张三\n电话：138-0013-8000\n邮箱：zhangsan@example.com",
  "file_type": "pdf",
  "pages": 1
}
```

#### 🏗️ 结构化后 (Structured)
```json
{
  "personal_info": {
    "name": "张三",
    "phone": "138-0013-8000",
    "email": " zhangsan@example.com "
  },
  "skills": ["Python", "Java", "Python"],  // 可能有重复
  "work_experience": [
    {
      "company": "ABC公司",
      "start_date": "2020.01",
      "end_date": "至今"
    }
  ]
}
```

#### ✨ 清洗后 (Cleaned)
```json
{
  "personal_info": {
    "name": "张三",
    "phone": "13800138000",  // 去除分隔符
    "email": "zhangsan@example.com"  // 去除空格
  },
  "skills": [
    {"name": "Python", "level": "熟练"},  // 补全level
    {"name": "Java", "level": "熟练"}
  ],
  "work_experience": [
    {
      "company": "ABC公司",
      "start_date": "2020-01",  // 标准化为YYYY-MM
      "end_date": "至今"
    }
  ]
}
```

#### 📊 分析后 (Analyzed)
```json
{
  "technical_analysis": {
    "score": 85,
    "detail_scores": {
      "技能广度": 28,
      "技能深度": 27,
      "技能相关性": 18,
      "技术验证度": 12
    },
    "insights": ["技术栈全面，涵盖后端主要技术"],
    "highlights": ["精通Python和Java"],
    "weaknesses": ["前端技术相对薄弱"]
  },
  "total_score": 82.5
}
```

---

## 3️⃣ Prompt如何配置和传递给LLM？ {#q3}

### 🎯 Prompt配置架构

```
PromptManager (全局单例)
    │
    ├── TechnicalAnalysisPrompt
    ├── ExperienceAnalysisPrompt
    ├── ProjectAnalysisPrompt
    ├── SoftSkillAnalysisPrompt
    └── ... (共14个Prompt类)
```

### 📝 Prompt定义示例

#### 代码位置：[prompts/analysis_prompts.py](prompts/analysis_prompts.py#L6-L56)

```python
class TechnicalAnalysisPrompt(BasePrompt):
    """技术能力分析Prompt"""

    def get_system_prompt(self) -> str:
        return """你是一位资深技术面试官，擅长评估候选人的技术能力。

你的任务是从以下维度分析候选人的技术能力：

1. **技能广度**（30分）
   - 技术栈覆盖面（语言、框架、数据库、工具等）
   - 跨领域能力（前端、后端、DevOps等）
   - 技术多样性

2. **技能深度**（30分）
   - 核心技术的熟练程度
   - 技术深度（源码、架构、性能优化等）
   - 技术年限和持续使用情况

3. **技能相关性**（20分）
   - 与目标岗位的匹配度
   - 技术栈的现代性和市场认可度
   - 技术发展趋势的跟随度

4. **技术验证度**（20分）
   - 技能在项目/工作中的应用验证
   - 开源贡献和技术博客
   - 技术认证和奖项

评分标准：
- 90-100分：技术专家，全面且深入
- 80-89分：技术优秀，核心能力强
- 70-79分：技术良好，能满足要求
- 60-69分：技术合格，基本满足
- 60分以下：技术不足，需要提升

请输出：
1. 总分（0-100）
2. 各维度详细得分
3. 关键发现（3-5条）
4. 亮点（2-3条）
5. 不足之处（2-3条）"""

    def get_user_prompt(self) -> str:
        return """请分析以下简历的技术能力：

{resume_data}

目标岗位要求：
{job_requirements}

请以JSON格式输出分析结果。"""
```

### 🔧 Prompt管理器

#### 代码位置：[prompts/__init__.py](prompts/__init__.py#L33-L66)

```python
class PromptManager:
    """Prompt模板管理器"""

    def __init__(self):
        """初始化Prompt管理器"""
        self._prompts: Dict[str, BasePrompt] = {}
        self._register_default_prompts()

    def _register_default_prompts(self):
        """注册默认的Prompt模板"""
        # 分析相关
        self.register("technical_analysis", TechnicalAnalysisPrompt())
        self.register("experience_analysis", ExperienceAnalysisPrompt())
        self.register("project_analysis", ProjectAnalysisPrompt())
        self.register("soft_skill_analysis", SoftSkillAnalysisPrompt())
        # ... 其他Prompt

    def get_system_prompt(self, name: str) -> Optional[str]:
        """获取系统Prompt"""
        prompt = self.get(name)
        return prompt.get_system_prompt() if prompt else None

    def get_user_prompt(self, name: str) -> Optional[str]:
        """获取用户Prompt"""
        prompt = self.get(name)
        return prompt.get_user_prompt() if prompt else None


# 全局Prompt管理器实例
prompt_manager = PromptManager()
```

### 🚀 Prompt传递给LLM的完整流程

#### 代码位置：[agents/analysis_agent.py](agents/analysis_agent.py#L138-L165)

```python
async def _analyze_technical(
    self,
    resume_data: Dict[str, Any],
    job_requirements: str
) -> Dict[str, Any]:
    """分析技术能力"""
    try:
        # 步骤1: 获取Prompt模板
        user_prompt = prompt_manager.get_user_prompt("technical_analysis")

        # 步骤2: 格式化Prompt，填充实际数据
        formatted_prompt = user_prompt.format(
            resume_data=json.dumps(resume_data, ensure_ascii=False, indent=2),
            job_requirements=job_requirements or "未提供特定岗位要求"
        )

        # 步骤3: 获取系统Prompt
        system_prompt = self.get_system_prompt("technical")

        # 步骤4: 构造消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ]

        # 步骤5: 调用LLM
        response = await self.llm.ainvoke(messages)

        # 步骤6: 解析响应
        response_text = response.content if hasattr(response, 'content') else str(response)

        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # 提取JSON（处理可能的额外文本）
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"score": 60, "note": "解析失败，返回默认分数"}

    except Exception as e:
        return {"score": 60, "error": str(e)}
```

### 📤 最终发送给LLM的消息

```json
[
  {
    "role": "system",
    "content": "你是一位资深技术面试官，擅长评估候选人的技术能力。\n\n你的任务是从以下维度分析候选人的技术能力：\n\n1. **技能广度**（30分）\n   - 技术栈覆盖面（语言、框架、数据库、工具等）\n   ...\n\n请输出：\n1. 总分（0-100）\n2. 各维度详细得分\n3. 关键发现（3-5条）\n4. 亮点（2-3条）\n5. 不足之处（2-3条）"
  },
  {
    "role": "user",
    "content": "请分析以下简历的技术能力：\n\n{\n  \"personal_info\": {\n    \"name\": \"张三\",\n    \"phone\": \"13800138000\",\n    \"email\": \"zhangsan@example.com\"\n  },\n  \"skills\": [\n    {\"name\": \"Python\", \"level\": \"熟练\"},\n    {\"name\": \"Java\", \"level\": \"熟悉\"},\n    {\"name\": \"React\", \"level\": \"了解\"}\n  ],\n  \"work_experience\": [\n    {\n      \"company\": \"ABC公司\",\n      \"start_date\": \"2020-01\",\n      \"end_date\": \"至今\",\n      \"position\": \"软件工程师\"\n    }\n  ],\n  \"projects\": [\n    {\n      \"name\": \"电商平台\",\n      \"role\": \"后端开发\",\n      \"description\": \"使用Python和Django开发\"\n    }\n  ]\n}\n\n目标岗位要求：\n5年以上Python开发经验，熟悉Django/Flask框架\n\n请以JSON格式输出分析结果。"
  }
]
```

---

## 4️⃣ 完整的调用链路 {#q4}

### 📍 前端调用入口

#### 代码位置：[app/streamlit_app.py](app/streamlit_app.py#L169-L193)

```python
# 1. 获取LLM实例
llm = get_llm()  # 返回 ChatZhipuAI(model="glm-4")

# 2. 创建OrchestratorAgent
orchestrator = OrchestratorAgent(llm, verbose=False)

# 3. 准备输入数据
input_data = {
    "file_path": temp_path,
    "text": None,
    "job_requirements": job_requirements if job_requirements else "",
    "report_types": report_types or ["full"]
}

# 4. 执行分析
result = asyncio.run(orchestrator.run(input_data))

# 5. 处理结果
if result.get("success"):
    st.session_state.analysis_result = result
    st.success("✅ 分析完成！")
else:
    st.error(f"❌ 分析失败: {result.get('error')}")
```

### 🔗 OrchestratorAgent内部调用链

#### 代码位置：[agents/orchestrator.py](agents/orchestrator.py#L94-L120)

```python
# 初始化所有子Agent
self.parsing_agent = ParsingAgent(llm, verbose)
self.structure_mapping_agent = StructureMappingAgent(llm, verbose)
self.cleaning_agent = CleaningAgent(llm, verbose)
self.deduplication_agent = DeduplicationAgent(llm, verbose)
self.analysis_agent = AnalysisAgent(llm, verbose)  # ← 关键
self.optimization_agent = OptimizationAgent(llm, verbose)
self.report_agent = ReportAgent(llm, verbose)

# 执行流程
await self._step_parse()              # 步骤1: 解析
await self._step_structure_mapping()  # 步骤2: 结构映射
await self._step_clean()              # 步骤3: 清洗
await self._step_deduplicate()        # 步骤4: 去重
await self._step_analyze()            # 步骤5: 分析 ← 关键步骤
await self._step_optimize()           # 步骤6: 优化
await self._step_report()             # 步骤7: 报告
```

### 🔍 AnalysisAgent内部调用

#### 代码位置：[agents/analysis_agent.py](agents/analysis_agent.py#L70-L88)

```python
# 并行执行四个维度的分析
analysis_tasks = [
    self._analyze_technical(resume_data, job_requirements),   # ← 调用LLM
    self._analyze_experience(resume_data),                    # ← 调用LLM
    self._analyze_project(resume_data),                       # ← 调用LLM
    self._analyze_soft_skill(resume_data)                     # ← 调用LLM
]

# 等待所有分析完成
technical_result, experience_result, project_result, soft_skill_result = \
    await self._run_parallel_analysis(analysis_tasks)
```

### 📊 完整调用链路图

```
Streamlit前端 (streamlit_app.py)
    │
    │ asyncio.run(orchestrator.run(input_data))
    ▼
OrchestratorAgent (orchestrator.py)
    │
    ├─→ ParsingAgent.run()
    ├─→ StructureMappingAgent.run()
    ├─→ CleaningAgent.run()
    ├─→ DeduplicationAgent.run()
    ├─→ AnalysisAgent.run()
    │       │
    │       ├─→ _analyze_technical()
    │       │       │
    │       │       ├─→ prompt_manager.get_user_prompt("technical_analysis")
    │       │       ├─→ user_prompt.format(resume_data=..., job_requirements=...)
    │       │       ├─→ self.get_system_prompt("technical")
    │       │       └─→ await self.llm.ainvoke([system_msg, user_msg])  ← LLM调用
    │       │
    │       ├─→ _analyze_experience()  ─────────────────────┐
    │       │       │                                          │
    │       ├─→ _analyze_project()  ─────────────────────────┤
    │       │       │                                          │
    │       └─→ _analyze_soft_skill()  ──────────────────────┤
    │                   │                                      │
    │                   └─→ 4个并行LLM调用                      │
    │                                                              │
    ├─→ OptimizationAgent.run()  ──────────────────────────────┤
    │                                                              │
    └─→ ReportAgent.run()  ─────────────────────────────────────┘
                   │
                   ▼
            返回分析结果
```

---

## 🔑 关键要点总结

### ✅ 已确认的实现细节

1. **LLM集成**
   - ✅ 使用 `langchain_core.language_models.BaseChatModel`
   - ✅ 通过 `ainvoke()` 异步调用LLM
   - ✅ 支持任何兼容BaseChatModel的LLM（ChatZhipuAI, ChatOpenAI等）

2. **Prompt配置**
   - ✅ 14个专用Prompt类
   - ✅ 统一的PromptManager管理
   - ✅ System Prompt + User Prompt分离
   - ✅ 支持参数化（.format()）

3. **数据传递**
   - ✅ 简历数据通过 `json.dumps()` 序列化
   - ✅ 作为User Prompt的一部分发送
   - ✅ LLM返回JSON格式的分析结果

4. **错误处理**
   - ✅ JSON解析失败时提取JSON
   - ✅ LLM调用失败时返回默认分数
   - ✅ 详细的错误日志

### 📊 数据转换示例

```python
# 原始简历数据（Python字典）
resume_data = {
    "personal_info": {"name": "张三", "phone": "13800138000"},
    "skills": ["Python", "Java"]
}

# 转换为JSON字符串（通过Prompt格式化）
resume_json = json.dumps(resume_data, ensure_ascii=False, indent=2)
# 结果: '{\n  "personal_info": {\n    "name": "张三", ...\n  }\n}'

# 填充到Prompt模板
user_prompt = prompt_manager.get_user_prompt("technical_analysis")
formatted = user_prompt.format(
    resume_data=resume_json,
    job_requirements="5年以上Python经验"
)

# 构造消息
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": formatted}
]

# 调用LLM
response = await llm.ainvoke(messages)

# 解析结果
result = json.loads(response.content)
```

---

## 📁 相关文件索引

| 功能 | 文件路径 |
|------|----------|
| Agent基类 | [agents/base.py](agents/base.py) |
| 主控Agent | [agents/orchestrator.py](agents/orchestrator.py) |
| 分析Agent | [agents/analysis_agent.py](agents/analysis_agent.py) |
| Prompt基类 | [prompts/base.py](prompts/base.py) |
| 分析Prompt | [prompts/analysis_prompts.py](prompts/analysis_prompts.py) |
| Prompt管理器 | [prompts/__init__.py](prompts/__init__.py) |
| 前端集成 | [app/streamlit_app.py](app/streamlit_app.py) |

---

**文档版本**: v1.0
**最后更新**: 2026-01-28
**作者**: Claude (AI架构分析师)
