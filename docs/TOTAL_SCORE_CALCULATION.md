# 总分计算说明

**版本**: 1.0
**最后更新**: 2026-01-29

---

## 总分计算公式

```
总分 = (技术能力分数 × 25%) + (经验背景分数 × 20%) + (项目经验分数 × 40%) + (软技能分数 × 15%)
```

---

## 维度权重配置

**位置**: [config/scoring.yaml](config/scoring.yaml:3-7)

```yaml
weights:
  technical: 0.25   # 技术能力 25%
  experience: 0.20  # 经验背景 20%
  project: 0.40     # 项目经验 40%
  soft_skill: 0.15  # 软技能 15%
```

**权重说明**:
- **项目经验** (40%): 权重最高，强调实战能力
- **技术能力** (25%): 基础能力要求
- **经验背景** (20%): 教育和工作经历
- **软技能** (15%): 综合素质

---

## 计算示例

### 示例1: 均衡型候选人

```
技术能力: 80分 × 25% = 20.00
经验背景: 75分 × 20% = 15.00
项目经验: 85分 × 40% = 34.00
软技能:   70分 × 15% = 10.50
─────────────────────────────
总分:                    = 79.50分
```

### 示例2: 项目突出型

```
技术能力: 60分 × 25% = 15.00
经验背景: 70分 × 20% = 14.00
项目经验: 95分 × 40% = 38.00
软技能:   65分 × 15% = 9.75
─────────────────────────────
总分:                    = 76.75分
```

**说明**: 即使技术和经验略弱，项目经验突出也可以获得较高总分。

---

## 代码实现

**位置**: [agents/analysis_agent.py:122-142](agents/analysis_agent.py#L122-L142)

```python
# 计算各维度的加权分数
"technical": {
    "score": technical_result_obj.score,           # 原始分数: 80
    "weight": config.weights["technical"],          # 权重: 0.25
    "weighted_score": technical_result_obj.score * config.weights["technical"],  # 加权分数: 80 × 0.25 = 20
    "detail_scores": technical_result_obj.detail_scores
}
# ... 其他维度类似
```

---

## 调整权重

### 如何修改权重

编辑 [config/scoring.yaml](config/scoring.yaml):

```yaml
weights:
  technical: 0.30   # 提高技术能力权重到30%
  experience: 0.20
  project: 0.35     # 降低项目经验到35%
  soft_skill: 0.15
```

### 不同岗位的权重建议

**研发岗位**:
```yaml
weights:
  technical: 0.30   # 重视技术
  experience: 0.20
  project: 0.35     # 重视项目实战
  soft_skill: 0.15
```

**管理岗位**:
```yaml
weights:
  technical: 0.20   # 降低技术要求
  experience: 0.30  # 提高经验要求
  project: 0.35     # 重视项目管理
  soft_skill: 0.15   # 重视软技能
```

**初级岗位**:
```yaml
weights:
  technical: 0.25
  experience: 0.15   # 降低经验要求
  project: 0.35
  soft_skill: 0.25   # 提高软技能（学习潜力）
```

---

## 分数等级

**位置**: [agents/report_agent.py:501-510](agents/report_agent.py#L501-L510)

```python
if total_score >= 85:
    return "强烈推荐 - 候选人综合能力优秀"
elif total_score >= 75:
    return "推荐 - 候选人综合能力良好"
elif total_score >= 65:
    return "谨慎推荐 - 候选人基本符合要求"
else:
    return "不推荐 - 候选人能力有待提升"
```

**等级划分**:
- **85-100分**: 强烈推荐（优秀）
- **75-84分**: 推荐（良好）
- **65-74分**: 谨慎推荐（合格）
- **0-64分**: 不推荐（待提升）

---

## 常见问题

### Q1: 为什么项目经验权重最高（40%）？

**A**: 项目经验最能反映实际工作能力：
- 展示真实的技术应用
- 体现解决问题能力
- 反映业务理解深度
- 证明实战经验

### Q2: 总分可以超过100分吗？

**A**: 不可以。总分计算方式为：
```
总分 = ∑(各维度分数 × 权重) ≤ 100
```

由于每个维度分数 ≤ 100，权重总和 = 1，所以总分 ≤ 100。

### Q3: 如果某个维度分数为0会怎样？

**A**: 该维度得分为0，但总分仍可由其他维度组成。

**示例**:
```
技术能力: 0分 × 25% = 0
经验背景: 80分 × 20% = 16
项目经验: 90分 × 40% = 36
软技能:   70分 × 15% = 10.5
─────────────────────────────
总分:                = 62.5分
```

### Q4: 如何平衡各维度分数？

**A**: 理想的候选人应该在项目经验和技术能力上都有较好表现：

| 维度 | 优秀 | 良好 | 合格 |
|------|------|------|------|
| 项目经验 | ≥85 | ≥75 | ≥65 |
| 技术能力 | ≥80 | ≥70 | ≥60 |
| 经验背景 | ≥75 | ≥65 | ≥55 |
| 软技能 | ≥70 | ≥60 | ≥50 |

---

## 配置验证

运行测试查看当前权重配置：

```python
from core.config import ScoreConfig

config = ScoreConfig.from_yaml("config/scoring.yaml")
print("当前权重配置:")
for key, value in config.weights.items():
    print(f"  {key}: {value*100:.0f}%")
```

**输出**:
```
当前权重配置:
  technical: 25%
  experience: 20%
  project: 40%
  soft_skill: 15%
```

---

## 相关文档

- [技术能力评分标准](TECHNICAL_SCORING_STANDARD.md)
- [经验背景评分标准](EXPERIENCE_SCORING_STANDARD.md)
- [项目经验评分标准](PROJECT_SCORING_STANDARD.md)
- [配置文件](config/scoring.yaml)
