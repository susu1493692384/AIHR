# 经验背景评分实现详解

## 版本信息
- **版本**: v1.0
- **更新日期**: 2026-01-30
- **核心文件**: [tools/analysis/experience_analyzer.py](../tools/analysis/experience_analyzer.py)

---

## 评分结构总览

**总分 = 100分**

| 维度 | 权重 | 最高分 | 说明 |
|------|------|--------|------|
| **教育背景** | 30% | 30分 | 学历层次 + 学校层次 |
| **工作经验** | 60% | 60分 | 年限 + 公司质量 + 职位级别 + 职业发展 |
| **实习经验** | 10% | 10分 | 实习质量 + 实习时长 |

---

## 一、教育背景评分（30分）

### 1.1 学历层次（20分）

| 学历 | 得分 | 说明 |
|------|------|------|
| 博士 | 20分 | 最高学历 |
| 硕士 | 15分 | 研究生学历 |
| 本科 | 10分 | 本科学历 |
| 大专 | 5分 | 专科/高职学历 |

**代码位置**: [experience_analyzer.py:252-275](../tools/analysis/experience_analyzer.py#L252-L275)

**评分规则**：
- 取最高学历计算
- 支持中英文名称匹配
- 模糊匹配（如"ph.d"匹配"博士"）

**示例**：
```python
# 最高学历
highest_edu = Education(degree="硕士", school="清华大学")

# 计算得分
degree_score = calculate_degree_score("硕士")  # 15分
```

### 1.2 学校层次（10分）

| 学校类型 | 得分 | 说明 |
|----------|------|------|
| 985/双一流 | 10分 | 顶尖高校 |
| 211 | 7分 | 重点高校 |
| 普通本科 | 5分 | 一般高校 |
| 其他 | 0分 | 不符合要求 |

**代码位置**: [experience_analyzer.py:277-297](../tools/analysis/experience_analyzer.py#L277-L297)

**学校分级配置**（config/scoring.yaml）：
```yaml
school_tier:
  985:
    - 清华大学
    - 北京大学
    - 复旦大学
    # ...
  211:
    - 北京理工大学
    - 北京航空航天大学
    # ...
```

**判断逻辑**：
```python
# 使用配置文件判断学校层次
tier = config.get_school_tier(school_name)
# tier 可能是 "985", "211", "普通"
```

---

## 二、工作经验评分（60分）

### 2.1 工作年限（20分）

**公式**：
```
年限得分 = 总工作月数 / 12 × 4
最高分 = 20分（即5年以上工作经验）
```

**代码位置**: [experience_analyzer.py:318-320](../tools/analysis/experience_analyzer.py#L318-L320)

**示例**：
- 1年（12月）：12 / 12 × 4 = 4分
- 3年（36月）：36 / 12 × 4 = 12分
- 5年（60月）：60 / 12 × 4 = 20分（满分）
- 10年（120月）：120 / 12 × 4 = 40分 → 限制为20分

**注意**：
- 不包括实习经历
- 多段工作经历累加计算

### 2.2 公司质量（15分）

**公司规模加分**：

| 规模 | 加分 | 说明 |
|------|------|------|
| 10000+人 | 8分/家 | 超大型公司 |
| 1000-9999人 | 6分/家 | 大型公司 |
| 100-999人 | 4分/家 | 中型公司 |
| 10-99人 | 2分/家 | 小型公司 |
| 未指定 | 2分/家 | 默认得分 |

**代码位置**: [experience_analyzer.py:424-442](../tools/analysis/experience_analyzer.py#L424-L442)

**计算公式**：
```
公司质量得分 = Σ(每家公司的规模加分)
最高分 = 15分
```

**示例**：
- 在阿里巴巴（10000+人）工作：8分
- 在初创公司（50人）工作：2分（默认）
- 总分：min(8 + 2, 15) = 10分

**配置来源**（config/scoring.yaml）：
```yaml
company_scale_bonus:
  "10000+": 8
  "1000-9999": 6
  "100-999": 4
  "10-99": 2
```

### 2.3 职位级别（15分）

**职位加分**：

| 职位级别 | 加分 | 说明 |
|----------|------|------|
| 总监/经理 | 15分/个 | 高级管理 |
| 主管 | 12分/个 | 中级管理 |
| 高级/资深 | 10分/个 | 高级技术 |
| Lead/负责人 | 8分/个 | 技术负责人 |
| 其他 | 0分 | 普通员工 |

**代码位置**: [experience_analyzer.py:444-470](../tools/analysis/experience_analyzer.py#L444-L470)

**计算公式**：
```
职位级别得分 = Σ(每个职位的加分)
最高分 = 15分
```

**示例**：
- 职位1：高级Java工程师 → 10分
- 职位2：技术Lead → 8分
- 总分：min(10 + 8, 15) = 15分（已满）

**匹配规则**：
- 精确匹配：职位名称完全包含关键词
- 支持中英文：高级/senior, 经理/manager

**配置来源**（config/scoring.yaml）：
```yaml
position_bonus:
  总监: 15
  经理: 15
  主管: 12
  高级: 10
  资深: 10
  lead: 8
  负责人: 8
```

### 2.4 职业发展（10分）

**评分标准**：

| 发展情况 | 得分 | 说明 |
|----------|------|------|
| 职位晋升 | 10分 | 职位明显提升 |
| 平稳发展 | 5分 | 职位平稳或小幅提升 |
| 停滞/下降 | 0分 | 职位下降或长期不变 |

**代码位置**: [experience_analyzer.py:472-520](../tools/analysis/experience_analyzer.py#L472-L520)

**判断逻辑**：
```python
# 计算职位级别的变化
position_levels = [exp.position_level for exp in work_experience]

# 检查是否有晋升趋势
if has_promotion(position_levels):
    score = 10
elif has_growth(position_levels):
    score = 5
else:
    score = 0
```

**职位级别映射**：
```python
POSITION_LEVEL_MAP = {
    # 高级管理
    "总监", "经理", "director", "manager": 5,
    # 中级管理
    "主管", "lead", "supervisor", "head": 4,
    # 高级技术
    "高级", "资深", "senior", "principal": 3,
    # 中级技术
    "工程师", "developer", "工程师": 2,
    # 初级
    "助理", "assistant", "初级": 1,
}
```

---

## 三、实习经验评分（10分）

### 3.1 实习识别规则

**判断标准**（满足任一即视为实习）：
1. 职位名称包含"实习"或"intern"
2. 工作时长小于6个月

**代码位置**: [experience_analyzer.py:135-165](../tools/analysis/experience_analyzer.py#L135-L165)

```python
def _separate_internships_and_work(self, work_history):
    """分离实习经历和工作经历"""
    internships = []
    work = []

    for exp in work_history:
        is_internship = (
            "实习" in exp.position.lower() or
            "intern" in exp.position.lower() or
            self._calculate_experience_months(exp) < 6
        )

        if is_internship:
            internships.append(exp)
        else:
            work.append(exp)

    return internships, work
```

### 3.2 实习质量（6分）

**公司规模加分**：

| 规模 | 加分 | 说明 |
|------|------|------|
| 10000+人 | 6分/家 | 大厂实习 |
| 1000-9999人 | 4分/家 | 知名公司 |
| 100-999人 | 2分/家 | 中型公司 |
| 10-99人 | 1分/家 | 小型公司 |
| 未指定 | 1分/家 | 默认 |

**代码位置**: [experience_analyzer.py:364-379](../tools/analysis/experience_analyzer.py#L364-L379)

**示例**：
- 在字节跳动（10000+人）实习：6分
- 在小公司实习：1分
- 总分：min(6 + 1, 6) = 6分（已满）

**配置来源**（config/scoring.yaml）：
```yaml
internship_company_bonus:
  "10000+": 6
  "1000-9999": 4
  "100-999": 2
  "10-99": 1
```

### 3.3 实习时长（4分）

**公式**：
```
实习时长得分 = 总实习月数 / 3 × 1
最高分 = 4分（即12个月以上）
```

**代码位置**: [experience_analyzer.py:381-389](../tools/analysis/experience_analyzer.py#L381-L389)

**示例**：
- 3个月实习：3 / 3 × 1 = 1分
- 6个月实习：6 / 3 × 1 = 2分
- 12个月实习：12 / 3 × 1 = 4分（满分）
- 18个月实习：18 / 3 × 1 = 6分 → 限制为4分

---

## 完整计算示例

### 示例候选人

**教育背景**：
- 硕士学历（15分）
- 清华大学（985，10分）
- 小计：25分

**工作经验**：
- 工作年限：3年（12分）
- 公司质量：阿里巴巴（8分）+ 中型公司（4分）= 12分（限制为15分）
- 职位级别：高级Java工程师（10分）+ 技术Lead（8分）= 15分（已满）
- 职业发展：有明显晋升（10分）
- 小计：12 + 15 + 10 + 10 = 47分

**实习经验**：
- 实习质量：字节跳动实习（6分）
- 实习时长：6个月（2分）
- 小计：8分

**总分**：
```
总分 = 教育背景(25) + 工作经验(47) + 实习经验(8)
     = 80分
```

---

## 配置文件

### config/scoring.yaml

```yaml
# 经验背景维度权重
experience_dimension_weights:
  education: 0.30    # 教育背景 30%
  work: 0.70         # 工作经验 70%
  internship: 0      # 实习经验 0%

# 学历层次加分
degree_scores:
  博士: 20
  硕士: 15
  本科: 10
  大专: 5

# 学校层次加分
school_tier_scores:
  "985": 10
  "211": 7
  普通: 5

# 职位级别加分
position_bonus:
  总监: 15
  经理: 15
  主管: 12
  高级: 10
  资深: 10
  lead: 8
  负责人: 8

# 公司规模加分
company_scale_bonus:
  "10000+": 8
  "1000-9999": 6
  "100-999": 4
  "10-99": 2

# 实习公司加分
internship_company_bonus:
  "10000+": 6
  "1000-9999": 4
  "100-999": 2
  "10-99": 1
```

---

## 代码实现要点

### 1. 默认配置机制

当配置文件中缺少某些配置时，使用硬编码的默认值：

**代码位置**: [experience_analyzer.py:21-51](../tools/analysis/experience_analyzer.py#L21-L51)

```python
# 默认配置
DEFAULT_POSITION_BONUS = {
    "总监": 15, "经理": 15, "主管": 12,
    "高级": 10, "资深": 10, "lead": 8, "负责人": 8,
}

DEFAULT_COMPANY_SCALE_BONUS = {
    "10000+": 8, "1000-9999": 6, "100-999": 4, "10-99": 2,
}

# 使用配置或默认值
self.position_bonus = (
    self.config.position_bonus
    if self.config.position_bonus
    else self.DEFAULT_POSITION_BONUS
)
```

### 2. 经历分离

自动识别实习和工作经历：

**判断标准**：
- 职位名称包含"实习"或"intern"
- 时长小于6个月

**示例**：
```python
# 会被识别为实习
"软件工程师实习生"  # 包含"实习"
"Intern Developer"   # 包含"intern"
"开发助理"（3个月） # 时长<6个月

# 会被识别为工作
"软件工程师"        # 正常职位
"Java开发"（12个月）  # 时长≥6个月
```

### 3. 时间计算

**月数计算公式**：
```python
months = (end_year - start_year) * 12 + (end_month - start_month)
```

**处理"至今"**：
```python
if exp.end_time == "至今":
    end_year = datetime.now().year
    end_month = datetime.now().month
```

---

## 评分特点

### 优势

✅ **多维度评估**
- 不仅看学历，还看工作经验
- 不仅看年限，还看公司质量和职位发展

✅ **突出大厂经验**
- 大公司（10000+人）加分显著
- 鼓励在知名企业工作

✅ **重视职业发展**
- 职位晋升有额外加分
- 鼓励持续成长

✅ **配置灵活**
- 所有评分标准可配置
- 支持不同岗位的差异化配置

### 适用场景

| 场景 | 适用性 | 说明 |
|------|--------|------|
| **校招** | ✅ 适用 | 看重教育背景 + 实习经验 |
| **社招（初级）** | ✅ 适用 | 工作年限权重较高 |
| **社招（高级）** | ✅ 适用 | 职位级别 + 职业发展重要 |
| **技术专家** | ⚠️ 一般 | 经验背景权重低，技术能力更重要 |

---

## 常见问题

### Q1: 博士和硕士的分数差距为什么只有5分？

**A**:
- 博士：20分
- 硕士：15分
- 差距：5分

设计考虑：
- 在工作中，实际能力比学历更重要
- 博士和硕士在实际工作中差异不大
- 避免过度强调学历而忽视实战能力

### Q2: 为什么实习经验只占10%？

**A**:
- 实习是短期经历，含金量不如正式工作
- 主要用于校招评估
- 社招时，实习经验权重自动降低

### Q3: 如何调整评分标准？

**A**: 修改 config/scoring.yaml：

```yaml
# 提高学历权重
degree_scores:
  博士: 30  # 从20提高到30
  硕士: 25  # 从15提高到25

# 提高大公司加分
company_scale_bonus:
  "10000+": 15  # 从8提高到15
```

---

## 相关文档

- [配置文件说明](../config/scoring.yaml)
- [数据模型定义](../core/models.py)
- [前端显示更新](FRONTEND_V3.1_UPDATE.md)

---

**更新日期**: 2026-01-30
**文档版本**: v1.0
**维护者**: System
