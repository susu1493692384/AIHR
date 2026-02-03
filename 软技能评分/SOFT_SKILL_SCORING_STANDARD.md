# 软技能评分标准

## 概述

**文件位置**: [tools/analysis/soft_skill_analyzer.py](../tools/analysis/soft_skill_analyzer.py)

**权重**: 15%（在总分中）

**评分方法**: 关键词匹配 + 简单累加

---

## 评分结构

软技能总分（0-100分）= 覆盖面得分 + 团队协作得分 + 领导力得分 + 沟通能力得分

每个子维度最高 25 分

### 子维度说明

| 子维度 | 最高分 | 评分方式 |
|--------|--------|----------|
| 覆盖面 | 25分 | 每找到一个软技能类别 +5分 |
| 团队协作 | 25分 | 每个关键词 +10分 |
| 领导力 | 25分 | 每个关键词 +10分 |
| 沟通能力 | 25分 | 每个关键词 +10分 |

---

## 评分规则详解

### 1. 覆盖面得分（0-25分）

**计算方式**:
```python
skill_count = len(found_skills)  # 找到的软技能类别数量
coverage_score = min(skill_count * 5, 25)  # 每个类别 +5分，最高25分
```

**软技能类别**（共7类）:
1. 团队协作
2. 领导力
3. 沟通能力
4. 学习能力
5. 问题解决
6. 创新
7. 抗压

**示例**:
- 找到 1 个类别: 1 × 5 = **5分**
- 找到 3 个类别: 3 × 5 = **15分**
- 找到 5 个类别: 5 × 5 = **25分**（达到最高分）

### 2. 团队协作得分（0-25分）

**关键词**: ["团队", "协作", "配合", "沟通"]

**计算方式**:
```python
teamwork_count = sum(1 for kw in keywords if kw in text)
teamwork_score = min(teamwork_count * 10, 25)  # 每个关键词 +10分
```

**示例**:
- 包含"团队": 1 × 10 = **10分**
- 包含"团队"、"协作": 2 × 10 = **20分**
- 包含3个以上关键词: **25分**（达到最高分）

### 3. 领导力得分（0-25分）

**关键词**: ["领导", "管理", "带领", "负责", "主管"]

**计算方式**:
```python
leadership_count = sum(1 for kw in keywords if kw in text)
leadership_score = min(leadership_count * 10, 25)
```

**示例**:
- 包含"带领": 1 × 10 = **10分**
- 包含"领导"、"管理": 2 × 10 = **20分**
- 包含3个以上关键词: **25分**（达到最高分）

### 4. 沟通能力得分（0-25分）

**关键词**: ["沟通", "交流", "表达", "协调"]

**计算方式**:
```python
communication_count = sum(1 for kw in keywords if kw in text)
communication_score = min(communication_count * 10, 25)
```

**示例**:
- 包含"沟通": 1 × 10 = **10分**
- 包含"沟通"、"表达": 2 × 10 = **20分**
- 包含3个以上关键词: **25分**（达到最高分）

---

## 关键词列表

### 完整关键词映射

```python
SOFT_SKILL_KEYWORDS = {
    "团队协作": ["团队", "协作", "配合", "沟通"],
    "领导力": ["领导", "管理", "带领", "负责", "主管"],
    "沟通能力": ["沟通", "交流", "表达", "协调"],
    "学习能力": ["学习", "掌握", "研究", "探索"],
    "问题解决": ["解决", "优化", "改进", "处理"],
    "创新": ["创新", "改进", "优化", "提出"],
    "抗压": ["压力", "挑战", "应对", "克服"],
}
```

### 关键词重复说明

**注意**: 不同类别之间有关键词重叠，会影响多个维度的评分：

| 关键词 | 影响的维度 |
|--------|-----------|
| 沟通 | 团队协作、沟通能力 |
| 协作 | 团队协作 |
| 配合 | 团队协作 |
| 交流 | 沟通能力 |
| 表达 | 沟通能力 |
| 协调 | 沟通能力 |
| 负责 | 领导力 |
| 改进 | 问题解决、创新 |
| 优化 | 问题解决、创新 |

---

## 评分计算流程

### 代码位置

[soft_skill_analyzer.py](../tools/analysis/soft_skill_analyzer.py:34-79)

### 计算步骤

```python
def analyze(self, resume: CleanedResume) -> AnalysisResult:
    """分析软技能"""
    # 1. 提取所有文本
    all_text = self._extract_all_text(resume)

    # 2. 计算分项得分
    detail_scores = self._calculate_detail_scores(all_text)

    # 3. 计算总分（简单相加）
    total_score = self._calculate_total_score(all_text)

    return AnalysisResult(
        dimension="soft_skill",
        score=total_score,
        detail_scores=detail_scores,
        ...
    )
```

### 文本提取范围

```python
def _extract_all_text(self, resume: CleanedResume) -> str:
    """提取所有文本"""
    parts = []

    # 1. 个人信息（姓名）
    if resume.cleaned_data.personal_info:
        parts.append(resume.cleaned_data.personal_info.name or "")

    # 2. 工作经历描述 + 成就
    for exp in resume.cleaned_data.work_experience:
        if exp.description:
            parts.append(exp.description)
        if exp.achievements:
            parts.extend(exp.achievements)

    # 3. 项目描述 + 成就
    for proj in resume.cleaned_data.projects:
        if proj.description:
            parts.append(proj.description)
        if proj.achievements:
            parts.extend(proj.achievements)

    return " ".join(parts)  # 拼接所有文本
```

---

## 评分示例

### 示例1: 基础候选人

**简历内容**:
```
工作经历：
- 负责后端开发
- 完成系统优化

项目经验：
- 参与团队开发
- 学习新技术
```

**评分计算**:

1. **覆盖面得分**
   - 找到类别: 领导力、团队协作、学习能力 (3个)
   - 得分: 3 × 5 = **15分**

2. **团队协作得分**
   - 关键词: "团队" (1个)
   - 得分: 1 × 10 = **10分**

3. **领导力得分**
   - 关键词: "负责" (1个)
   - 得分: 1 × 10 = **10分**

4. **沟通能力得分**
   - 关键词: 无
   - 得分: **0分**

**总分**: 15 + 10 + 10 + 0 = **35分**

### 示例2: 优秀候选人

**简历内容**:
```
工作经历：
- 负责团队管理，带领5人团队完成项目
- 与产品经理沟通需求，协调各方资源
- 解决系统性能问题，优化查询速度

项目经验：
- 主导技术架构设计，创新性提出解决方案
- 团队协作完成开发，确保项目按时交付
- 学习前沿技术，提升团队技术水平
- 应对高压工作环境，克服技术难题
```

**评分计算**:

1. **覆盖面得分**
   - 找到类别: 领导力、沟通能力、问题解决、创新、团队协作、学习能力、抗压 (7个)
   - 得分: 7 × 5 = **25分**（已达最高）

2. **团队协作得分**
   - 关键词: "团队"、"协作" (2个)
   - 得分: 2 × 10 = **20分**

3. **领导力得分**
   - 关键词: "负责"、"带领"、"主导" (3个)
   - 得分: 3 × 10 = **25分**（已达最高）

4. **沟通能力得分**
   - 关键词: "沟通"、"协调" (2个)
   - 得分: 2 × 10 = **20分**

**总分**: 25 + 20 + 25 + 20 = **90分**

---

## 代码结构

### 类定义

```python
class SoftSkillAnalyzer(BaseAnalyzer):
    """软技能分析器"""

    # 软技能关键词（硬编码）
    SOFT_SKILL_KEYWORDS = {
        "团队协作": ["团队", "协作", "配合", "沟通"],
        "领导力": ["领导", "管理", "带领", "负责", "主管"],
        "沟通能力": ["沟通", "交流", "表达", "协调"],
        "学习能力": ["学习", "掌握", "研究", "探索"],
        "问题解决": ["解决", "优化", "改进", "处理"],
        "创新": ["创新", "改进", "优化", "提出"],
        "抗压": ["压力", "挑战", "应对", "克服"],
    }

    def __init__(self, config: ScoreConfig = None):
        super().__init__(config)
        self.dimension_name = "soft_skill"
        self.weight = self.config.weights.get("soft_skill", 0.15)  # 15%
```

### 主要方法

| 方法 | 功能 | 代码行数 |
|------|------|---------|
| `analyze()` | 主分析方法，协调整个评分流程 | 34-49 |
| `_calculate_detail_scores()` | 计算各子维度得分 | 51-73 |
| `_calculate_total_score()` | 计算总分（简单相加） | 75-79 |
| `_found_skills()` | 查找文本中出现的软技能类别 | 81-87 |
| `_calculate_category_score()` | 计算某个类别的得分 | 89-93 |
| `_extract_all_text()` | 提取简历所有文本 | 95-117 |
| `_extract_insights()` | 提取关键发现 | 119-130 |
| `_extract_highlights()` | 提取亮点 | 132-148 |
| `_extract_weaknesses()` | 提取不足 | 150-164 |

---

## 特点分析

### 优点

1. **简单直接**: 关键词匹配，计算快速
2. **可解释性强**: 每个得分都有明确的来源
3. **易于理解**: 评分规则清晰明了

### 局限性

1. **硬编码关键词**: 关键词列表固定，无法配置
2. **简单匹配**: 只检查关键词是否存在，不考虑上下文
3. **重复加分**: 同一个关键词可能被多个维度计算
4. **缺少权重**: 各子维度权重相同，没有区分重要性
5. **上限较低**: 简单累加方式，难以达到高分

### 与其他维度对比

| 维度 | 评分方式 | 配置化 | 子维度加权 |
|------|---------|--------|-----------|
| 技术能力 | 按类别加权 | ✅ | ✅ |
| 经验背景 | 子维度加权 | ✅ | ✅ |
| 项目经验 | 子维度加权 | ✅ | ✅ |
| 软技能 | 简单累加 | ❌ | ❌ |

---

## 配置化改造建议

### 短期改进

将关键词移到配置文件：

```yaml
# config/scoring.yaml

soft_skill_keywords:
  teamwork: ["团队", "协作", "配合"]
  leadership: ["领导", "管理", "带领"]
  communication: ["沟通", "交流", "表达"]
  learning: ["学习", "掌握", "研究"]
  problem_solving: ["解决", "优化", "改进"]
  innovation: ["创新", "提出"]
  resilience: ["压力", "挑战", "应对"]

soft_skill_dimension_weights:
  coverage: 0.20      # 覆盖面 20%
  teamwork: 0.30      # 团队协作 30%
  leadership: 0.25    # 领导力 25%
  communication: 0.25 # 沟通能力 25%
```

### 长期优化

1. **使用 LLM 分析**: 利用 LLM 理解上下文，提取软技能表现
2. **证据引用**: 标注关键词出现的具体位置
3. **评分等级**: 根据关键词数量和质量分级评分
4. **去重机制**: 避免同一关键词被多次计算

---

## 总结

**软技能评分**目前采用**关键词匹配 + 简单累加**的方式：

- ✅ 优点: 简单、快速、可解释
- ⚠️ 缺点: 硬编码、简单匹配、上限低

**代码位置**: [tools/analysis/soft_skill_analyzer.py](../tools/analysis/soft_skill_analyzer.py)

**改进方向**: 配置化 → 子维度加权 → LLM 智能分析
