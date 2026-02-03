# LLM辅助函数重构文档

## 重构日期
2026-01-31

## 重构目的
将LLM相关的通用查询功能从前端代码中分离出来，提高代码的可维护性和可复用性。

## 重构内容

### 1. 新建模块：[utils/llm_helpers.py](../utils/llm_helpers.py)

**功能**：提供通用的LLM查询辅助函数

**导出的函数**：
- `get_llm()`: 获取LLM实例（带缓存）
- `get_skill_description(skill_name, level)`: 获取技能描述
- `get_school_description(school_name)`: 获取学校描述
- `get_company_description(company_name)`: 获取公司描述

**特点**：
- 使用 `@lru_cache(maxsize=1)` 缓存LLM实例
- 统一的错误处理机制
- 支持LLM联网搜索功能
- 自动清理markdown格式输出

### 2. 更新模块：[app/streamlit_app.py](../app/streamlit_app.py)

**改动**：
- 移除了原本的 `get_llm()`, `get_skill_description()`, `get_school_description()` 函数定义
- 改为从 `utils.llm_helpers` 导入这些函数
- 使用 Streamlit 的缓存装饰器包装导入的函数

**代码示例**：
```python
# 导入LLM辅助函数
from utils.llm_helpers import get_llm, get_skill_description as _get_skill_description
from utils.llm_helpers import get_school_description as _get_school_description

@st.cache_data(ttl=3600)
def get_skill_description(skill_name: str, level: str = "了解") -> str:
    """获取技能描述（使用Streamlit缓存）"""
    return _get_skill_description(skill_name, level)

@st.cache_data(ttl=86400)
def get_school_description(school_name: str) -> str:
    """获取学校描述（使用Streamlit缓存）"""
    return _get_school_description(school_name)
```

## 重构优势

### 1. 代码组织更清晰
- **之前**：LLM查询函数混杂在前端代码中
- **现在**：统一的LLM辅助模块，职责单一

### 2. 可复用性提升
- 其他模块（如agents、tools）也可以使用这些函数
- 避免代码重复

### 3. 易于测试
- 可以独立测试LLM辅助函数
- 测试文件：[test/test_llm_helpers.py](../test/test_llm_helpers.py)

### 4. 易于扩展
- 未来添加新的LLM查询函数只需在 `utils/llm_helpers.py` 中添加
- 前端和其他模块都可以使用

### 5. 缓存策略优化
- **LLM实例缓存**：使用 `@lru_cache` 在Python层面缓存
- **查询结果缓存**：使用 `@st.cache_data` 在Streamlit层面缓存
- 双层缓存提高性能

## 使用示例

### 在其他模块中使用

```python
# 导入LLM辅助函数
from utils.llm_helpers import get_llm, get_skill_description, get_company_description

# 获取LLM实例
llm = get_llm()

# 获取技能描述
description = get_skill_description("Python", "精通")
print(description)

# 获取公司描述
company_desc = get_company_description("阿里巴巴")
print(company_desc)
```

### 在前端中使用

```python
# Streamlit会自动使用缓存装饰器
from utils.llm_helpers import get_skill_description as _get_skill_description

@st.cache_data(ttl=3600)
def get_skill_description(skill_name: str, level: str = "了解") -> str:
    return _get_skill_description(skill_name, level)
```

## 技术细节

### 缓存机制

**Python层面（@lru_cache）**：
- 用于缓存LLM实例
- 避免重复创建ChatZhipuAI对象
- `maxsize=1` 表示只缓存一个实例

**Streamlit层面（@st.cache_data）**：
- 用于缓存查询结果
- 技能描述：TTL=3600秒（1小时）
- 学校描述：TTL=86400秒（24小时）
- 基于参数值自动缓存

### LLM联网搜索

智谱AI的GLM-4模型默认支持联网搜索功能：
- 自动从互联网获取最新信息
- 特别适合查询学校信息等动态内容
- 返回经过处理的搜索结果摘要

## 文件清单

### 新增文件
- [utils/llm_helpers.py](../utils/llm_helpers.py) - LLM辅助函数模块
- [test/test_llm_helpers.py](../test/test_llm_helpers.py) - 单元测试

### 修改文件
- [app/streamlit_app.py](../app/streamlit_app.py) - 前端应用，移除函数定义，改为导入

## 测试验证

运行测试：
```bash
python test/test_llm_helpers.py
```

测试内容：
1. ✅ LLM实例获取
2. ✅ 技能描述生成
3. ✅ 学校描述生成
4. ✅ 缓存机制验证

## 注意事项

1. **环境变量**：需要配置 `ZHIPU_API_KEY` 环境变量
2. **网络连接**：联网搜索功能需要互联网访问
3. **缓存清理**：如需更新数据，清除Streamlit缓存或等待TTL过期
4. **错误处理**：所有函数都有异常处理，失败时返回默认值

## 未来扩展

可以考虑添加更多LLM辅助函数：
- `get_major_description(major_name)`: 专业描述
- `get_tech_stack_info(tech_name)`: 技术栈详细信息
- `get_industry_trends(industry)`: 行业趋势分析
- `get_project_role_description(role)`: 项目角色描述

---

**重构人员**: AI Assistant
**审核状态**: ✅ 完成
