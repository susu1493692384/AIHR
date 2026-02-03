# LLM 岗位匹配工具使用说明

## 更新日期
2026-01-30

## 概述

`LLMJobMatcher` 是一个基于大语言模型的智能岗位匹配工具，用于判断候选人的简历与岗位要求的匹配程度。

### 与规则引擎的对比

| 特性 | 规则引擎 (JobMatcher) | LLM 匹配器 (LLMJobMatcher) |
|------|---------------------|---------------------------|
| **实现方式** | 硬编码规则 | LLM 智能分析 |
| **配置依赖** | 需要维护大量关键词配置 | 无需额外配置 |
| **灵活性** | 低，只能匹配预定义的关键词 | 高，可以理解复杂的岗位要求 |
| **准确性** | 依赖规则完整性 | 依赖 LLM 理解能力 |
| **速度** | 快，纯本地计算 | 慢，需要调用 LLM API |
| **成本** | 免费 | 需要支付 LLM API 费用 |
| **可维护性** | 需要持续更新关键词配置 | 无需维护 |

---

## 使用方法

### 1. 初始化 LLMJobMatcher

```python
from tools.matching import LLMJobMatcher
from langchain_openai import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",  # 或 gpt-4o
    temperature=0.1,       # 降低温度以获得稳定结果
    api_key="your-api-key"
)

# 创建匹配器
matcher = LLMJobMatcher(llm)
```

### 2. 执行岗位匹配

```python
# 准备数据
job_requirements = """
职位：高级 Java 后端开发工程师

要求：
1. 5年以上 Java 开发经验
2. 精通 Spring Boot、MyBatis
3. 熟悉分布式系统设计
"""

resume_data = {
    "personal_info": {"name": "张三", ...},
    "education": [...],
    "work_experience": [...],
    "projects": [...],
    "skills": [...]
}

# 可选：提供分析结果以获得更准确的匹配
analysis_results = {
    "technical_analysis": {"score": 85.5, ...},
    "experience_analysis": {"score": 80.0, ...},
    "project_analysis": {"score": 75.0, ...}
}

# 执行匹配
result = matcher.match_resume_to_job(
    resume_data=resume_data,
    job_requirements=job_requirements,
    analysis_results=analysis_results  # 可选
)
```

### 3. 解析匹配结果

```python
if result["success"]:
    print(f"匹配分数：{result['match_score']}")
    print(f"匹配等级：{result['match_level']}")
    print(f"总结：{result['summary']}")
    print(f"优势：{result['strengths']}")
    print(f"不足：{result['weaknesses']}")
    print(f"建议：{result['recommendations']}")
else:
    print(f"匹配失败：{result['error']}")
```

---

## 返回结果格式

### 成功时返回

```python
{
    "success": True,
    "match_score": 85,  # 0-100 的整数
    "match_level": "高度匹配",  # 完美匹配|高度匹配|中度匹配|低度匹配|不匹配
    "summary": "候选人整体素质优秀，技能匹配度高...",
    "strengths": [
        "精通 Java 和 Spring Boot",
        "5年以上大厂工作经验",
        "有分布式系统开发经验"
    ],
    "weaknesses": [
        "缺少云原生相关经验"
    ],
    "recommendations": [
        "建议补充 Kubernetes 经验",
        "可以强调系统性能优化经验"
    ],
    "skill_analysis": {
        "matched_skills": ["Java", "Spring Boot", "MySQL", "Redis"],
        "missing_skills": ["Kubernetes", "Docker"],
        "skill_coverage": 75
    },
    "experience_analysis": {
        "years_match": True,
        "relevant_experience": True,
        "analysis": "候选人具有5年以上相关工作经验..."
    },
    "education_analysis": {
        "degree_match": True,
        "major_match": True,
        "analysis": "候选人为985高校计算机专业毕业..."
    }
}
```

### 失败时返回

```python
{
    "success": False,
    "error": "LLM API 调用失败",
    "match_score": 0,
    "match_level": "未知",
    ...
}
```

---

## 集成到系统

### 在 Agent 中使用

```python
# agents/matching_agent.py
from tools.matching import LLMJobMatcher

class MatchingAgent(BaseAgent):
    """岗位匹配 Agent"""

    def __init__(self, llm: BaseChatModel):
        super().__init__(llm)
        self.matcher = LLMJobMatcher(llm)

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = input_data.get("resume_data")
        job_requirements = input_data.get("job_requirements", "")
        analysis_results = input_data.get("analysis_results")

        # 使用 LLM 进行匹配
        match_result = self.matcher.match_resume_to_job(
            resume_data=resume_data,
            job_requirements=job_requirements,
            analysis_results=analysis_results
        )

        return {
            "success": True,
            "match_result": match_result
        }
```

### 在 Streamlit 前端使用

```python
# app/streamlit_app.py
from tools.matching import LLMJobMatcher

def matching_section():
    st.header("岗位匹配分析")

    # 输入岗位要求
    job_requirements = st.text_area(
        "请输入岗位要求",
        height=200,
        placeholder="粘贴职位描述..."
    )

    if st.button("分析匹配度") and job_requirements:
        with st.spinner("正在分析..."):
            # 获取简历数据
            resume_data = st.session_state.get("resume_data")
            analysis_results = st.session_state.get("analysis_results")

            # 创建匹配器
            llm = get_llm()  # 假设有这个函数
            matcher = LLMJobMatcher(llm)

            # 执行匹配
            result = matcher.match_resume_to_job(
                resume_data=resume_data,
                job_requirements=job_requirements,
                analysis_results=analysis_results
            )

            # 显示结果
            if result["success"]:
                st.metric("匹配分数", f"{result['match_score']} 分")
                st.info(f"匹配等级：{result['match_level']}")

                st.subheader("优势")
                for strength in result["strengths"]:
                    st.success(f"- {strength}")

                st.subheader("不足")
                for weakness in result["weaknesses"]:
                    st.warning(f"- {weakness}")

                st.subheader("建议")
                for rec in result["recommendations"]:
                    st.info(f"- {rec}")
```

---

## 配置要求

### 1. LLM API Key

需要配置 OpenAI API Key（或其他兼容的 API）：

```python
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")  # 从环境变量读取
)
```

### 2. 模型选择

推荐使用的模型：

| 模型 | 用途 | 优点 | 缺点 |
|------|------|------|------|
| **gpt-4o-mini** | 日常使用 | 便宜、快速 | 理解能力略弱 |
| **gpt-4o** | 复杂分析 | 理解能力强 | 较贵 |
| **gpt-3.5-turbo** | 测试 | 最便宜 | 能力最弱 |

### 3. Temperature 设置

建议使用较低的 temperature（0.1-0.3）以获得稳定的结果：

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,  # 0.1-0.3 之间
)
```

---

## 最佳实践

### 1. 提供完整的分析结果

```python
# ✅ 推荐
result = matcher.match_resume_to_job(
    resume_data=resume_data,
    job_requirements=job_requirements,
    analysis_results=analysis_results  # 提供分析结果
)

# ❌ 不推荐
result = matcher.match_resume_to_job(
    resume_data=resume_data,
    job_requirements=job_requirements
)
```

### 2. 处理错误情况

```python
result = matcher.match_resume_to_job(...)

if not result.get("success"):
    # LLM 匹配失败，可以使用规则引擎作为后备
    from tools.matching import JobMatcher
    result = JobMatcher.match_resume_to_job(
        resume_data=resume_data,
        job_requirements=job_requirements
    )
```

### 3. 缓存匹配结果

```python
import hashlib

def cache_key(resume_data, job_requirements):
    data = json.dumps(resume_data, sort_keys=True) + job_requirements
    return hashlib.md5(data.encode()).hexdigest()

# 检查缓存
key = cache_key(resume_data, job_requirements)
cached_result = cache.get(key)

if cached_result:
    return cached_result

# 执行匹配
result = matcher.match_resume_to_job(...)

# 保存到缓存
cache.set(key, result, timeout=3600)  # 缓存1小时
```

### 4. 限制岗位要求长度

```python
def truncate_requirements(text: str, max_length: int = 2000) -> str:
    """截断过长的岗位要求"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

job_requirements = truncate_requirements(job_requirements)
```

---

## 迁移指南

### 从 JobMatcher 迁移到 LLMJobMatcher

#### 步骤1：更新导入

```python
# 旧代码
from tools.matching import JobMatcher
matcher = JobMatcher()

# 新代码
from tools.matching import LLMJobMatcher
matcher = LLMJobMatcher(llm)
```

#### 步骤2：更新调用方式

```python
# 旧代码
result = JobMatcher.match_resume_to_job(
    resume_data=resume_data,
    job_requirements=job_requirements
)

# 新代码（需要实例化）
matcher = LLMJobMatcher(llm)
result = matcher.match_resume_to_job(
    resume_data=resume_data,
    job_requirements=job_requirements
)
```

#### 步骤3：处理返回结果差异

```python
# JobMatcher 返回格式
{
    "match_score": 75.5,
    "match_level": "高度匹配",
    "skill_analysis": {
        "matched_skills": [...],
        "missing_skills": [...]
    }
}

# LLMJobMatcher 返回格式（相同，但有额外字段）
{
    "success": True,  # 新增
    "match_score": 75,  # 整数
    "match_level": "高度匹配",
    "summary": "...",  # 新增
    "strengths": [...],  # 新增
    "weaknesses": [...],  # 新增
    "recommendations": [...],  # 新增
    "skill_analysis": {...},
    "experience_analysis": {...},  # 新增
    "education_analysis": {...}  # 新增
}
```

#### 步骤4：添加 LLM 初始化

```python
# 在应用启动时初始化 LLM
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

## 常见问题

### Q1: LLM 匹配太慢怎么办？

**A**:
1. 使用更快的模型（如 `gpt-4o-mini`）
2. 异步调用，避免阻塞主流程
3. 缓存匹配结果
4. 考虑使用规则引擎作为后备

### Q2: LLM 匹配结果不稳定？

**A**:
1. 降低 `temperature` 参数（0.1-0.3）
2. 使用更强大的模型（如 `gpt-4o`）
3. 在提示词中明确评分标准
4. 多次调用取平均值

### Q3: 如何降低成本？

**A**:
1. 优先使用 `gpt-4o-mini`（比 `gpt-4o` 便宜 10 倍）
2. 缓存匹配结果，避免重复调用
3. 只在需要时使用 LLM，简单场景用规则引擎
4. 批量处理以降低 API 调用次数

### Q4: LLM 无法解析 JSON 怎么办？

**A**:
`LLMJobMatcher` 已内置容错机制：
1. 尝试直接解析 JSON
2. 尝试从代码块中提取 JSON
3. 尝试从花括号中提取 JSON
4. 如果都失败，返回错误信息

---

## 配置清理建议

迁移到 `LLMJobMatcher` 后，以下配置可以删除：

### 可删除的配置

```yaml
# config/scoring.yaml

# ❌ 可以删除（LLM 不需要）
common_skills:
  - Java
  - Python
  - ...

chinese_skills:
  it: [...]
  finance: [...]
  ...

industry_major_keywords:
  it:
    major_keywords: [...]
    position_keywords: [...]
  ...

major_relevance_scoring:
  industry_match: 80
  general_match: 60
  default_score: 50
```

### 保留的配置

```yaml
# ✅ 需要保留（其他模块还在使用）
weights: {...}
school_tier: {...}
experience_dimension_weights: {...}
project_dimension_weights: {...}
...
```

---

## 总结

### LLMJobMatcher 的优势

✅ **更灵活**：可以理解各种复杂的岗位要求
✅ **更准确**：基于语义理解，而不是关键词匹配
✅ **更丰富**：提供优势、不足、建议等详细分析
✅ **免维护**：不需要持续更新关键词配置

### 使用建议

1. **生产环境**：使用 LLM 匹配器 + 规则引擎（后备）
2. **测试环境**：使用 `gpt-4o-mini` 节省成本
3. **关键场景**：使用 `gpt-4o` 获得最佳效果
4. **高并发**：使用规则引擎，LLM 用于离线分析

---

**更新日期**: 2026-01-30
**状态**: ✅ 可用
**文档版本**: v1.0
