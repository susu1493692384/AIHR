# 性能优化方案：减少不必要的LLM调用

**问题**：每一步都调用LLM，导致分析速度慢、API成本高

**当前状态**：
- 7个步骤，每步都调用LLM
- 总耗时：40-60秒
- LLM调用次数：7-10次

---

## 📊 当前设计分析

### 步骤1: 解析简历
**当前**：ParsingAgent调用LLM解析
```
file_parser.py (工具) → 提取文本 → ParsingAgent (LLM) → 解析结构
```

**问题**：工具只提取了纯文本，但结构解析交给LLM
**优化方向**：✅ 合理（LLM用于理解非结构化文本）

### 步骤2: 结构映射
**当前**：StructureMappingAgent调用LLM映射
```
parsed_data → LLM → mapped_data
```

**问题**：可以用规则映射，没必要用LLM
**优化方向**：❌ 应该用规则/工具映射

### 步骤3: 数据清洗
**当前**：CleaningAgent调用LLM清洗
```
resume_data → LLM → cleaned_data
```

**问题**：已有工具但没用！
- `DateNormalizer` - 日期标准化
- `TextNormalizer` - 文本清洗
- `MissingValueHandler` - 缺失值处理

**优化方向**：❌ 应该用工具，不用LLM

### 步骤4: 数据去重
**当前**：DeduplicationAgent调用LLM去重
```
resume_data → LLM → deduplicated_data
```

**问题**：去重应该用算法（相似度计算），不需要LLM
**优化方向**：❌ 应该用算法去重

### 步骤5: 多维度分析
**当前**：AnalysisAgent调用LLM x4
```
技术分析 (LLM) → score
经验分析 (LLM) → score
项目分析 (LLM) → score
软技能分析 (LLM) → score
```

**优化方向**：✅ 合理（LLM用于理解内容）

### 步骤6: 优化建议
**当前**：OptimizationAgent调用LLM
```
analysis_results → LLM → suggestions
```

**优化方向**：✅ 合理（需要生成建议）

### 步骤7: 生成报告
**当前**：ReportAgent调用LLM生成报告
```
all_results → LLM → report
```

**问题**：可以用模板+少量LLM润色
**优化方向**：⚠️ 可以用模板生成

---

## 🎯 优化方案

### 方案A：混合架构（推荐）

**目标**：只在做需要"理解"的步骤时使用LLM

| 步骤 | 当前 | 优化后 | 节省 |
|------|------|--------|------|
| 1. 解析 | LLM | 工具 + LLM | - |
| 2. 映射 | LLM | 规则/工具 | ✅ 1次LLM |
| 3. 清洗 | LLM | 工具（DateNormalizer等） | ✅ 1次LLM |
| 4. 去重 | LLM | 算法（相似度计算） | ✅ 1次LLM |
| 5. 分析 | LLM x4 | LLM x4 | - |
| 6. 优化 | LLM | LLM | - |
| 7. 报告 | LLM | 模板 + LLM（可选） | ✅ 0.5次LLM |

**优化结果**：
- LLM调用次数：7-10次 → 4-5次
- 预计节省时间：15-20秒
- 预计节省成本：40-50%

---

### 方案B：快速通道（极速模式）

**思路**：先做规则处理，最后统一用LLM分析

```
规则预处理（并行，不调用LLM）
├── 文件解析（工具）
├── 结构映射（规则）
├── 数据清洗（工具）
├── 数据去重（算法）
└── 数据验证（工具）

智能分析（只调用LLM一次）
└── AnalysisAgent（一次性分析所有维度）

生成建议（调用LLM）
└── OptimizationAgent
```

**优势**：
- LLM调用次数：7-10次 → 2-3次
- 预计耗时：60秒 → 20-30秒
- 工具处理可以并行，更快

---

## 🔧 具体实现建议

### 1. 清洗Agent优化

**当前代码**：
```python
# agents/cleaning_agent.py
response = await self.llm.ainvoke([...])  # 调用LLM
result = self.parse_json_response(response)
```

**优化后**：
```python
# 直接使用工具
from tools.cleaning.date_normalizer import DateNormalizerTool
from tools.cleaning.text_normalizer import TextNormalizerTool
from tools.cleaning.missing_value_handler import MissingValueHandlerTool

# 1. 日期标准化
date_normalizer = DateNormalizerTool()
cleaned_data = date_normalizer.normalize_dates(resume_data)

# 2. 文本清洗
text_normalizer = TextNormalizerTool()
cleaned_data = text_normalizer.normalize_text(cleaned_data)

# 3. 缺失值处理
handler = MissingValueHandlerTool()
cleaned_data = handler.handle_missing_values(cleaned_data)

# 生成清洗报告
report = {
    "normalized_dates": count_dates,
    "cleaned_fields": count_fields,
    "filled_missing": count_missing
}
```

**优势**：
- 不调用LLM，速度快（<1秒）
- 结果确定性，不会因为LLM不稳定而出错
- 代码已经实现了！只需要调用

### 2. 去重Agent优化

**当前**：调用LLM去重

**优化后**：用算法
```python
def deduplicate_skills(skills):
    """使用字符串相似度去重"""
    from difflib import SequenceMatcher

    unique_skills = []
    for skill in skills:
        is_duplicate = False
        for existing in unique_skills:
            similarity = SequenceMatcher(None, skill, existing).ratio()
            if similarity > 0.85:  # 相似度阈值
                is_duplicate = True
                break
        if not is_duplicate:
            unique_skills.append(skill)

    return unique_skills
```

### 3. 结构映射优化

**当前**：调用LLM映射字段

**优化后**：用规则映射
```python
FIELD_MAPPING = {
    "个人信息": "personal_info",
    "教育背景": "education",
    "工作经历": "work_experience",
    # ...
}

def map_structure(parsed_data):
    """使用规则映射字段名"""
    mapped = {}
    for key, value in parsed_data.items():
        mapped_key = FIELD_MAPPING.get(key, key)
        mapped[mapped_key] = value
    return mapped
```

---

## 📈 性能对比

### 当前性能（7次LLM调用）

```
步骤1: 3秒 (文件解析 + LLM)
步骤2: 8秒 (LLM)
步骤3: 5秒 (LLM)
步骤4: 4秒 (LLM)
步骤5: 15秒 (4次LLM并行)
步骤6: 7秒 (LLM)
步骤7: 3秒 (LLM)

总计：45秒
```

### 优化后性能（4-5次LLM调用）

```
步骤1: 3秒 (文件解析 + LLM)
步骤2: 0.5秒 (规则映射)
步骤3: 0.5秒 (工具处理)
步骤4: 0.5秒 (算法去重)
步骤5: 15秒 (4次LLM并行)
步骤6: 7秒 (LLM)
步骤7: 1秒 (模板生成)

总计：27.5秒（节省40%时间）
```

### 极速模式（2-3次LLM调用）

```
规则预处理（并行）: 2秒
智能分析（LLM）: 15秒
生成建议（LLM）: 7秒

总计：24秒（节省50%时间）
```

---

## 🚀 推荐实施步骤

### 阶段1：快速优化（立即实施）
1. **修改CleaningAgent**：直接调用工具，不调用LLM
   - 删除LLM调用代码
   - 使用DateNormalizer、TextNormalizer等工具
   - 预计节省：5秒

2. **修改DeduplicationAgent**：用算法去重
   - 实现相似度计算
   - 预计节省：4秒

**预期效果**：
- 节省时间：9秒（45秒 → 36秒）
- 节省成本：2次LLM调用
- 实施难度：⭐⭐☆☆☆

### 阶段2：中期优化（可选）
3. **修改StructureMappingAgent**：用规则映射
   - 创建字段映射表
   - 预计节省：7.5秒

4. **优化ReportAgent**：用模板生成
   - 创建报告模板
   - LLM只负责润色
   - 预计节省：2秒

**预期效果**：
- 节省时间：9.5秒（36秒 → 26.5秒）
- 节省成本：1.5次LLM调用
- 实施难度：⭐⭐⭐☆☆

### 阶段3：深度优化（长期）
5. **并行化工具处理**
6. **缓存机制**
7. **批量处理**

---

## 💡 总结

### 当前问题
- ✅ 过度依赖LLM，连简单的数据清洗都用LLM
- ✅ 已有工具但没使用（DateNormalizer等）
- ✅ 每步都串行，没有并行处理

### 优化收益
- **性能提升**：45秒 → 26秒（提升42%）
- **成本降低**：减少40-50%的LLM调用
- **稳定性**：工具处理比LLM更稳定

### 实施建议
1. **立即**：修改CleaningAgent和DeduplicationAgent，使用工具和算法
2. **可选**：优化StructureMappingAgent和ReportAgent
3. **保持**：AnalysisAgent和OptimizationAgent继续使用LLM（需要理解能力）

---

**文档版本**: v1.0
**最后更新**: 2026-01-28
