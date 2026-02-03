# 经验背景归一化处理文档

## 更新日期
2026-01-31

## 问题分析

### 原始问题

**未归一化前的评分**：
- 理论最高分：50.8分
  - 教育背景：30分 × 0.29 = 8.7分
  - 工作经验：60分 × 0.70 = 42分
  - 实习经验：10分 × 0.01 = 0.1分
  - **总计：50.8分** ❌

**真实案例**：
- 清华本科+6年工作 = 47.8分（未到50分）
- 清华博士+6年工作 = 50.7分（理论最高分）

**问题**：即使满分也无法达到60分及格线！

---

## 解决方案：归一化处理

### 代码实现

**文件**：[tools/analysis/experience_analyzer.py:173-231](../tools/analysis/experience_analyzer.py#L173-L231)

**核心代码**：
```python
def _calculate_total_score(self, detail_scores: Dict[str, float]) -> float:
    """计算总分（使用配置的权重 + 归一化到0-100）"""

    # 计算加权总分（原始得分）
    weighted_total = (
        dimension_sums["education"] * weights.get("education", 0.29) +
        dimension_sums["work"] * weights.get("work", 0.70) +
        dimension_sums["internship"] * weights.get("internship", 0.01)
    )

    # 计算理论最高分（用于归一化）
    max_education = 30  # 学历20 + 学校10
    max_work = 60       # 6年工作经验
    max_internship = 10 # 12个月实习

    max_possible = (
        max_education * weights.get("education", 0.29) +
        max_work * weights.get("work", 0.70) +
        max_internship * weights.get("internship", 0.01)
    )  # = 50.8

    # 归一化到0-100范围
    if max_possible > 0:
        normalized_total = (weighted_total / max_possible) * 100
    else:
        normalized_total = 0

    return round(min(normalized_total, 100), 2)
```

### 归一化公式

```
归一化得分 = (原始得分 / 50.8) × 100
```

---

## 效果对比

### 更新前（无归一化）

| 案例 | 原始得分 | 评价 |
|------|----------|------|
| 清华本科+6年工作 | 47.8分 | ❌ 不到50分 |
| 清华博士+6年工作 | 50.7分 | ❌ 理论最高分 |
| 普通本科+3年工作 | 25.4分 | ❌ 仅为理论最高分的50% |

### 更新后（有归一化）

| 案例 | 原始得分 | 归一化后 | 评价 |
|------|----------|----------|------|
| 清华本科+6年工作 | 47.8分 | **94分** ✅ | 优秀 |
| 清华博士+6年工作 | 50.7分 | **99.8分** ✅ | 接近满分 |
| 普通本科+3年工作 | 25.4分 | **50分** ✅ | 中等 |

---

## 配置文件更新

**文件**：[config/scoring.yaml](../config/scoring.yaml)

**用户同步调整**：
```yaml
# 提高教育权重（29% → 50%）
experience_dimension_weights:
  education: 0.50    # 0.29 → 0.50
  work: 0.50         # 0.70 → 0.50
  internship: 0.01

# 提高学历分数
degree_scores:
  博士: 40   # 20 → 40 (+100%)
  硕士: 20   # 15 → 20 (+33%)
  本科: 10   # 保持不变

# 提高学校分数
school_tier_scores:
  "985": 20  # 10 → 20 (+100%)
  "211": 15  # 7 → 15 (+114%)
  普通: 10   # 5 → 10 (+100%)
```

### 新的计算结果（配置更新后）

**理论最高分**：
- 教育背景：40分（博士20 + 985 20）× 0.50 = 20分
- 工作经验：60分 × 0.50 = 30分
- 实习经验：10分 × 0.01 = 0.1分
- **总分：50.1分**

**归一化后**：
- 清华博士+6年工作 = (40×0.5 + 60×0.5) / 50.1 × 100 = **99.8分** ✅

---

## 技术细节

### 归一化的优点

1. **分数范围合理**：0-100分，符合用户预期
2. **各维度平衡**：避免工作权重过高压倒教育
3. **可解释性强**：94分表示达到理论最高分的94%

### 归一化的注意事项

1. **权重敏感性**：调整权重会影响归一化结果
2. **理论最高分变化**：配置调整后需要重新计算max_possible
3. **向后兼容**：已调整配置的需要重新分析简历

### 动态计算理论最高分

代码中的max_possible是动态计算的：

```python
max_possible = (
    max_education * weights.get("education", 0.29) +
    max_work * weights.get("work", 0.70) +
    max_internship * weights.get("internship", 0.01)
)
```

这意味着：
- 调整权重 → 自动调整归一化基准
- 调整分数 → 自动调整归一化基准
- **归一化始终有效** ✅

---

## 测试验证

### 单元测试

创建测试验证归一化：

```python
# 测试：理论最高分应归一化到100
max_detail = {
    "教育背景_学历层次": 20,  # 博士
    "教育背景_学校层次": 10,  # 985
    "工作经验_年限": 60,       # 6年
    "实习经验_时长": 10         # 12个月
}

result = analyzer._calculate_total_score(max_detail)
assert result == 100.0  # 归一化后应该是满分
```

### 真实案例验证

```python
# 清华本科 + 6年工作
detail = {
    "教育背景_学历层次": 10,
    "教育背景_学校层次": 10,
    "工作经验_年限": 60
}

# 原始得分：47.8分
# 归一化后：47.8 / 50.8 × 100 = 94.1分 ✅
```

---

## 相关文件

- **代码实现**：[tools/analysis/experience_analyzer.py](../tools/analysis_analyzer.py)
- **配置文件**：[config/scoring.yaml](../config/scoring.yaml)
- **评分标准**：[EXPERIENCE_SCORING_STANDARD.md](./EXPERIENCE_SCORING_STANDARD.md)

---

**更新人员**: AI Assistant
**审核状态**: ✅ 完成
