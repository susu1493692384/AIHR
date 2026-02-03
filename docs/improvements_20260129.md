# 技术能力评分改进记录

**日期**: 2026-01-29
**问题**: 技术能力维度得0分的根本原因分析
**解决方案**: 从项目经验中自动提取技能信息

## 问题描述

在分析简历时，发现技术能力得分为0分，但实际上候选人在项目经验中使用了多种技术：

- **智慧教学助手项目**: GLM3、大语言模型
- **人体行为模仿项目**: YOLOv8、关键点检测、机器人运动控制算法
- **用户地理轨迹预测项目**: 马尔可夫链、pandas、folium

### 根本原因

1. **解析阶段**: 候选人简历中没有单独的"技能"章节，导致 `skills` 字段为空
2. **评分阶段**: 技术能力评分完全依赖 `skills` 字段，如果为空则所有维度都是0分
3. **数据丢失**: 项目中的 `tech_stack` 字段包含丰富的技术信息，但没有被利用

## 解决方案

### 方案选择

选择**方案2：在分析阶段增强**，修改技术能力评分逻辑：

- ✅ 不需要重新解析简历
- ✅ 不需要修改解析器
- ✅ 只需修改评分逻辑
- ✅ 向后兼容

### 实现细节

在 `tools/analysis/resume_scorer.py` 中添加了两个新方法：

#### 1. `_extract_skills_from_projects(projects)`

从项目经验中提取技能信息：

```python
# 从项目的tech_stack中提取技能
tech_stack = project.get("tech_stack", [])
for tech in tech_stack:
    extracted_skills[tech_lower] = {
        "name": tech.strip(),
        "category": auto_classified_category,
        "level": "熟练"  # 项目中的技能默认为"熟练"
    }

# 从描述中提取技能（关键词匹配）
combined_text = f"{role} {description}".lower()
```

**特点**：
- 自动分类技能（language/framework/database/tool）
- 区分熟练度（tech_stack中的标记为"熟练"，描述中的标记为"了解"）
- 去重并排序

#### 2. `_classify_skill(skill_name, skill_categories)`

自动分类技能：

```python
# 优先匹配精确分类
for category, keywords in skill_categories.items():
    if skill_name in keywords:
        return category

# 模糊匹配（包含关键词）
for category, keywords in skill_categories.items():
    for keyword in keywords:
        if keyword in skill_name or skill_name in keyword:
            return category
```

**支持的分类**：
- **language**: Python, Java, GLM, GPT, LLM等
- **framework**: YOLO, TensorFlow, PyTorch, LangChain等
- **database**: MySQL, PostgreSQL, Redis等
- **tool**: Pandas, NumPy, Docker, Git等

#### 3. 改进 `score_technical` 方法

在 `score_technical` 方法开头添加技能提取逻辑：

```python
skills = resume_data.get("skills", [])

# 如果skills为空，尝试从项目中提取技能
if not skills and projects:
    skills = ResumeScorer._extract_skills_from_projects(projects)
```

## 改进效果

### 测试结果

| 维度 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| **技术能力总分** | 0 | 67.0 | +67.0 |
| 技能广度 | 0 | 30.0 | +30.0 |
| 技能深度 | 0 | 21.0 | +21.0 |
| 技能相关性 | 0 | 0.0 | 0 |
| 技能验证度 | 0 | 16.0 | +16.0 |

### 提取的技能（共10个）

1. YOLOv8 (framework, 熟练)
2. 关键点检测 (framework, 熟练)
3. 机器人运动控制算法 (framework, 熟练)
4. GLM3 (language, 熟练)
5. 大语言模型 (language, 熟练)
6. 马尔可夫链
7. folium (tool, 熟练)
8. pandas (tool, 熟练)

### 分析结果

**优势**：
- ✅ 技能多样性好
- ✅ 实战经验丰富
- ✅ 技术栈覆盖面广，掌握多种技术

**建议**：
- 扩展技术栈广度（补充更多编程语言和框架）
- 提升技能深度（深入研究某些技术）
- 增加项目实践验证

## 技术细节

### 技能分类关键词

```python
skill_categories = {
    "language": ["python", "java", "glm", "gpt", "llm", ...],
    "framework": ["yolo", "tensorflow", "langchain", ...],
    "database": ["mysql", "postgresql", "redis", ...],
    "tool": ["pandas", "docker", "git", ...]
}
```

### 熟练度判断规则

- **"熟练"**: 直接从项目 `tech_stack` 中提取
- **"了解"**: 从项目描述或职责中通过关键词匹配提取

### 后续优化方向

1. **技能去重**: 改进去重算法（如 "GLM3" 和 "GLM" 应该合并）
2. **技能权重**: 根据项目复杂度和技术难度调整技能权重
3. **技能验证**: 提高技能验证度的计算准确性
4. **相关性评分**: 改进与岗位要求的相关性评分

## 文件变更

- ✅ `tools/analysis/resume_scorer.py`: 添加技能提取和分类方法
- ✅ `test_skill_extraction.py`: 技能提取单元测试
- ✅ `test_complete_analysis.py`: 完整分析流程测试

## 向后兼容性

✅ **完全向后兼容**

- 如果 `skills` 字段有值，使用原有逻辑
- 只有在 `skills` 为空且有项目时才提取技能
- 不影响已有的评分逻辑和数据结构
