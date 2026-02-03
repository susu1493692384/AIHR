# 项目经验维度总分计算详解

**版本**: 1.0
**最后更新**: 2026-01-29
**分析器**: [ProjectAnalyzer](tools/analysis/project_analyzer.py)

---

## 总分计算公式

```
项目经验总分 = 项目数量得分 + 项目质量得分 + 技术深度得分 + 业务价值得分
```

**评分结构 (总分100分)**:
```
项目数量: 25分
+ 项目质量: 25分
+ 技术深度: 25分
+ 业务价值: 25分
─────────────────────
总分最高: 100分
```

---

## 各子维度评分规则

### 1. 项目数量 (25分)

**配置位置**: [config/scoring.yaml](config/scoring.yaml#L263-L264)

```yaml
project_count_score_per_project: 10  # 每个项目10分
project_count_max_score: 25          # 最高25分
```

**计算公式**:
```
项目数量得分 = min(项目数量 × 10, 25)
```

**示例**:
- 1个项目: 1 × 10 = **10分**
- 2个项目: 2 × 10 = **20分**
- 3个项目: 3 × 10 = **25分** (达到上限)
- 4个及以上: **25分** (上限)

---

### 2. 项目质量 (25分)

**配置位置**: [config/scoring.yaml](config/scoring.yaml#L251-L256)

#### 2.1 角色加分

```yaml
project_role_bonus:
  负责人: 30
  主导: 25
  核心: 20
  开发: 10
  参与: 5
```

**匹配规则**: 角色名称包含关键词即可匹配
- "项目负责人" → 匹配 "负责人" → **30分**
- "核心开发者" → 匹配 "核心" → **20分**

#### 2.2 团队规模加分

```yaml
project_team_size_bonus:
  "20+": 10    # 20人及以上
  "10-19": 5   # 10-19人
  "1-9": 0     # 小团队
```

**计算公式**:
```
项目质量得分 = sum(每个项目的角色加分 + 团队规模加分)
最高25分
```

**示例**:
```
项目1: 负责人(30分) + 20人团队(10分) = 40分
项目2: 核心(20分) + 5人团队(0分) = 20分
────────────────────────────────────────
总分: 60分 → min(60, 25) = 25分 (达到上限)
```

**代码位置**: [project_analyzer.py:145-165](tools/analysis/project_analyzer.py#L145-L165)

---

### 3. 技术深度 (25分)

**配置位置**: [config/scoring.yaml](config/scoring.yaml#L257-L262)

#### 3.1 技术栈加分

```yaml
project_tech_stack_score_per_tech: 3           # 每个技术3分
project_tech_stack_max_score_per_project: 10    # 每个项目最高10分
```

**计算公式**:
```
技术栈加分 = min(技术数量 × 3, 10)
```

**示例**:
- 1个技术: 1 × 3 = **3分**
- 2个技术: 2 × 3 = **6分**
- 3个技术: 3 × 3 = **9分**
- 4个及以上: **10分** (上限)

#### 3.2 复杂度指标加分

```yaml
project_complexity_bonus:
  has_high_concurrency: 15  # 高并发
  distributed_system: 15    # 分布式系统
  high_availability: 15     # 高可用
  large_team: 10           # 大型团队
```

**complexity_indicators 格式**:
```json
{
  "has_high_concurrency": true,
  "distributed_system": true
}
```

**计算公式**:
```
技术深度得分 = sum(每个项目的技术栈加分 + 复杂度加分)
最高25分（单项目复杂度最高15分）
```

**示例**:
```
项目1: 技术栈10分 + 高并发15分 + 分布式15分 = 40分
项目2: 技术栈6分 + 高并发15分 = 21分
──────────────────────────────────────────
总分: 61分 → min(61, 25) = 25分 (达到上限)
```

**代码位置**: [project_analyzer.py:167-183](tools/analysis/project_analyzer.py#L167-L183)

---

### 4. 业务价值 (25分)

**配置位置**: [config/scoring.yaml](config/scoring.yaml#L265-L266)

```yaml
project_achievement_score_per_item: 5           # 每个成就5分
project_achievement_max_score_per_project: 25    # 每个项目最高25分
```

**计算公式**:
```
业务价值得分 = sum(每个项目的成就数量 × 5)
最高25分
```

**示例**:
```
项目1: 3个成就 × 5 = 15分
项目2: 2个成就 × 5 = 10分
项目3: 4个成就 × 5 = 20分
──────────────────────────
总分: 45分 → min(45, 25) = 25分 (达到上限)
```

**代码位置**: [project_analyzer.py:185-193](tools/analysis/project_analyzer.py#L185-L193)

---

## 完整计算示例

### 示例: 优秀候选人

**项目数据**:
```json
[
  {
    "name": "电商系统",
    "role": "项目负责人",
    "team_size": 20,
    "tech_stack": ["Python", "Django", "MySQL", "Redis", "Docker"],
    "achievements": ["性能提升50%", "用户增长30%", "转化率提升25%"],
    "complexity_indicators": {
      "has_high_concurrency": true,
      "distributed_system": true
    }
  },
  {
    "name": "推荐系统",
    "role": "核心开发",
    "team_size": 8,
    "tech_stack": ["Python", "TensorFlow", "MySQL"],
    "achievements": ["准确率提升20%"],
    "complexity_indicators": {}
  }
]
```

**计算过程**:

#### 1. 项目数量 (25分)
```
2个项目 × 10分 = 20分
```

#### 2. 项目质量 (25分)
```
项目1: 负责人(30) + 20人团队(10) = 40分
项目2: 核心(20) + 8人团队(0) = 20分
────────────────────────────────
总分: 60分 → min(60, 25) = 25分 (封顶)
```

#### 3. 技术深度 (25分)
```
项目1: 技术栈5×3=15(封顶10) + 高并发15 + 分布式15 = 40分
项目2: 技术栈3×3=9 + 无复杂度 = 9分
────────────────────────────────────────
总分: 49分 → min(49, 25) = 25分 (封顶)
```

#### 4. 业务价值 (25分)
```
项目1: 3个成就 × 5 = 15分
项目2: 1个成就 × 5 = 5分
──────────────────────────
总分: 20分
```

#### 项目经验总分
```
项目数量: 20分
项目质量: 25分
技术深度: 25分
业务价值: 20分
───────────────
总分: 90/100分
```

---

## 配置调整示例

### 示例1: 提高负责人角色权重

```yaml
project_role_bonus:
  负责人: 40  # 原30分 → 40分
  主导: 35   # 原25分 → 35分
```

**效果**:
- 1个负责人项目: 40分 (达到上限25分)
- 负责人项目更容易获得满分

---

### 示例2: 重视技术深度

```yaml
project_tech_stack_score_per_tech: 5  # 原3分 → 5分
project_tech_stack_max_score_per_project: 15  # 原10分 → 15分

project_complexity_bonus:
  distributed_system: 20  # 原15分 → 20分
  has_high_concurrency: 20  # 原15分 → 20分
```

**效果**:
- 3个技术栈: 3 × 5 = 15分
- 高并发+分布式: 20 + 20 = 40分
- 技术深度得分显著提升

---

## 维度最高分限制

**配置位置**: [config/scoring.yaml](config/scoring.yaml#L268-L273)

```yaml
project_dimension_max_scores:
  count: 25               # 项目数量最高25分
  quality: 25             # 项目质量最高25分
  tech_depth: 25          # 技术深度最高25分
  business_value: 25      # 业务价值最高25分
  complexity_per_project: 15  # 单个项目复杂度最高15分
```

**说明**: 每个子维度都有最高分限制，确保总分不超过100分。

---

## 代码实现

**计算流程**: [project_analyzer.py:112-143](tools/analysis/project_analyzer.py#L112-L143)

```python
def _calculate_total_score(self, projects):
    """计算总分"""
    if not projects:
        return 0.0

    # 计算各子维度得分
    detail_scores = self._calculate_detail_scores(projects)

    # 总分 = 各子维度得分之和（最高100分）
    total = sum(detail_scores.values())
    return round(min(total, 100), 2)
```

---

## 常见问题

### Q1: 为什么单个项目可以超过25分？

**A**: 因为是累加计算多个项目的得分，然后应用维度上限。

**示例**:
```
项目1: 负责人(30) + 大团队(10) = 40分
项目2: 核心(20) + 小团队(0) = 20分
────────────────────────────────
总分: 60分 → min(60, 25) = 25分 (应用维度上限)
```

### Q2: 如何让项目质量达到满分？

**A**: 至少需要以下之一：
- 1个负责人项目 + 大团队(≥20人)
- 1个负责人项目 + 1个核心项目
- 2个核心项目 + 团队规模加分

### Q3: 技术深度为什么容易满分？

**A**: 因为技术栈和复杂度都加分：
- 4个技术 = 12分
- 高并发 + 分布式 = 30分
- 单项目即可达42分，远超25分上限

### Q4: 业务价值如何提高？

**A**: 需要量化成果：
```
每项成就: 5分
5项成就: 5 × 5 = 25分 (满分)
```

**成就示例**:
- 性能提升50%
- 用户增长30%
- 转化率提升25%
- 系统稳定性提升
- 成本降低20%

---

## 相关文档

- [项目经验配置指南](docs/PROJECT_CONFIG_GUIDE.md)
- [项目经验评分标准](PROJECT_SCORING_STANDARD.md)
- [项目经验v2.0更新说明](docs/PROJECT_V2.0_UPDATE.md)
- [配置文件](config/scoring.yaml)
