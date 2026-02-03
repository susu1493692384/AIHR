# 优化建议Prompt增强文档

## 更新日期
2026-01-31

## 更新目的
增强LLM生成的优化建议的详细程度和可操作性，解决建议字数太少、不够具体的问题。

## 更新内容

### 1. Prompt增强

#### System Prompt更新

**核心要求**：
- 每条建议总字数不少于150字
- 包含5个详细部分：问题分析、改进步骤、改进示例、预期效果、优先级
- 改进步骤必须3-5个具体步骤，避免空泛表述
- 示例必须提供"改进前vs改进后"的对比

#### User Prompt更新

**输出格式要求**：
```json
[
  {
    "category": "技术能力",
    "problem_analysis": "问题分析（2-3句话，50-80字）",
    "action_steps": [
      "步骤1：具体行动方案",
      "步骤2：具体行动方案",
      "步骤3：具体行动方案"
    ],
    "before_after": "改进前：...\\n改进后：...",
    "expected_benefit": "预期效果（1-2句话，30-60字）",
    "priority": "高"
  }
]
```

### 2. 前端显示更新

**新增字段显示**：
- 🔍 **问题分析**：说明当前存在的问题
- 📋 **改进步骤**：3-5个具体可执行的步骤
- ✨ **改进示例**：改进前vs改进后的对比
- 🎯 **预期效果**：改进后能带来的好处

**向后兼容**：
- 保留旧格式支持（只有`suggestion`和`example`字段）
- 新格式优先显示详细信息

### 3. 代码更新

#### 文件：[prompts/optimization_prompts.py](../prompts/optimization_prompts.py)

**OptimizationPrompts类**：
- System Prompt：增加详细要求（150字以上、5个部分、3-5个步骤）
- User Prompt：增加详细格式说明和示例

**PriorityOptimizationPrompt类**：
- System Prompt：增加详细要求（120字以上、4个部分）
- User Prompt：增加详细格式说明

#### 文件：[app/streamlit_app.py](../app/streamlit_app.py)

**显示逻辑更新**（lines 652-695）：
```python
# 新格式：详细建议
if suggestion.get("problem_analysis"):
    st.markdown("**🔍 问题分析**")
    st.write(suggestion.get("problem_analysis"))

    st.markdown("**📋 改进步骤**")
    for step in action_steps:
        st.markdown(f"- {step}")

    st.markdown("**✨ 改进示例**")
    st.markdown(before_after)

    st.markdown("**🎯 预期效果**")
    st.info(suggestion.get("expected_benefit"))
# 旧格式：简单建议（向后兼容）
else:
    st.write(suggestion.get("suggestion", ""))
```

## 示例对比

### 更新前（旧格式）

```json
{
  "category": "技术能力",
  "suggestion": "您的技能熟练度有待提升，建议深入学习核心技术。",
  "priority": "高",
  "example": "例如：深入学习Django框架源码"
}
```

**字数**：约40字
**问题**：过于简略，缺乏具体步骤

### 更新后（新格式）

```json
{
  "category": "技术能力",
  "problem_analysis": "您的技能熟练度分布不均衡，精通级别的技能较少，大部分技能停留在了解水平。这会导致技术能力得分偏低，影响面试机会。",
  "action_steps": [
    "选择1-2项核心技术（如Python、Java），制定深入学习计划",
    "通过实战项目提升熟练度，例如开发一个完整的应用系统",
    "阅读框架源码（如Django、Spring），理解底层实现原理",
    "参与开源项目贡献代码，获得代码审查反馈",
    "在简历中调整技能等级描述，如实标注但突出核心技能"
  ],
  "before_after": "改进前：技能：Python(了解)、Java(了解)、MySQL(了解)\\n改进后：技能：Python(熟练)- 熟练使用Django/Flask框架，开发过3个完整项目；Java(熟悉)- 掌握Spring Boot，具备微服务开发经验；MySQL(熟练)- 熟悉索引优化、主从复制，处理过百万级数据",
  "expected_benefit": "技术能力得分提升15-20分，面试时展现扎实的技术基础，获得更多技术面试机会。",
  "priority": "高"
}
```

**字数**：约250字
**改进**：详细的问题分析、具体的改进步骤、明确的改进示例、可量化的预期效果

## 效果预期

### 1. 建议质量提升

| 指标 | 更新前 | 更新后 | 提升 |
|------|--------|--------|------|
| 平均字数 | 40-60字 | 150-250字 | 3-4倍 |
| 具体步骤 | 无 | 3-5个 | ✅ |
| 改进示例 | 简单 | 对比形式 | ✅ |
| 可操作性 | 低 | 高 | ✅ |

### 2. 用户体验提升

- ✅ 建议更具体，求职者知道如何执行
- ✅ 提供改进前后的对比，便于理解
- ✅ 明确预期效果，更有改进动力
- ✅ 分步骤展示，不会感到overwhelming

### 3. 兼容性保障

- ✅ 支持新格式（详细建议）
- ✅ 兼容旧格式（简单建议）
- ✅ 规则工具fallback保持不变

## 使用说明

### LLM模式（推荐）

当LLM可用时，会自动生成详细建议：
```python
# 自动调用LLM生成
suggestions = await optimization_agent.run(input_data)
# 返回详细格式建议
```

### 规则工具模式

当LLM不可用时，使用规则工具：
```python
# fallback到规则工具
from tools.optimization import SuggestionGenerator
suggestions = SuggestionGenerator.generate_suggestions(
    analysis_results,
    resume_data
)
# 返回简单格式建议（保持向后兼容）
```

## 注意事项

1. **LLM API成本**：更详细的prompt会增加token消耗，但换来更高质量的建议
2. **响应时间**：LLM生成详细建议需要更多时间，建议配合loading提示使用
3. **缓存策略**：建议的缓存时间可以设置更长（如24小时），因为建议相对稳定
4. **渐进式展示**：前端使用expander，用户可以选择性查看详情

## 测试验证

运行以下命令测试新格式：

```bash
# 测试LLM生成详细建议
python -c "
import asyncio
from agents.optimization_agent import OptimizationAgent
from utils.llm_helpers import get_llm

async def test():
    llm = get_llm()
    agent = OptimizationAgent(llm, verbose=True)

    test_data = {
        'analysis_results': {
            'score_breakdown': {
                'technical': {'score': 45, 'detail_scores': {'技能总数': 3, '精通': 0}}
            }
        },
        'resume_data': {'skills': [{'name': 'Python', 'level': '了解'}]},
        'job_requirements': ''
    }

    result = await agent.run(test_data)
    print(result)

asyncio.run(test())
"
```

## 相关文件

- [prompts/optimization_prompts.py](../prompts/optimization_prompts.py) - Prompt定义
- [agents/optimization_agent.py](../agents/optimization_agent.py) - Agent实现
- [app/streamlit_app.py](../app/streamlit_app.py) - 前端显示
- [tools/optimization/suggestion_generator.py](../tools/optimization/suggestion_generator.py) - 规则工具

---

**更新人员**: AI Assistant
**审核状态**: ✅ 完成
