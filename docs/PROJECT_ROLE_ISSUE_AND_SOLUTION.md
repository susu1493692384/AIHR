# 项目角色字段问题及解决方案

## 问题描述

实际简历解析后，`Project.role` 字段的内容不是"角色"（如"负责人"、"核心开发"），而是"职责描述"（如"独立构建..."、"负责数据采集..."）。

### 问题示例

```json
{
  "name": "智慧教学助手",
  "role": "独立构建模型专属数据库，并使用 GLM3搭建大语言模型，实现大语言模型的本地化。",
  "start_time": "2025-01",
  "end_time": "2025-04"
}
```

**期望的 role**: "负责人"、"核心"、"开发" 等
**实际的 role**: "独立构建模型专属数据库..."（这是职责描述）

### 影响

1. **角色匹配失败**: `if "负责人" in proj.role` 无法匹配到职责描述
2. **评分失真**: 项目质量评分中的角色加分无法生效
3. **数据不一致**: 与数据模型定义的字段语义不符

---

## 解决方案

### 方案1: 增强 ProjectAnalyzer 的角色识别能力 ⭐ 推荐

在 ProjectAnalyzer 中增加智能角色识别，从职责描述中推断角色。

**优点**:
- 不需要修改已解析的数据
- 向后兼容
- 灵活可配置

**实现**:

```python
def _infer_role_from_description(self, proj: Project) -> str:
    """
    从项目描述中推断实际角色

    检查优先级：
    1. 如果 role 已是标准角色，直接返回
    2. 从职责描述中识别角色关键词
    3. 根据描述特征推断角色
    """
    # 如果已经是标准角色，直接返回
    standard_roles = ["负责人", "主导", "核心", "开发", "参与"]
    for std_role in standard_roles:
        if std_role in proj.role:
            return std_role

    # 从职责描述中识别
    role_lower = proj.role.lower()

    # 负责人/主导特征词
    lead_keywords = ["独立", "主导", "负责", "搭建", "设计", "架构", "lead", "owner"]
    if any(kw in role_lower for kw in lead_keywords):
        # 检查是否完整负责整个项目
        if "独立" in role_lower or "搭建" in role_lower or "构建" in role_lower:
            return "负责人"
        return "核心"

    # 核心开发特征词
    core_keywords = ["实现", "开发", "训练", "优化", "implement", "develop"]
    if any(kw in role_lower for kw in core_keywords):
        return "核心"

    # 参与特征词
    assist_keywords = ["协助", "参与", "采集", "标注", "assist"]
    if any(kw in role_lower for kw in assist_keywords):
        return "参与"

    # 默认
    return "开发"
```

**配置文件**:

```yaml
# config/scoring.yaml

# 角色推断关键词配置
project_role_inference:
  lead_keywords:
    - "独立"
    - "主导"
    - "负责整个"
    - "搭建"
    - "设计架构"

  core_keywords:
    - "实现"
    - "开发"
    - "训练"
    - "优化"
    - "构建"

  assist_keywords:
    - "协助"
    - "参与"
    - "采集"
    - "标注"
    - "处理"
```

### 方案2: 数据清洗阶段修复

在数据清洗工具（MissingValueHandler）中检测并修复 role 字段。

**优点**:
- 数据源头修复，一处修复处处生效
- 可以记录修复日志

**缺点**:
- 需要修改已解析的数据
- 可能丢失原始信息

### 方案3: 改进 LLM 解析 Prompt

优化解析提示词，明确区分"角色"和"职责"。

**Prompt 优化**:

```
请提取项目经验信息，每个项目需要包含：

1. 项目名称
2. 项目角色（注意：这是一个简短的角色名称，如"负责人"、"核心开发"、"开发人员"等，不要填写职责描述）
3. 项目时间
4. 技术栈
5. 项目描述（项目背景、目标等）
6. 项目职责/成就（你在项目中具体做了什么）

示例：
❌ 错误示例：
  role: "独立构建模型专属数据库，并使用 GLM3搭建大语言模型"

✅ 正确示例：
  role: "负责人"
  achievements: ["独立构建模型专属数据库", "使用 GLM3搭建大语言模型"]
```

---

## 推荐实施方案

**组合方案**: 方案1 + 方案3

### 第一步: 立即修复（方案1）

修改 ProjectAnalyzer，增加智能角色识别功能，处理已有的和未来的数据。

### 第二步: 根本解决（方案3）

优化 LLM 解析提示词，从源头确保数据格式正确。

### 实施优先级

1. **高优先级**: 方案1（立即解决现有数据问题）
2. **中优先级**: 方案3（防止新数据出现问题）
3. **低优先级**: 方案2（如果需要完整的修复日志）

---

## 技术细节

### 角色识别逻辑

```
role 字段内容可能是：

1. 标准角色:
   - "负责人"、"核心开发"、"开发人员"
   → 直接使用

2. 职责描述:
   - "独立构建模型专属数据库，并使用 GLM3..."
   - "负责数据采集、原始数据处理..."
   - "基于 YOLOv8 架构的关键点检测..."
   → 识别关键词，推断角色

3. 混合形式:
   - "项目负责人，负责架构设计"
   → 提取标准角色部分
```

### 评分策略

```python
# 获取推断后的角色
inferred_role = self._infer_role_from_description(proj)

# 使用推断后的角色进行评分
role_bonus = 0
for keyword, points in self.role_bonus.items():
    if keyword in inferred_role:
        role_bonus = max(role_bonus, points)
```

---

## 配置化设计

所有识别规则和关键词都可以在 `config/scoring.yaml` 中配置：

```yaml
project_role_inference:
  # 负责人/主导特征词
  lead_keywords:
    - "独立"
    - "主导"
    - "负责整个"
    - "从0到1"
    - "搭建系统"

  # 核心开发特征词
  core_keywords:
    - "实现"
    - "开发"
    - "构建"
    - "训练"
    - "优化"

  # 参与特征词
  assist_keywords:
    - "协助"
    - "参与"
    - "采集"
    - "标注"
    - "处理"

  # 默认角色（当无法推断时使用）
  default_role: "开发"
```

---

## 测试验证

创建测试用例验证角色推断功能：

```python
test_cases = [
    {
        "role": "独立构建模型专属数据库，并使用 GLM3搭建大语言模型",
        "expected": "负责人"
    },
    {
        "role": "负责数据采集、原始数据处理及数据标注工作",
        "expected": "核心"
    },
    {
        "role": "参与项目开发，协助完成前端页面",
        "expected": "参与"
    }
]
```

---

## 总结

这个问题反映了实际应用中的数据质量问题。通过增强系统的容错能力和智能识别能力，可以：
1. 提高评分准确性
2. 改善用户体验
3. 增强系统鲁棒性

**关键点**:
- 不要假设数据总是完美的
- 增加容错机制
- 提供可配置的识别规则
- 记录数据修复日志，便于后续分析
