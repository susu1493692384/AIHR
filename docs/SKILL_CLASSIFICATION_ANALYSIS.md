# 技能分类机制分析

## 问题分析

用户指出：**技能分类关键词表现在只有IT行业的，但系统支持6个行业**

这确实是一个设计问题！

## 技能分类的两个层次

系统中有两个不同用途的"技能分类"：

### 1. 行业技能分类配置（用于评分权重）

**位置**: `config/scoring.yaml` 中的 `industry_detection.{industry}.skill_categories`

**作用**: 定义每个行业的技能类别及其评分权重

**示例**:
```yaml
industry_detection:
  it:
    skill_categories:
      language: {weight: 0.35, name: "编程语言"}
      framework: {weight: 0.25, name: "开发框架"}
      database: {weight: 0.20, name: "数据库"}
      tool: {weight: 0.15, name: "开发工具"}
      other: {weight: 0.05, name: "其他"}

  finance:
    skill_categories:
      accounting_standards: {weight: 0.30, name: "会计准则"}
      financial_analysis: {weight: 0.25, name: "财务分析"}
      financial_tools: {weight: 0.25, name: "财务工具"}
      tax_law: {weight: 0.10, name: "税法法规"}
      reporting: {weight: 0.10, name: "财务报告"}
```

**关键点**:
- ✅ 已支持6个行业
- ✅ 每个行业有独立的技能类别
- ✅ 用于计算评分时的权重分配

### 2. 技能分类关键词表（用于自动分类）

**位置**: `config/scoring.yaml` 中的 `skill_categories`（最外层）

**作用**: 当LLM/解析器提取技能时，自动将技能归类到正确的类别

**示例**:
```yaml
skill_categories:
  language:
    - python
    - java
    - javascript
    - typescript
    - go
    - rust
    - c++
    - c#
    - ruby
    - php
    - swift
    - kotlin
    - scala
    - r
    - matlab
    - shell
    - bash
    - glm
    - gpt
    - llm
    - langchain

  framework:
    - spring
    - django
    - flask
    - react
    - vue
    - angular
    - fastapi
    - express
    - laravel
    - rails
    - tensorflow
    - pytorch
    - keras
    - yolo
    - opencv
    - transformers
    - langchain
    - langgraph

  database:
    - mysql
    - postgresql
    - mongodb
    - redis
    - oracle
    - sqlserver
    - sqlite
    - elasticsearch
    - neo4j
    - cassandra
    - hive
    - spark

  tool:
    - docker
    - kubernetes
    - git
    - jenkins
    - linux
    - nginx
    - aws
    - azure
    - gcp
    - terraform
    - ansible
    - jira
    - pandas
    - numpy
    - folium
    - matplotlib
    - gitlab
    - github
    - vscode
    - idea
    - postman
    - swagger
    - graphql
    - rest
    - api
    - http
    - json
    - xml
```

**关键点**:
- ❌ 只有IT行业的技能关键词
- ❌ 其他行业（财务、HR、销售、运营）的技能关键词缺失
- ❌ 用于自动分类技能到正确的类别

## 技能分类流程

### 完整流程图

```
1. 解析简历
   ↓
2. 提取技能列表（技能名称）
   ↓
3. 使用 skill_categories 关键词表自动分类
   - Python → language ✓
   - 会计准则 → ??? (找不到，归为 other)
   ↓
4. 检测行业（基于职位标题）
   ↓
5. 使用 industry_detection.{industry}.skill_categories 获取权重
   ↓
6. 计算加权得分
```

### 问题示例

**IT行业候选人**：
```python
技能：Python, React, MySQL

分类过程：
1. Python → 在 language 关键词表中 → category = "language" ✓
2. React → 在 framework 关键词表中 → category = "framework" ✓
3. MySQL → 在 database 关键词表中 → category = "database" ✓

评分：
- language: 40分 × 0.35 = 14.00
- framework: 30分 × 0.25 = 7.50
- database: 40分 × 0.20 = 8.00
- 总分: 36.88分 ✓
```

**财务行业候选人**：
```python
技能：会计准则, 财务分析, Excel

分类过程：
1. 会计准则 → 不在关键词表中 → category = "other" ❌
2. 财务分析 → 不在关键词表中 → category = "other" ❌
3. Excel → 在 tool 关键词表中 → category = "tool" ✓

评分：
- accounting_standards: 40分 × 0.30 = 12.00 (期望)
- financial_analysis: 80分 × 0.25 = 20.00 (期望)
- financial_tools: 40分 × 0.25 = 10.00 (期望)

实际：
- other: 40分 × 0.05 = 2.00 ❌
- other: 80分 × 0.05 = 4.00 ❌
- tool: 40分 × 0.15 = 6.00 ✓
- 总分: 15分 (错误！应该是52.5分)
```

## 影响范围

### 当前问题的严重程度

#### 1. 对于IT行业简历

**影响**: ✅ 无影响

**原因**: IT行业的技能关键词完整，能正确分类

**示例**:
```
Python → language ✓
React → framework ✓
MySQL → database ✓
Docker → tool ✓
```

#### 2. 对于其他行业简历

**影响**: ❌ 严重！评分完全错误

**原因**: 其他行业的技能无法被正确分类，全部归为"other"

**示例**:
```
财务行业：
  会计准则 → other ❌ (应该是 accounting_standards)
  财务分析 → other ❌ (应该是 financial_analysis)
  Excel → tool ✓ (碰巧IT行业也有)

HR行业：
  招聘流程 → other ❌ (应该是 recruitment)
  劳动法规 → other ❌ (应该是 labor_law)

销售行业：
  销售技巧 → other ❌ (应该是 sales_techniques)
  商务谈判 → other ❌ (应该是 negotiation)
```

## 解决方案

### 方案1: 扩展关键词表支持所有行业（推荐）

为每个行业添加技能分类关键词表：

```yaml
skill_categories:
  # IT行业技能关键词
  language: [python, java, ...]
  framework: [react, django, ...]
  database: [mysql, postgresql, ...]
  tool: [docker, git, ...]

  # 财务行业技能关键词
  accounting_standards: [gaap, ifrs, 会计准则, 财务准则]
  financial_analysis: [财务分析, 财务报表, 预算管理]
  financial_tools: [excel, sap, oracle, 用友, 金蝶]
  tax_law: [税法, 税务, 税务法规]
  reporting: [财务报告, 年报, 季报]

  # HR行业技能关键词
  recruitment: [招聘, 面试, 猎头, 简历筛选]
  employee_relations: [员工关系, 企业文化, 团队建设]
  labor_law: [劳动法, 劳动法规, 合同法]
  performance_management: [绩效, kpi, 考核, 晋升]
  hr_tools: [hris, oa, 钉钉, 企业微信]

  # 其他行业...
```

**优点**:
- ✅ 所有行业的技能都能正确分类
- ✅ 评分准确
- ✅ 自动分类，无需手动指定

**缺点**:
- ⚠️ 配置文件会变大
- ⚠️ 需要维护多行业关键词表

### 方案2: LLM自动分类（智能化）

使用LLM根据行业自动分类技能：

```python
def classify_skill_with_llm(skill_name: str, industry: str) -> str:
    """使用LLM分类技能"""
    prompt = f"""
    请将技能"{skill_name}"归类到{industry}行业的正确类别中。

    {industry}行业的类别包括：
    {get_industry_categories(industry)}

    只返回类别名称，不要其他内容。
    """
    category = call_llm(prompt)
    return category
```

**优点**:
- ✅ 不需要维护庞大的关键词表
- ✅ 智能化，能理解技能上下文
- ✅ 可扩展到任意行业

**缺点**:
- ⚠️ 需要调用LLM（成本较高）
- ⚠️ 可能不稳定

### 方案3: 混合方案（推荐）

```python
def classify_skill(skill_name: str, industry: str) -> str:
    """分类技能（混合方案）"""
    # 1. 先尝试关键词匹配（快速）
    category = match_by_keywords(skill_name, industry)
    if category and category != "other":
        return category

    # 2. 关键词匹配失败，使用LLM（准确）
    if llm_available:
        category = classify_skill_with_llm(skill_name, industry)
        return category

    # 3. LLM也失败，返回"other"
    return "other"
```

**优点**:
- ✅ 快速：大多数技能通过关键词匹配
- ✅ 准确：复杂技能使用LLM分类
- ✅ 灵活：可扩展到任意行业

## 建议

### 短期（立即实施）

**扩展 skill_categories 关键词表**

至少添加主要行业的核心技能关键词：

```yaml
skill_categories:
  # IT行业（已有）
  language: [python, java, ...]
  framework: [react, django, ...]
  database: [mysql, redis, ...]
  tool: [docker, git, ...]

  # 财务行业（新增）
  accounting_standards: [gaap, ifrs, 会计准则, 财务准则, 企业会计]
  financial_analysis: [财务分析, 报表分析, 预算, 核算, 审计]
  financial_tools: [excel, word, ppt, sap, oracle, 用友, 金蝶]
  tax_law: [税法, 税务, 税务法规, 个人所得税, 企业所得税]
  reporting: [财务报告, 年报, 季报, 月报, 报表编制]

  # HR行业（新增）
  recruitment: [招聘, 面试, 猎头, 简历筛选, 人才引进]
  employee_relations: [员工关系, 企业文化, 团队建设, 员工关怀]
  labor_law: [劳动法, 劳动法规, 合同法, 社保, 公积金]
  performance_management: [绩效, kpi, 考核, 晋升, 激励]
  hr_tools: [hris, oa, 钉钉, 企业微信, 飞书]

  # 其他行业...
```

### 长期（优化方向）

1. **LLM辅助分类**
   - 关键词匹配失败时，使用LLM分类
   - 提高分类准确性

2. **学习机制**
   - 记录人工修正的分类结果
   - 不断优化关键词表

3. **行业扩展**
   - 支持用户自定义行业
   - 支持用户自定义技能类别

## 总结

### 当前问题

❌ **skill_categories 关键词表只有IT行业**
- 其他行业技能无法正确分类
- 导致评分严重错误

### 影响范围

| 行业 | 影响 | 说明 |
|------|------|------|
| IT | ✅ 无影响 | 关键词完整 |
| 财务 | ❌ 严重 | 技能全部归为"other" |
| HR | ❌ 严重 | 技能全部归为"other" |
| 销售 | ❌ 严重 | 技能全部归为"other" |
| 运营 | ❌ 严重 | 技能全部归为"other" |
| 通用 | ❌ 严重 | 技能全部归为"other" |

### 建议方案

**立即实施**: 扩展 skill_categories 关键词表，支持所有6个行业

**长期优化**: 实现LLM辅助分类，提高准确性和可扩展性
