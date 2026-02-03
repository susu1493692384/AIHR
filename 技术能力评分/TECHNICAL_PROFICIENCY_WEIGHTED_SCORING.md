# 技术能力评分实现详解

## 版本信息
- **版本**: v3.0（按熟练度加权）
- **更新日期**: 2026-01-30
- **核心文件**: [tools/analysis/technical_analyzer.py](../tools/analysis/technical_analyzer.py)

---

## 核心算法：按熟练度加权平均

### 算法原理

**总分 = (所有技能的加权平均分 / 最高分) × 100**

其中：
- 每个技能的加权分 = 技能等级分 × 熟练度权重
- 加权平均分 = 所有技能的加权分之和 / 所有权重之和
- 最高分 = 80（所有技能都是"精通"时的加权平均分）

---

## 评分标准

### 1. 技能等级分（LEVEL_SCORES）

| 熟练度 | 基础分 | 说明 |
|--------|--------|------|
| 精通 | 80分 | 专家级，能独立设计系统架构 |
| 熟练 | 60分 | 高级，能独立完成复杂任务 |
| 熟悉 | 40分 | 中级，能在指导下完成常规任务 |
| 了解 | 20分 | 初级，基础认知，需要学习 |

**代码位置**: [technical_analyzer.py:13-18](../tools/analysis/technical_analyzer.py#L13-L18)

```python
LEVEL_SCORES = {
    "精通": 80,
    "熟练": 60,
    "熟悉": 40,
    "了解": 20,
}
```

### 2. 熟练度权重（LEVEL_WEIGHTS）

| 熟练度 | 权重 | 说明 |
|--------|------|------|
| 精通 | 1.5 | 核心技能，权重最高 |
| 熟练 | 1.0 | 主要技能，标准权重 |
| 熟悉 | 0.7 | 可用技能，权重较低 |
| 了解 | 0.5 | 入门技能，权重最低 |

**代码位置**: [technical_analyzer.py:21-26](../tools/analysis/technical_analyzer.py#L21-L26)

```python
LEVEL_WEIGHTS = {
    "精通": 1.5,  # 核心技能，权重最高
    "熟练": 1.0,  # 主要技能
    "熟悉": 0.7,  # 可用技能
    "了解": 0.5,  # 入门技能
}
```

**设计理念**：
- 精通技能权重最高（1.5），体现核心竞争力
- 熟练技能权重为1.0，作为主要技能参考
- 熟悉和了解技能权重较低，避免过度拔高
- 通过加权平均，客观反映技术能力水平

---

## 计算流程

### 步骤1：计算每个技能的加权分

```python
for skill in skills:
    level_score = LEVEL_SCORES.get(skill.level, 40)
    weight = LEVEL_WEIGHTS.get(skill.level, 0.7)
    weighted_score = level_score * weight
```

**示例**：
- Python（精通）= 80 × 1.5 = 120分
- Java（熟练）= 60 × 1.0 = 60分
- MySQL（熟悉）= 40 × 0.7 = 28分
- Git（了解）= 20 × 0.5 = 10分

### 步骤2：计算加权总分和权重总和

```python
weighted_sum = Σ(weighted_score)  # 所有技能的加权分之和
weight_sum = Σ(weight)            # 所有权重之和
```

**示例**：
```
加权总分 = 120 + 60 + 28 + 10 = 218
权重总和 = 1.5 + 1.0 + 0.7 + 0.5 = 3.7
```

### 步骤3：计算加权平均分

```python
avg_weighted_score = weighted_sum / weight_sum
```

**示例**：
```
加权平均分 = 218 / 3.7 = 58.92分
```

### 步骤4：归一化到0-100

```python
max_score = 80  # 最高分（所有技能都是"精通"）
final_score = (avg_weighted_score / max_score) × 100
```

**示例**：
```
最终得分 = (58.92 / 80) × 100 = 73.65分
```

**代码位置**: [technical_analyzer.py:137-188](../tools/analysis/technical_analyzer.py#L137-L188)

---

## 完整示例

### 示例1：均衡型候选人

**技能列表**：
```python
skills = [
    Skill(name="Python", level="精通"),  # 核心技能
    Skill(name="Java", level="熟练"),    # 主要技能
    Skill(name="MySQL", level="熟练"),   # 主要技能
    Skill(name="Docker", level="熟悉"),  # 可用技能
    Skill(name="Git", level="熟悉"),     # 可用技能
    Skill(name="Redis", level="了解"),   # 入门技能
]
```

**计算过程**：

| 技能 | 等级 | 等级分 | 权重 | 加权分 |
|------|------|--------|------|--------|
| Python | 精通 | 80 | 1.5 | 120 |
| Java | 熟练 | 60 | 1.0 | 60 |
| MySQL | 熟练 | 60 | 1.0 | 60 |
| Docker | 熟悉 | 40 | 0.7 | 28 |
| Git | 熟悉 | 40 | 0.7 | 28 |
| Redis | 了解 | 20 | 0.5 | 10 |
| **总和** | - | - | **5.4** | **306** |

**最终计算**：
```
加权平均分 = 306 / 5.4 = 56.67
最终得分 = (56.67 / 80) × 100 = 70.83分
```

### 示例2：专家型候选人（高分）

**技能列表**：
```python
skills = [
    Skill(name="Python", level="精通"),
    Skill(name="Go", level="精通"),
    Skill(name="Java", level="熟练"),
]
```

**计算过程**：

| 技能 | 等级 | 等级分 | 权重 | 加权分 |
|------|------|--------|------|--------|
| Python | 精通 | 80 | 1.5 | 120 |
| Go | 精通 | 80 | 1.5 | 120 |
| Java | 熟练 | 60 | 1.0 | 60 |
| **总和** | - | - | **4.0** | **300** |

**最终计算**：
```
加权平均分 = 300 / 4.0 = 75.0
最终得分 = (75.0 / 80) × 100 = 93.75分
```

### 示例3：初学者型候选人（低分）

**技能列表**：
```python
skills = [
    Skill(name="Python", level="了解"),
    Skill(name="Git", level="了解"),
    Skill(name="Docker", level="了解"),
]
```

**计算过程**：

| 技能 | 等级 | 等级分 | 权重 | 加权分 |
|------|------|--------|------|--------|
| Python | 了解 | 20 | 0.5 | 10 |
| Git | 了解 | 20 | 0.5 | 10 |
| Docker | 了解 | 20 | 0.5 | 10 |
| **总和** | - | - | **1.5** | **30** |

**最终计算**：
```
加权平均分 = 30 / 1.5 = 20.0
最终得分 = (20.0 / 80) × 100 = 25.00分
```

---

## 展示维度（detail_scores）

**重要**：这些维度用于诊断分析，**不参与总分计算**。

### 展示维度列表

| 维度 | 说明 | 示例 |
|------|------|------|
| 技能总数 | 掌握的技能数量 | 6项 |
| 精通 | 精通级别的技能数量 | 2项 |
| 熟练 | 熟练级别的技能数量 | 2项 |
| 熟悉 | 熟悉级别的技能数量 | 1项 |
| 了解 | 了解级别的技能数量 | 1项 |
| 验证技能 | 在项目中验证过的技能 | 4项 |
| 验证比例 | 验证技能占比 | 67% |

**代码位置**: [technical_analyzer.py:87-135](../tools/analysis/technical_analyzer.py#L87-L135)

---

## 为什么使用熟练度加权？

### 优势

1. **突出核心技能**
   - 精通技能权重1.5倍，能显著提升总分
   - 符合实际招聘需求：1个精通技能 > 10个了解技能

2. **避免技能堆砌**
   - 了解技能权重低（0.5），堆砌大量了解技能收益低
   - 鼓励深度学习而非广度撒网

3. **客观反映能力**
   - 加权平均比简单平均更准确
   - 体现技能的熟练度分布

### 对比其他方案

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **简单平均** | 简单易懂 | 无法区分质量 | 技能评估 |
| **按类别加权** | 考虑技能重要性 | 配置复杂，需维护 | 行业细分 |
| **按熟练度加权** | 突出核心竞争力 | - | **通用场景** ✅ |

---

## 代码实现

### 核心计算函数

```python
def _calculate_total_score(self, skills: List[Skill]) -> tuple[float, Dict]:
    """
    计算总分（按熟练度加权平均）

    计算公式：
    - 每个技能的加权分 = 技能等级分 × 熟练度权重
    - 总分 = (所有技能的加权分之和 / 所有权重之和) / 最高分 × 100

    Args:
        skills: 技能列表

    Returns:
        tuple[float, Dict]: (总分, 技能得分明细)
    """
    if not skills:
        return 0.0, {}

    # 计算加权总和
    weighted_sum = 0.0
    weight_sum = 0.0
    skill_breakdown = []

    for skill in skills:
        level_score = self.LEVEL_SCORES.get(skill.level, 40)
        weight = self.LEVEL_WEIGHTS.get(skill.level, 0.7)

        weighted_score = level_score * weight
        weighted_sum += weighted_score
        weight_sum += weight

        skill_breakdown.append({
            "name": skill.name,
            "level": skill.level,
            "level_score": level_score,
            "weight": weight,
            "weighted_score": round(weighted_score, 2)
        })

    # 计算加权平均分
    avg_weighted_score = weighted_sum / weight_sum if weight_sum > 0 else 0

    # 归一化到 0-100
    # 最高分是精通（80分），所以满分是80
    max_score = 80
    final_score = (avg_weighted_score / max_score * 100) if max_score > 0 else 0

    return round(min(final_score, 100), 2), {
        "skills": skill_breakdown,
        "weighted_sum": round(weighted_sum, 2),
        "weight_sum": round(weight_sum, 2),
        "avg_weighted_score": round(avg_weighted_score, 2)
    }
```

---

## 验证与测试

### 测试脚本

```bash
python test/test_technical_proficiency_weighted.py
```

### 验证点

✅ 精通技能占比高的候选人得分更高
✅ 少量精通技能 > 大量了解技能
✅ 总分范围：0-100
✅ 加权平均分范围：0-80

---

## 常见问题

### Q1: 为什么最高分是80而不是100？

**A**: 因为"精通"的基础分是80分。加权平均后，所有技能都是"精通"时：
```
加权平均分 = (80×1.5 + 80×1.5) / (1.5 + 1.5) = 80分
最终得分 = (80 / 80) × 100 = 100分 ✅
```

### Q2: 如果有技能等级不在标准列表中怎么办？

**A**: 使用默认值：
```python
level_score = LEVEL_SCORES.get(skill.level, 40)  # 默认"熟悉"
weight = LEVEL_WEIGHTS.get(skill.level, 0.7)     # 默认0.7
```

### Q3: 如何调整评分标准？

**A**: 修改类属性：
```python
# 如果想降低"精通"的权重
LEVEL_WEIGHTS = {
    "精通": 1.2,  # 从1.5降到1.2
    "熟练": 1.0,
    "熟悉": 0.7,
    "了解": 0.5,
}
```

---

## 相关文档

- [展示维度v2.1更新说明](TECHNICAL_V2.1_UPDATE.md)
- [按类别加权计算详解](TECHNICAL_WEIGHTED_CALCULATION.md)（旧版，仅供参考）
- [前端显示v3.0更新](../docs/FRONTEND_V3.0_UPDATE.md)

---

**更新日期**: 2026-01-30
**文档版本**: v3.0
**维护者**: System
