# 部署指南

**适用场景**: 在新电脑/服务器上部署AI简历分析系统
**最后更新**: 2026-01-28

---

## 📋 部署前检查清单

- [ ] Python 3.9 或更高版本
- [ ] pip (Python包管理器)
- [ ] Git (可选，用于克隆代码)
- [ ] 智谱AI API Key
- [ ] 至少 2GB 可用内存
- [ ] 网络连接（用于下载依赖和调用API）

---

## 🚀 部署步骤

### 步骤1: 准备Python环境

#### Windows

```powershell
# 1. 检查Python版本
python --version
# 应显示 Python 3.9.0 或更高

# 2. 如果未安装，从 python.org 下载安装
```

#### Linux/Mac

```bash
# 1. 检查Python版本
python3 --version
# 或
python --version

# 2. 如果未安装
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (使用Homebrew):
brew install python@3.9
```

---

### 步骤2: 获取项目代码

#### 方式A: 使用Git克隆（推荐）

```bash
git clone <repository-url>
cd AI_HR2
```

#### 方式B: 下载压缩包

1. 下载项目压缩包
2. 解压到目标目录
3. 进入项目目录

```bash
cd AI_HR2
```

---

### 步骤3: 创建虚拟环境

虚拟环境可以隔离项目依赖，避免冲突。

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

**验证激活成功**：
- 命令行前面会显示 `(venv)`
- 运行 `python --version` 确认使用正确的Python

---

### 步骤4: 安装依赖

```bash
# 升级pip（推荐）
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**依赖列表**：

```txt
langchain>=0.1.0
langchain-core>=0.1.0
langchain-zhipu>=0.1.0
PyPDF2>=3.0.0
python-docx>=1.0.0
streamlit>=1.28.0
python-dotenv>=1.0.0
pyyaml>=6.0
```

**安装时间**: 约2-5分钟（取决于网络速度）

---

### 步骤5: 配置环境变量

#### 5.1 创建 .env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
notepad .env      # Windows
nano .env        # Linux/Mac
vim .env         # 或使用vim
```

#### 5.2 填入API Key

```bash
ZHIPU_API_KEY=your_actual_api_key_here
```

**获取API Key**：

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 进入"API Key"页面
4. 创建新的API Key
5. 复制API Key到 `.env` 文件

**⚠️ 重要提示**：
- 不要泄露API Key
- 不要提交 `.env` 文件到Git
- `.gitignore` 已配置忽略此文件

---

### 步骤6: 验证安装

运行测试以验证所有组件正常工作：

```bash
# 运行测试套件
pytest tests/ -v

# 应该看到 109 个测试全部通过
# passed: 109
```

**如果测试失败**：

1. 检查依赖是否完整安装：
```bash
pip list | grep langchain
```

2. 检查Python版本：
```bash
python --version
```

3. 重新安装依赖：
```bash
pip install -r requirements.txt --force-reinstall
```

---

### 步骤7: 启动应用

#### 方式A: Streamlit前端（推荐）

```bash
streamlit run app/streamlit_app.py
```

访问 `http://localhost:8501`

#### 方式B: 命令行API

创建测试脚本 `test_api.py`：

```python
import asyncio
from langchain_zhipu import ChatZhipuAI
from agents import OrchestratorAgent

async def main():
    # 初始化
    llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.3,
        api_key="your_api_key"  # 从.env自动加载
    )

    orchestrator = OrchestratorAgent(llm, verbose=True)

    # 分析
    result = await orchestrator.run({
        "file_path": "path/to/resume.pdf",
        "job_requirements": "Python开发工程师",
        "report_types": ["full"]
    })

    print(f"成功: {result['success']}")
    print(f"总分: {result['state']['total_score']}")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python test_api.py
```

---

## 🔧 常见部署问题

### 问题1: ModuleNotFoundError: No module named 'langchain_zhipu'

**原因**: 依赖未安装或虚拟环境未激活

**解决**:
```bash
# 确保虚拟环境已激活
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 重新安装依赖
pip install langchain-zhipu
```

---

### 问题2: FileNotFoundError: config/scoring.yaml

**原因**: 配置文件缺失

**解决**:
```bash
# 检查配置文件是否存在
ls config/scoring.yaml

# 如果缺失，从仓库重新获取
git checkout config/scoring.yaml
```

---

### 问题3: API Key错误

**原因**: API Key未配置或无效

**解决**:
```bash
# 检查.env文件
cat .env

# 确保格式正确（无空格）
ZHIPU_API_KEY=your_key

# 验证API Key
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ZHIPU_API_KEY'))"
```

---

### 问题4: PyPDF2 DeprecationWarning

**原因**: PyPDF2已弃用

**影响**: 不影响功能，仅是警告

**解决** (可选):
```bash
pip uninstall PyPDF2
pip install pypdf
```

---

## 📦 生产环境部署

### 使用Docker部署（推荐）

#### 1. 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. 创建 .dockerignore

```text
venv/
.venv/
.env
.git/
__pycache__/
*.pyc
tests/
docs/
examples/
.pytest_cache/
```

#### 3. 构建和运行

```bash
# 构建镜像
docker build -t ai-resume-analyzer .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -e ZHIPU_API_KEY=your_api_key \
  --name resume-app \
  ai-resume-analyzer
```

访问 `http://localhost:8501`

---

### 使用Systemd服务（Linux）

#### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/resume-analyzer.service
```

```ini
[Unit]
Description=AI Resume Analyzer
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/AI_HR2
Environment="PATH=/path/to/AI_HR2/venv/bin"
ExecStart=/path/to/AI_HR2/venv/bin/streamlit run app/streamlit_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 2. 启动服务

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start resume-analyzer

# 开机自启
sudo systemctl enable resume-analyzer

# 查看状态
sudo systemctl status resume-analyzer
```

---

## 🌐 网络配置

### 国内用户加速

如果下载依赖缓慢，使用国内镜像源：

```bash
# 临时使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🔒 安全建议

### 1. 保护API Key

- ✅ 使用 `.env` 文件（已在 `.gitignore` 中）
- ✅ 不要在代码中硬编码API Key
- ✅ 定期轮换API Key
- ❌ 不要提交 `.env` 到Git

### 2. 文件上传限制

在 `streamlit_app.py` 中已限制文件类型：

```python
file_uploader(
    "选择简历文件",
    type=["pdf", "docx"],  # 只允许PDF和DOCX
    accept_multiple_files=False
)
```

### 3. 临时文件清理

系统会自动清理上传的临时文件：

```python
# 分析完成后删除临时文件
if os.path.exists(temp_path):
    os.remove(temp_path)
```

---

## 📊 性能优化

### 1. LLM调用优化

```python
# 使用批处理减少API调用
analysis_tasks = [
    self._analyze_technical(data),
    self._analyze_experience(data),
    self._analyze_project(data),
    self._analyze_soft_skill(data)
]
# 并行执行
await asyncio.gather(*analysis_tasks)
```

### 2. 缓存配置

Streamlit配置缓存：

```python
@st.cache_resource
def get_llm():
    return ChatZhipuAI(model="glm-4")
```

---

## 📝 部署检查清单

部署完成后，使用此清单验证：

- [ ] Python版本正确 (3.9+)
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装 (pip list)
- [ ] `.env` 文件已配置
- [ ] API Key有效
- [ ] 配置文件存在 (config/scoring.yaml)
- [ ] 测试全部通过 (pytest tests/)
- [ ] Streamlit应用可启动
- [ ] 可以访问 http://localhost:8501
- [ ] 上传简历功能正常
- [ ] 分析功能正常

---

## 🆘 获取帮助

如果遇到问题：

1. 查看 [README.md](README.md) - 项目概述
2. 查看 [tests/TEST_REPORT.md](tests/TEST_REPORT.md) - 测试报告
3. 查看 [docs/ARCHITECTURE_ANALYSIS.md](docs/ARCHITECTURE_ANALYSIS.md) - 架构文档
4. 提交 Issue 到项目仓库

---

**文档版本**: v1.0
**最后更新**: 2026-01-28
