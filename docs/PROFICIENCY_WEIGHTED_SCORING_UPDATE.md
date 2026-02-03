# 技术能力评分系统更新 - 熟练度加权平均

## 更新日期
2026-01-30

## 更新概述

根据用户需求 **"重新设计一下技术能力的评分，直接是分数=技能等级评分的平均分，权重按熟练度来算"**，我们对技术能力评分系统进行了全面重新设计。

**核心变化**：
- ❌ 移除了复杂的行业检测和类别加权系统
- ✅ 采用简洁的熟练度加权平均算法
- ✅ 简化了配置和维护
- ✅ 提高了评分的透明度和可解释性

---

## 新的评分系统

### 1. 技能等级评分

| 等级 | 基础分 | 说明 |
|------|--------|------|
| 精通 | 80分 | 核心技能，权重最高 |
| 熟练 | 60分 | 主要技能 |
| 熟悉 | 40分 | 可用技能 |
| 了解 | 20分 | 入门技能 |

### 2. 熟练度权重

| 等级 | 权重 | 说明 |
|------|------|------|
| 精通 | 1.5 | 核心技能，最重要 |
| 熟练 | 1.0 | 主要技能，标准参考 |
| 熟悉 | 0.7 | 可用技能，重要性较低 |
| 了解 | 0.5 | 入门技能，重要性最低 |

### 3. 计算公式

```
加权总分 = Σ(技能等级分 × 熟练度权重)
权重总和 = Σ(熟练度权重)
加权平均分 = 加权总分 / 权重总和
最终得分 = (加权平均分 / 满分80) × 100
```

### 4. 计算示例

假设候选人有以下技能：

| 技能 | 等级 | 等级分 | 权重 | 加权分 |
|------|------|--------|------|--------|
| Python | 精通 | 80 | 1.5 | 120 |
| Java | 精通 | 80 | 1.5 | 120 |
| Spring Boot | 熟练 | 60 | 1.0 | 60 |
| MySQL | 熟练 | 60 | 1.0 | 60 |
| React | 熟悉 | 40 | 0.7 | 28 |
| Redis | 熟悉 | 40 | 0.7 | 28 |
| Docker | 了解 | 20 | 0.5 | 10 |
| Kubernetes | 了解 | 20 | 0.5 | 10 |
| **总计** | - | - | **7.4** | **436** |

计算过程：
```
加权平均分 = 436 / 7.4 = 58.92
最终得分 = (58.92 / 80) × 100 = 73.65分
```

---

## 代码修改

### 1. TechnicalAnalyzer 类更新

**文件**: [tools/analysis/technical_analyzer.py](tools/analysis/technical_analyzer.py)

#### 修改1: 更新技能等级评分

```python
# 修改前
LEVEL_SCORES = {
    "精通": 40,  # ❌ 旧值
    "熟练": 30,
    "熟悉": 20,
    "了解": 10,
}

# 修改后
LEVEL_SCORES = {
    "精通": 80,  # ✅ 新值（翻倍）
    "熟练": 60,
    "熟悉": 40,
    "了解": 20,
}
```

#### 修改2: 添加熟练度权重

```python
# 新增
LEVEL_WEIGHTS = {
    "精通": 1.5,  # 核心技能，权重最高
    "熟练": 1.0,  # 主要技能
    "熟悉": 0.7,  # 可用技能
    "了解": 0.5,  # 入门技能
}
```

#### 修改3: 简化 `__init__` 方法

```python
# 修改前
def __init__(self, config: ScoreConfig = None, llm=None, enable_llm_analysis: bool = False):
    super().__init__(config)
    self.dimension_name = "technical"
    self.weight = self.config.weights.get("technical", 0.25)
    # LLM分析器（已移除）
    self.llm = llm
    self.enable_llm_analysis = enable_llm_analysis and llm is not None
    self.llm_analyzer = None
    if self.enable_llm_analysis:
        self.llm_analyzer = LLMSkillAnalyzer(llm=llm)
    # 行业检测器（已移除）
    self.industry_detector = IndustryDetector(config)

# 修改后
def __init__(self, config: ScoreConfig = None):
    super().__init__(config)
    self.dimension_name = "technical"
    self.weight = self.config.weights.get("technical", 0.25)
```

#### 修改4: 简化 `analyze` 方法

```python
# 修改前
def analyze(self, resume: CleanedResume) -> AnalysisResult:
    # 1. 检测行业
    industry = self.industry_detector.detect_industry(resume)

    # 2. 计算类别权重
    category_weights = self.industry_detector.get_category_weights(industry)

    # 3. 计算总分（按类别加权）
    total_score, category_breakdown = self._calculate_total_score(skills, category_weights)

    # 4. LLM识别热门技术（已移除）
    if self.enable_llm_analysis:
        hot_skills = self.llm_analyzer.identify_hot_skills(...)
        insights = self.llm_analyzer.extract_insights(...)
        highlights = self.llm_analyzer.extract_highlights(...)
        weaknesses = self.llm_analyzer.extract_weaknesses(...)

    return AnalysisResult(
        dimension=self.dimension_name,
        score=total_score,
        raw_analysis={
            "industry": industry,
            "industry_name": industry_name,
            "category_breakdown": category_breakdown,
            "hot_skills": hot_skills
        }
    )

# 修改后
def analyze(self, resume: CleanedResume) -> AnalysisResult:
    skills = resume.cleaned_data.skills

    # 1. 计算展示维度（用于诊断分析）
    detail_scores = self._calculate_detail_scores(skills)

    # 2. 计算总分（按熟练度加权平均）
    total_score, skill_breakdown = self._calculate_total_score(skills)

    # 3. 提取关键发现（规则）
    insights = self._extract_insights(resume)

    # 4. 提取亮点（规则）
    highlights = self._extract_highlights(resume)

    # 5. 提取不足（规则）
    weaknesses = self._extract_weaknesses(resume)

    return AnalysisResult(
        dimension=self.dimension_name,
        score=total_score,
        detail_scores=detail_scores,
        insights=insights,
        highlights=highlights,
        weaknesses=weaknesses,
        raw_analysis={
            "skill_count": len(skills),
            "skill_breakdown": skill_breakdown
        }
    )
```

#### 修改5: 重写 `_calculate_total_score` 方法

```python
# 修改前（按类别加权）
def _calculate_total_score(self, skills: List[Skill], category_weights: Dict[str, float]) -> tuple[float, Dict]:
    # 按类别分组
    category_scores: Dict[str, List[float]] = {}
    for skill in skills:
        category = skill.category
        level_score = self.LEVEL_SCORES.get(skill.level, 40)
        if category not in category_scores:
            category_scores[category] = []
        category_scores[category].append(level_score)

    # 计算各类别加权得分
    total = 0.0
    total_weight = 0.0
    category_breakdown = {}

    for category, scores in category_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        weight = category_weights.get(category, 0.05)
        weighted_score = avg_score * weight
        total += weighted_score
        total_weight += weight

        category_breakdown[category] = {
            "name": category_names.get(category, category),
            "avg_score": round(avg_score, 2),
            "weight": weight,
            "weighted_score": round(weighted_score, 2),
            "skill_count": len(scores)
        }

    # 归一化到 0-100
    max_score = 80 * 1.0
    final_score = (total / max_score * 100) if max_score > 0 else 0
    return round(min(final_score, 100), 2), category_breakdown

# 修改后（按熟练度加权平均）
def _calculate_total_score(self, skills: List[Skill]) -> tuple[float, Dict]:
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
    max_score = 80
    final_score = (avg_weighted_score / max_score * 100) if max_score > 0 else 0

    return round(min(final_score, 100), 2), {
        "skills": skill_breakdown,
        "weighted_sum": round(weighted_sum, 2),
        "weight_sum": round(weight_sum, 2),
        "avg_weighted_score": round(avg_weighted_score, 2)
    }
```

#### 修改6: 移除未使用的导入

```python
# 修改前
from tools.analysis.industry_detector import IndustryDetector
from tools.analysis.llm_skill_analyzer import LLMSkillAnalyzer

# 修改后（已移除）
```

### 2. 前端显示更新

**文件**: [app/streamlit_app.py](app/streamlit_app.py)

#### 修改前：显示行业检测和类别加权

```python
# 显示检测到的行业信息
detected_industry = raw_analysis.get("industry", "unknown")
industry_name = raw_analysis.get("industry_name", "未知行业")
st.markdown(f"**🏷️ 检测到的行业**: {industry_name} ({detected_industry})")

# 显示类别加权计算
category_breakdown = raw_analysis.get("category_breakdown", {})
if category_breakdown:
    st.info(f"📌 以下显示【{industry_name}】行业技术能力总分的详细计算过程（按类别加权）")
    # 创建表格显示各类别的得分
    table_data = []
    for category_key, category_info in sorted_categories:
        table_data.append({
            "类别": category_info["name"],
            "平均分": f"{category_info['avg_score']:.1f}",
            "权重": f"{category_info['weight']:.0%}",
            "加权得分": f"{category_info['weighted_score']:.2f}",
            "技能数": category_info["skill_count"]
        })
```

#### 修改后：显示熟练度加权平均

```python
# 显示技术能力得分明细（按熟练度加权平均）
st.markdown("**总分计算方式（按熟练度加权平均）：**")

skill_breakdown = raw_analysis.get("skill_breakdown", {})
if skill_breakdown and "skills" in skill_breakdown:
    st.info("📌 以下显示技术能力总分的详细计算过程（按熟练度加权平均）")

    # 创建表格显示每个技能的得分
    table_data = []
    for skill_info in skill_breakdown["skills"]:
        table_data.append({
            "技能": skill_info["name"],
            "等级": skill_info["level"],
            "等级分": skill_info["level_score"],
            "权重": skill_info["weight"],
            "加权分": skill_info["weighted_score"]
        })

    # 显示计算公式
    weighted_sum = skill_breakdown.get("weighted_sum", 0)
    weight_sum = skill_breakdown.get("weight_sum", 0)
    avg_weighted_score = skill_breakdown.get("avg_weighted_score", 0)

    st.markdown(f"""
    **计算公式**：
    - 加权总分 = Σ(技能等级分 × 熟练度权重) = {weighted_sum:.2f}
    - 权重总和 = Σ(熟练度权重) = {weight_sum:.2f}
    - 加权平均分 = 加权总分 / 权重总和 = {avg_weighted_score:.2f}
    - 最终得分 = (加权平均分 / 满分80) × 100 = **{total_score:.1f}分**
    """)

    st.caption("""
    💡 **计算说明**：
    - **技能等级分**：精通80分、熟练60分、熟悉40分、了解20分
    - **熟练度权重**：精通1.5、熟练1.0、熟悉0.7、了解0.5
    - **加权分**：技能等级分 × 熟练度权重
    - **加权平均分**：所有技能的加权分之和 / 所有权重之和
    - **满分**：所有技能都是"精通"（80分）时的加权平均分 = 80分
    - **最终得分**：(加权平均分 / 80) × 100，归一化到0-100分范围

    🎯 **设计理念**：
    - 精通技能权重最高（1.5），体现核心竞争力
    - 熟练技能权重为1.0，作为主要技能参考
    - 熟悉和了解技能权重较低，避免过度拔高
    - 通过加权平均，客观反映技术能力水平
    """)
```

---

## 测试验证

### 测试文件

**文件**: [test/test_proficiency_weighted_scoring.py](test/test_proficiency_weighted_scoring.py)

### 测试结果

✅ **所有测试通过**

#### 测试1: 正常情况（混合技能）

- 输入：精通2、熟练2、熟悉2、了解2（共8个技能）
- 预期得分：73.65
- 实际得分：73.65
- ✅ 通过

#### 测试2: 无技能

- 输入：0个技能
- 预期得分：0
- 实际得分：0.0
- ✅ 通过

#### 测试3: 全精通（最高分）

- 输入：3个精通技能
- 预期得分：100
- 实际得分：100.0
- ✅ 通过

#### 测试4: 全了解（最低分）

- 输入：2个了解技能
- 预期得分：25.0
- 实际得分：25.0
- ✅ 通过

#### 测试5: 混合等级（1精通、1熟练、1熟悉、1了解）

- 输入：精通1、熟练1、熟悉1、了解1
- 预期得分：73.65
- 实际得分：73.65
- ✅ 通过

---

## 新旧系统对比

### 旧系统：按类别加权

**复杂度高**：
- ❌ 需要检测行业（IT、金融、HR等）
- ❌ 不同行业有不同的技能类别和权重
- ❌ 需要维护大量行业配置
- ❌ 配置错误会导致评分异常
- ❌ 用户难以理解为什么不同行业权重不同

**示例配置**（IT行业）：
```yaml
skill_categories:
  language: {name: "编程语言", weight: 0.35}
  framework: {name: "框架", weight: 0.25}
  database: {name: "数据库", weight: 0.20}
  tool: {name: "工具", weight: 0.15}
  other: {name: "其他", weight: 0.05}
```

### 新系统：按熟练度加权平均

**简洁高效**：
- ✅ 不需要检测行业
- ✅ 不需要维护类别权重配置
- ✅ 算法简单透明，易于理解
- ✅ 精通技能自然获得更高权重
- ✅ 符合直觉：精通比熟练更重要

**核心逻辑**：
```python
LEVEL_SCORES = {精通: 80, 熟练: 60, 熟悉: 40, 了解: 20}
LEVEL_WEIGHTS = {精通: 1.5, 熟练: 1.0, 熟悉: 0.7, 了解: 0.5}

# 计算加权平均
weighted_avg = Σ(等级分 × 权重) / Σ(权重)
final_score = (weighted_avg / 80) × 100
```

---

## 用户影响

### 正面影响

1. **评分更透明**：用户可以清楚看到每个技能如何影响总分
2. **配置更简单**：不需要维护复杂的行业配置
3. **系统更稳定**：减少了配置错误导致的问题
4. **算法更直观**：熟练度越高，对总分贡献越大（符合直觉）

### 潜在影响

1. **评分差异**：同一份简历在新旧系统下得分可能不同
   - 旧系统：精通技能在低权重类别中贡献较小
   - 新系统：精通技能始终获得1.5倍权重，贡献更大

2. **行业差异化消失**：
   - 旧系统：不同行业有不同权重（如IT更重视编程语言）
   - 新系统：所有行业使用统一的熟练度权重

---

## 向后兼容性

### 兼容性处理

虽然 `TechnicalAnalyzer` 的内部实现发生了重大变化，但对外接口保持兼容：

- ✅ `__init__(config)` 签名不变（只是移除了可选参数）
- ✅ `analyze(resume)` 方法签名不变
- ✅ 返回的 `AnalysisResult` 结构不变
- ✅ `score_breakdown` 中的 `technical` 分量仍然可用

### 需要更新的代码

如果其他代码依赖于 `raw_analysis` 中的特定字段，需要更新：

```python
# 旧代码
industry = result.raw_analysis.get("industry")
category_breakdown = result.raw_analysis.get("category_breakdown")

# 新代码
skill_breakdown = result.raw_analysis.get("skill_breakdown")
```

---

## 迁移指南

### 对于开发者

1. **更新导入**（如果直接使用了 `IndustryDetector` 或 `LLMSkillAnalyzer`）：
   ```python
   # 删除这些导入
   from tools.analysis.industry_detector import IndustryDetector
   from tools.analysis.llm_skill_analyzer import LLMSkillAnalyzer
   ```

2. **更新 `TechnicalAnalyzer` 初始化**：
   ```python
   # 旧代码
   analyzer = TechnicalAnalyzer(config, llm=llm, enable_llm_analysis=True)

   # 新代码
   analyzer = TechnicalAnalyzer(config)
   ```

3. **更新数据访问**：
   ```python
   # 旧代码
   industry = result.raw_analysis.get("industry")
   category_breakdown = result.raw_analysis.get("category_breakdown")

   # 新代码
   skill_breakdown = result.raw_analysis.get("skill_breakdown")
   ```

### 对于配置管理员

可以删除以下配置（如果不再需要）：

```yaml
# config/scoring.yaml
industry_detection:  # ❌ 不再需要
  it:
    position_keywords: [...]
    skill_categories: {...}

  finance:  # ❌ 不再需要
    position_keywords: [...]
    skill_categories: {...}

  # 其他行业配置...
```

---

## 设计理念

### 为什么选择熟练度加权平均？

1. **符合直觉**：技能越熟练，对能力的贡献越大
2. **突出核心竞争力**：精通技能获得1.5倍权重，鼓励深度学习
3. **简化系统**：不需要复杂的行业检测和配置
4. **透明可解释**：每个技能的贡献一目了然
5. **行业无关**：适用于所有行业，不需要定制

### 权重设计依据

| 等级 | 权重 | 理由 |
|------|------|------|
| 精通 | 1.5 | 精通一项技能比熟练3项技能更有价值 |
| 熟练 | 1.0 | 标准参考权重 |
| 熟悉 | 0.7 | 可以使用但不够深入，贡献度打7折 |
| 了解 | 0.5 | 仅入门，贡献度打5折 |

---

## 后续优化建议

### 短期优化

1. ✅ 完成核心算法实现
2. ✅ 更新前端显示
3. ✅ 添加单元测试
4. ⏳ 更新用户文档

### 长期优化

1. **动态权重调整**：根据岗位要求动态调整熟练度权重
   - 例如：某些岗位可能更看重"熟练"而非"精通"

2. **技能稀缺性加分**：对稀缺技能（如AI、区块链）给予额外加分
   - 可以通过 `LEVEL_SCORES` 的基础上叠加 `稀缺性系数`

3. **技能组合加成**：特定技能组合给予额外加分
   - 例如：Python + 机器学习 + 数据分析 = +5分

4. **用户反馈机制**：收集用户对评分的反馈，持续优化权重
   - 通过A/B测试验证新的权重设置

---

## 总结

### 实现的修改

✅ **TechnicalAnalyzer 类**：
- 更新 `LEVEL_SCORES`（翻倍）
- 添加 `LEVEL_WEIGHTS`
- 简化 `__init__` 方法（移除LLM和行业检测）
- 简化 `analyze` 方法（移除LLM调用）
- 重写 `_calculate_total_score` 方法（使用新的加权平均公式）
- 移除未使用的导入

✅ **前端显示**（streamlit_app.py）：
- 移除行业检测显示
- 移除类别加权计算显示
- 添加熟练度加权平均显示
- 更新计算公式说明

✅ **测试**：
- 创建完整的单元测试
- 验证边界情况（无技能、全精通、全了解、混合等级）
- 所有测试通过 ✅

### 核心改进

- **简洁性**：移除了复杂的行业检测和类别加权系统
- **透明性**：评分算法清晰可解释，用户可以理解每个技能的贡献
- **稳定性**：减少了配置依赖，降低了出错概率
- **通用性**：适用于所有行业，不需要定制配置

### 用户影响

- ✅ 用户上传简历时会看到更清晰的评分说明
- ✅ 不再出现"未知行业"的困惑
- ✅ 评分更符合直觉（精通技能自然获得更高权重）

---

**实施日期**: 2026-01-30
**状态**: ✅ 已完成
**文档版本**: v1.0
