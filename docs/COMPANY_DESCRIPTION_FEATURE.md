# 公司描述功能实现文档

## 实现日期
2026-01-31

## 功能概述
为工作经验中的公司名称添加LLM生成的公司介绍，帮助HR快速了解候选人所在公司的背景信息。

## 实现内容

### 1. 新增函数：[utils/llm_helpers.py:104-139](../utils/llm_helpers.py#L104-L139)

```python
def get_company_description(company_name: str) -> str:
    """获取公司描述（使用LLM联网搜索生成）"""
```

**功能特点**：
- ✅ 使用LLM联网搜索获取公司信息
- ✅ 2-3句话简洁描述
- ✅ 包含主营业务、公司性质、所在行业
- ✅ 带异常处理，失败时返回默认描述

**Prompt设计**：
```
公司名称：{company_name}

要求：
1. 简洁明了，2-3句话
2. 说明公司的主营业务
3. 说明公司的性质（上市公司/独角兽/创业公司/国企/外企等）
4. 可以提及公司所在行业或领域
5. 利用联网搜索获取最新信息
```

### 2. 前端集成：[app/streamlit_app.py:597-617](../app/streamlit_app.py#L597-L617)

在教育背景的expander中添加了学校描述显示：
```python
# LLM生成的公司描述
with st.spinner(f"正在获取{company}的信息..."):
    company_description = get_company_description(company)
    st.info(f"🏢 {company_description}")
```

### 3. 测试文件更新：[test/test_llm_helpers.py](../test/test_llm_helpers.py)

添加了公司描述的测试用例：
```python
# 测试4: get_company_description
description = get_company_description("阿里巴巴")
print(f"  公司描述: {description}")
```

## 使用效果

当用户在Streamlit前端展开工作经验时：
1. 会看到"正在获取XXX公司的信息..."的加载提示
2. LLM通过联网搜索获取该公司的最新信息
3. 显示类似：
   ```
   🏢 阿里巴巴是中国领先的电子商务和科技公司，上市公司，业务涵盖电商零售、云计算、数字媒体等多个领域。
   ```

## 技术细节

### 缓存策略
- **TTL**: 86400秒（24小时）
- **原因**: 公司信息相对稳定，不需要频繁更新
- **优化**: 避免重复调用LLM，节省API成本

### 联网搜索
- 智谱AI GLM-4模型自动启用web_search工具
- 适用于查询公司、学校等动态信息
- 返回经过处理的搜索结果摘要

### 容错处理
```python
try:
    response = llm.invoke(prompt)
    # ... 处理响应
except Exception:
    return f"{company_name}是企业。"
```

## 功能对比

| 功能 | 函数名 | 缓存时间 | 用途 |
|------|--------|----------|------|
| 技能描述 | get_skill_description | 1小时 | 解释技能是什么 |
| 学校描述 | get_school_description | 24小时 | 介绍学校背景 |
| 公司描述 | get_company_description | 24小时 | 介绍公司背景 |

## 使用示例

### 直接调用
```python
from utils.llm_helpers import get_company_description

# 获取公司描述
desc = get_company_description("腾讯")
print(desc)
# 输出：腾讯是中国领先的互联网增值服务提供商，上市公司，业务涵盖社交、游戏、金融科技等领域。
```

### 在Streamlit中使用
```python
from utils.llm_helpers import get_company_description as _get_company_description

@st.cache_data(ttl=86400)
def get_company_description(company_name: str) -> str:
    return _get_company_description(company_name)

# 在UI中显示
description = get_company_description(work['company'])
st.info(f"🏢 {description}")
```

## 注意事项

1. **网络连接**：联网搜索需要互联网访问
2. **API密钥**：需要配置 `ZHIPU_API_KEY` 环境变量
3. **缓存清理**：如需更新数据，清除Streamlit缓存或等待24小时
4. **公司名称**：依赖简历中提供的公司名称准确性

## 未来扩展

可以考虑添加更多公司相关信息：
- `get_company_ranking(company_name)`: 公司排名信息
- `get_company_culture(company_name)`: 公司文化介绍
- `get_company_benefits(company_name)`: 公司福利待遇
- `get_industry_comparison(industry)`: 行业对比分析

## 相关文件

- [utils/llm_helpers.py](../utils/llm_helpers.py) - 核心实现
- [app/streamlit_app.py](../app/streamlit_app.py) - 前端集成
- [test/test_llm_helpers.py](../test/test_llm_helpers.py) - 测试用例
- [docs/LLM_HELPERS_REFACTOR.md](../docs/LLM_HELPERS_REFACTOR.md) - 重构文档

---

**实现人员**: AI Assistant
**审核状态**: ✅ 完成
