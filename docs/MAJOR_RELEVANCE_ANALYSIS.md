# 专业背景相关性判断机制分析

## 文档信息

- **版本**: v1.0
- **更新日期**: 2026-01-30
- **相关问题**: 系统已支持多行业，但专业相关性判断仍写死为IT行业

---

## 当前实现

### 代码位置

[experience_analyzer.py:573-576](tools/analysis/experience_analyzer.py#L573-L576)

```python
# CS相关专业
if highest_edu.major:
    major_lower = highest_edu.major.lower()
    if any(cs in major_lower for cs in self.cs_related_majors):
        highlights.append("专业背景相关")
```

### 判断逻辑

```
获取最高学历的专业名称
    ↓
转换为小写
    ↓
匹配 cs_related_majors 列表
    ↓
如果匹配成功 → "专业背景相关"
如果未匹配 → 不显示此亮点
```

### 专业列表配置

**位置**: [config/scoring.yaml:586-610](config/scoring.yaml#L586-L610)

```yaml
# 相关专业列表（用于判断专业是否相关）
cs_related_majors:
  - 计算机
  - 软件工程
  - 人工智能
  - 数据科学
  - 机器学习
  - 深度学习
  - 信息安全
  - 网络工程
  - 物联网
  - 数学
  - 统计
  - computer
  - software
  - ai
  - artificial intelligence
  - data science
  - machine learning
  - deep learning
  - information security
  - network engineering
  - iot
  - math
  - mathematics
  - statistics
```

### 匹配示例

| 专业名称 | 是否相关 | 判断依据 |
|---------|---------|---------|
| 计算机科学与技术 | ✅ 相关 | 包含 "计算机" |
| 软件工程 | ✅ 相关 | 完全匹配 |
| 人工智能 | ✅ 相关 | 完全匹配 |
| 数据科学 | ✅ 相关 | 完全匹配 |
| 数学与应用数学 | ✅ 相关 | 包含 "数学" |
| Computer Science | ✅ 相关 | 包含 "computer" |
| 财务管理 | ❌ 不相关 | 不在列表中 |
| 会计学 | ❌ 不相关 | 不在列表中 |
| 人力资源管理 | ❌ 不相关 | 不在列表中 |

---

## 问题分析

### 核心问题

**当前实现**：
- ✅ 只支持IT/CS相关专业
- ❌ 不支持其他行业（财务、HR、销售、运营、通用）
- ⚠️ 系统已支持6个行业，但专业判断仍写死为IT

### 影响

**对IT行业候选人**：
```
专业: 计算机科学与技术
判断: ✅ 专业背景相关
结果: 亮点中显示 "专业背景相关"
```

**对财务行业候选人**：
```
专业: 会计学
判断: ❌ 专业背景相关（代码硬编码，只匹配CS专业）
结果: 亮点中不显示 "专业背景相关"
问题: 财务专业的候选人申请财务岗位，理应显示"专业背景相关"
```

**对HR行业候选人**：
```
专业: 人力资源管理
判断: ❌ 专业背景相关
问题: HR专业的候选人申请HR岗位，理应显示"专业背景相关"
```

---

## 改进方案

### 方案1：根据行业动态判断专业相关性（推荐）

#### 实现思路

为每个行业配置对应的相关专业列表，根据检测到的行业动态判断。

#### 配置文件扩展

在 [config/scoring.yaml](config/scoring.yaml) 中添加：

```yaml
# 行业相关专业映射
industry_related_majors:
  # IT/互联网行业
  it:
    - 计算机
    - 软件工程
    - 人工智能
    - 数据科学
    - 机器学习
    - 深度学习
    - 信息安全
    - 网络工程
    - 物联网
    - 数学
    - 统计
    - computer
    - software
    - ai
    - data science
    - machine learning
    - information security
    - network engineering
    - iot
    - math
    - statistics

  # 财务行业
  finance:
    - 会计
    - 财务管理
    - 审计
    - 财务学
    - 金融学
    - 金融工程
    - 税务
    - 会计学
    - accounting
    - finance
    - financial management
    - taxation

  # HR行业
  hr:
    - 人力资源管理
    - 工商管理
    - 心理学
    - 社会学
    - 人力资源
    - hrm
    - business administration
    - psychology
    - sociology

  # 销售行业
  sales:
    - 市场营销
    - 销售管理
    - 工商管理
    - 国际贸易
    - 市场营销学
    - marketing
    - sales management
    - business administration
    - international trade

  # 运营行业
  operations:
    - 市场营销
    - 工商管理
    - 统计学
    - 数据分析
    - 电子商务
    - marketing
    - business administration
    - statistics
    - data analysis
    - e-commerce

  # 通用行业
  general:
    - 工商管理
    - 经济学
    - 管理学
    - business administration
    - economics
    - management
```

#### 代码实现

修改 [experience_analyzer.py](tools/analysis/experience_analyzer.py)：

```python
class ExperienceAnalyzer(BaseAnalyzer):
    def __init__(self, config: ScoreConfig = None):
        super().__init__(config)

        # 加载行业相关专业映射
        self.industry_related_majors = (
            self.config.industry_related_majors
            if self.config.industry_related_majors
            else self._get_default_industry_majors()
        )

    def _get_default_industry_majors(self) -> Dict[str, List[str]]:
        """获取默认的行业专业映射"""
        return {
            "it": self.DEFAULT_CS_RELATED_MAJORS,  # 使用现有的CS专业列表
            "general": []
        }

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """分析经验背景"""
        # 1. 检测行业
        from tools.analysis.industry_detector import IndustryDetector
        industry_detector = IndustryDetector(self.config)
        industry = industry_detector.detect_industry(resume)

        # 2. 分离实习和工作经历
        internships, work_experience = self._separate_internships_and_work(
            resume.cleaned_data.work_experience
        )

        # 3. 计算得分
        detail_scores = self._calculate_detail_scores(
            resume.cleaned_data.education,
            work_experience,
            internships
        )
        total_score = self._calculate_total_score(detail_scores)

        # 4. 提取亮点（使用行业特定的专业列表）
        highlights = self._extract_highlights(
            resume,
            resume.cleaned_data.education,
            work_experience,
            internships,
            industry  # 传入检测到的行业
        )

        return AnalysisResult(
            dimension=self.dimension_name,
            score=total_score,
            detail_scores=detail_scores,
            insights=self._extract_insights(...),
            highlights=highlights,  # 使用新的亮点提取方法
            weaknesses=self._extract_weaknesses(...),
            raw_analysis={
                "industry": industry,
                "job_count": len(work_experience),
                "internship_count": len(internships),
                "education_count": len(resume.cleaned_data.education)
            }
        )

    def _extract_highlights(
        self,
        resume: CleanedResume,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience],
        industry: str  # 新增：行业参数
    ) -> List[str]:
        """提取亮点（支持多行业专业判断）"""
        highlights = []

        # 教育背景亮点
        if education:
            highest_edu = self._get_highest_education(education)
            degree = highest_edu.degree

            # 高学历
            if "博士" in degree or "phd" in degree.lower():
                highlights.append("拥有博士学位")

            # 985/211学校
            if self.config and self.config.school_tier:
                tier = self.config.get_school_tier(highest_edu.school)
                if tier == "985":
                    highlights.append("毕业于985院校")
                elif tier == "211":
                    highlights.append("毕业于211院校")

            # ========== 新增：行业相关专业判断 ==========
            # 获取当前行业的相关专业列表
            related_majors = self.industry_related_majors.get(
                industry,
                self.industry_related_majors.get("general", [])
            )

            # 判断专业是否相关
            if highest_edu.major and related_majors:
                major_lower = highest_edu.major.lower()
                if any(major.lower() in major_lower for major in related_majors):
                    highlights.append("专业背景相关")

            # ... 其他亮点提取逻辑

        return highlights
```

### 方案2：使用LLM智能判断专业相关性（高级）

#### 实现思路

利用LLM根据行业和职位描述智能判断专业相关性。

```python
def _is_major_relevant_llm(
    self,
    major: str,
    industry: str,
    target_position: str
) -> bool:
    """使用LLM判断专业是否相关"""

    if not self.llm:
        # 回退到关键词匹配
        return self._is_major_relevant_keyword(major, industry)

    prompt = f"""
    请判断以下专业是否与目标职位相关：

    专业：{major}
    目标行业：{industry}
    目标职位：{target_position}

    考虑以下因素：
    1. 专业的核心课程是否与职位要求匹配
    2. 专业的培养目标是否符合职位需求
    3. 相关性评分（0-10分）

    只回答"是"或"否"，不要其他内容。
    """

    try:
        response = await self.llm.ainvoke(prompt)
        return "是" in response or "相关" in response
    except:
        return self._is_major_relevant_keyword(major, industry)
```

---

## 示例对比

### 当前实现（硬编码IT专业）

**IT行业候选人**：
```
专业: 计算机科学与技术
职位: 软件工程师
判断: ✅ 专业背景相关
```

**财务行业候选人**：
```
专业: 会计学
职位: 财务分析师
判断: ❌ 专业背景相关（错误！）
```

**HR行业候选人**：
```
专业: 人力资源管理
职位: HRBP
判断: ❌ 专业背景相关（错误！）
```

### 改进后（多行业专业列表）

**IT行业候选人**：
```
专业: 计算机科学与技术
职位: 软件工程师
判断: ✅ 专业背景相关
行业: it
专业列表: [计算机, 软件工程, 人工智能, ...]
```

**财务行业候选人**：
```
专业: 会计学
职位: 财务分析师
判断: ✅ 专业背景相关
行业: finance
专业列表: [会计, 财务管理, 审计, 金融学, ...]
```

**HR行业候选人**：
```
专业: 人力资源管理
职位: HRBP
判断: ✅ 专业背景相关
行业: hr
专业列表: [人力资源管理, 工商管理, 心理学, ...]
```

---

## 配置示例

### 完整的行业专业配置

```yaml
# config/scoring.yaml

# ============ 行业相关专业映射 ============
# 用于判断候选人的专业是否与目标行业相关
industry_related_majors:
  # IT/互联网行业
  it:
    name: "IT/互联网行业相关专业"
    majors:
      # 核心专业（完全匹配）
      - 计算机科学与技术
      - 软件工程
      - 人工智能
      - 数据科学
      - 机器学习
      # ...

      # 相关专业（关键词匹配）
      - 计算机
      - 软件
      - 人工智能
      - 数据

  # 财务行业
  finance:
    name: "财务行业相关专业"
    majors:
      - 会计学
      - 财务管理
      - 审计学
      - 金融学
      - 税务

  # HR行业
  hr:
    name: "人力资源专业"
    majors:
      - 人力资源管理
      - 工商管理
      - 应用心理学
      - 劳动关系

  # 其他行业...
```

---

## 代码实现（完整版）

### 修改 ExperienceAnalyzer

```python
# tools/analysis/experience_analyzer.py

class ExperienceAnalyzer(BaseAnalyzer):
    """经验背景分析器 - 支持多行业专业判断"""

    def __init__(self, config: ScoreConfig = None, llm=None):
        super().__init__(config)

        # 行业检测器
        from tools.analysis.industry_detector import IndustryDetector
        self.industry_detector = IndustryDetector(config)

        # 加载行业相关专业映射
        self.industry_related_majors = (
            config.industry_related_majors
            if config.industry_related_majors
            else {}
        )

    def analyze(self, resume: CleanedResume) -> AnalysisResult:
        """分析经验背景（支持多行业）"""
        # 1. 检测行业
        industry = self.industry_detector.detect_industry(resume)

        # 2. 分离实习和工作
        internships, work_experience = self._separate_internships_and_work(
            resume.cleaned_data.work_experience
        )

        # 3. 计算得分
        detail_scores = self._calculate_detail_scores(
            resume.cleaned_data.education,
            work_experience,
            internships
        )
        total_score = self._calculate_total_score(detail_scores)

        # 4. 提取亮点（传入行业）
        highlights = self._extract_highlights(
            resume,
            resume.cleaned_data.education,
            work_experience,
            internships,
            industry  # 关键：传入行业
        )

        # 5. 提取关键发现
        insights = self._extract_insights(
            resume,
            resume.cleaned_data.education,
            work_experience,
            internships
        )

        # 6. 提取不足
        weaknesses = self._extract_weaknesses(
            resume,
            resume.cleaned_data.education,
            work_experience,
            internships
        )

        return AnalysisResult(
            dimension=self.dimension_name,
            score=total_score,
            detail_scores=detail_scores,
            insights=insights,
            highlights=highlights,
            weaknesses=weaknesses,
            raw_analysis={
                "industry": industry,
                "industry_name": self.industry_detector.get_industry_name(industry),
                "job_count": len(work_experience),
                "internship_count": len(internships),
                "education_count": len(resume.cleaned_data.education)
            }
        )

    def _extract_highlights(
        self,
        resume: CleanedResume,
        education: List[Education],
        work_experience: List[WorkExperience],
        internships: List[WorkExperience],
        industry: str  # 新增行业参数
    ) -> List[str]:
        """提取亮点（支持多行业专业判断）"""
        highlights = []

        # 教育背景亮点
        if education:
            highest_edu = self._get_highest_education(education)
            degree = highest_edu.degree

            # 高学历
            if "博士" in degree or "phd" in degree.lower():
                highlights.append("拥有博士学位")
            elif "硕士" in degree or "研究生" in degree:
                highlights.append("拥有硕士学历")

            # 985/211学校
            if self.config and self.config.school_tier:
                tier = self.config.get_school_tier(highest_edu.school)
                if tier == "985":
                    highlights.append("毕业于985院校")
                elif tier == "211":
                    highlights.append("毕业于211院校")

            # ========== 新增：行业相关专业判断 ==========
            if highest_edu.major:
                # 获取当前行业的相关专业列表
                related_majors = self.industry_related_majors.get(industry, [])

                if related_majors:
                    # 判断专业是否相关
                    major_lower = highest_edu.major.lower()
                    is_relevant = any(
                        major.lower() in major_lower
                        for major in related_majors
                    )

                    if is_relevant:
                        highlights.append("专业背景相关")

        # 工作经验亮点
        if work_experience:
            # 大厂经历（根据行业定义）
            industry_big_companies = {
                "it": ["阿里", "腾讯", "字节", "百度", "华为", "美团", "京东", "Google", "Microsoft", "Amazon"],
                "finance": ["四大会计师事务所", "中金", "中信证券", "招商银行", "工商银行"],
                "hr": [],
                "sales": [],
                "operations": [],
                "general": []
            }

            big_companies = industry_big_companies.get(industry, [])

            for exp in work_experience:
                if any(company in exp.company for company in big_companies):
                    highlights.append(f"有{exp.company}工作经历")
                    break

            # 管理经验
            for exp in work_experience:
                if any(k in exp.position for k in ["经理", "总监", "主管", "负责人", "lead"]):
                    highlights.append("具有管理经验")
                    break

        # 实习经验亮点
        if internships and not work_experience:
            total_internship_months = sum(
                self._calculate_experience_months(exp)
                for exp in internships
            )
            if total_internship_months >= 6:
                highlights.append("实习经验丰富（6个月以上）")

        return highlights
```

---

## 配置文件修改

### 在 config/scoring.yaml 中添加

```yaml
# ============ 行业相关专业映射 ============
industry_related_majors:
  # IT/互联网行业
  it:
    name: "IT/互联网"
    majors:
      # 核心专业
      - 计算机科学与技术
      - 软件工程
      - 人工智能
      - 数据科学
      - 机器学习
      - 深度学习
      # 相关专业
      - 计算机
      - 软件
      - ai
      - 数据
      - 数学
      - 统计
      - physics
      - 电子信息

  # 财务行业
  finance:
    name: "财务行业"
    majors:
      - 会计学
      - 财务管理
      - 审计学
      - 金融学
      - 金融工程
      - 税务
      - accounting
      - finance
      - financial management
      - taxation

  # HR行业
  hr:
    name: "人力资源"
    majors:
      - 人力资源管理
      - 工商管理
      - 应用心理学
      - 劳动关系
      - 人力资源
      - hrm
      - business administration

  # 销售行业
  sales:
    name: "销售行业"
    majors:
      - 市场营销
      - 销售管理
      - 工商管理
      - 国际贸易
      - 市场营销学
      - marketing
      - sales management

  # 运营行业
  operations:
    name: "运营"
    majors:
      - 市场营销
      - 工商管理
      - 统计学
      - 数据分析
      - 电子商务
      - marketing
      - data analysis

  # 通用行业
  general:
    name: "通用"
    majors:
      - 工商管理
      - 经济学
      - 管理学
      - business administration
      - economics
```

---

## 总结

### 当前问题

- ❌ 专业相关性判断**硬编码为IT行业**
- ❌ 其他行业候选人的专业相关性无法被识别
- ⚠️ 与多行业支持不匹配

### 改进后

- ✅ 根据检测到的行业动态判断
- ✅ 支持6个行业的专业列表
- ✅ 配置驱动，易于扩展
- ✅ 在亮点中显示"专业背景相关"

### 实施优先级

| 优先级 | 方案 | 工作量 | 效果 |
|--------|------|--------|------|
| 高 | 方案1：配置驱动 | 中 | ✅ 完全解决，易维护 |
| 中 | 方案2：LLM判断 | 高 | ✅ 智能化，但成本高 |
| 低 | 保持现状 | 无 | ⚠️ 继续只支持IT |

### 建议

**推荐实施方案1**：
1. 在 `config/scoring.yaml` 中添加 `industry_related_majors` 配置
2. 修改 `ExperienceAnalyzer.__init__()` 加载配置
3. 修改 `ExperienceAnalyzer.analyze()` 传入行业参数
4. 修改 `_extract_highlights()` 使用行业特定专业列表

**工作量估计**：
- 配置文件修改：30分钟
- 代码修改：1-2小时
- 测试验证：1小时

**收益**：
- ✅ 支持所有6个行业
- ✅ 提高分析准确性
- ✅ 提升用户体验

---

**文档版本**: v1.0
**创建日期**: 2026-01-30
