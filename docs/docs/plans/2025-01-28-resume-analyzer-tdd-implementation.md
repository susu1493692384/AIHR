# Resume Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a multi-agent resume analysis system using LangChain and ZhipuAI that parses PDF/Word resumes, cleans data, analyzes across 4 dimensions (technical 25%, experience 20%, project 40%, soft-skills 15%), and generates structured JSON reports with optimization suggestions.

**Architecture:** Multi-agent system with 6 agents (Parsing, Cleaning, Analysis, Optimization, Report, Orchestrator) using LangGraph for workflow orchestration. Each agent uses specialized tools. Data flows: Upload → Parse → Clean → Parallel Analysis (4 dimensions) → Optimize → Report.

**Tech Stack:** Python 3.9+, LangChain, LangGraph, langchain-zhipu, PyPDF2, python-docx, Streamlit, pytest, YAML config

---

## Task 1: Project Initialization

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `pyproject.toml`

**Step 1: Create requirements.txt**

```bash
cat > requirements.txt << 'EOF'
# Core Framework
langchain>=0.1.0
langchain-core>=0.1.0
langchain-zhipu>=0.1.0
langgraph>=0.0.0

# File Parsing
PyPDF2>=3.0.0
python-docx>=1.0.0

# Frontend
streamlit>=1.28.0

# Tools
python-dotenv>=1.0.0
pyyaml>=6.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
EOF
```

**Step 2: Create .env.example**

```bash
cat > .env.example << 'EOF'
ZHIPU_API_KEY=your_zhipu_api_key_here
EOF
```

**Step 3: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db
EOF
```

**Step 4: Create pyproject.toml**

```bash
cat > pyproject.toml << 'EOF'
[project]
name = "resume-analyzer"
version = "0.1.0"
description = "AI-powered resume analysis system"
requires-python = ">=3.9"
dependencies = [
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "langchain-zhipu>=0.1.0",
    "langgraph>=0.0.0",
    "PyPDF2>=3.0.0",
    "python-docx>=1.0.0",
    "streamlit>=1.28.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
EOF
```

**Step 5: Create directory structure**

```bash
mkdir -p core agents tools/{parsing,cleaning,analysis} prompts utils config tests/{test_tools,test_agents} app docs/plans
```

**Step 6: Create __init__.py files**

```bash
touch core/__init__.py
touch agents/__init__.py
touch tools/__init__.py
touch tools/parsing/__init__.py
touch tools/cleaning/__init__.py
touch tools/analysis/__init__.py
touch prompts/__init__.py
touch utils/__init__.py
touch tests/__init__.py
touch tests/test_tools/__init__.py
touch tests/test_agents/__init__.py
```

**Step 7: Commit**

```bash
git add .
git commit -m "chore: initialize project structure and dependencies"
```

---

## Task 2: Core Data Models - PersonalInfo

**Files:**
- Create: `core/models.py`
- Test: `tests/test_models.py`

**Step 1: Write failing test for PersonalInfo**

```python
# tests/test_models.py
import pytest
from core.models import PersonalInfo
from datetime import datetime


def test_personal_info_creation_with_all_fields():
    """Test creating PersonalInfo with all fields"""
    info = PersonalInfo(
        name="张三",
        phone="13800138000",
        email="zhangsan@example.com",
        location="北京",
        birth_date="1990-01",
        gender="男"
    )
    assert info.name == "张三"
    assert info.phone == "13800138000"
    assert info.email == "zhangsan@example.com"
    assert info.location == "北京"
    assert info.birth_date == "1990-01"
    assert info.gender == "男"


def test_personal_info_creation_with_required_only():
    """Test creating PersonalInfo with only name"""
    info = PersonalInfo(name="李四")
    assert info.name == "李四"
    assert info.phone is None
    assert info.email is None


def test_personal_info_name_required():
    """Test that name is required"""
    with pytest.raises(TypeError):
        PersonalInfo()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_personal_info_creation_with_all_fields -v
```
Expected: `ImportError: cannot import name 'PersonalInfo' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class PersonalInfo:
    """个人信息数据模型"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add PersonalInfo data model"
```

---

## Task 3: Core Data Models - Education

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for Education**

```python
# tests/test_models.py (add to existing file)
from core.models import Education


def test_education_creation_with_all_fields():
    """Test creating Education with all fields"""
    edu = Education(
        school="清华大学",
        major="计算机科学与技术",
        degree="本科",
        start_time="2018-09",
        end_time="2022-06",
        gpa="3.8/4.0",
        description="主修课程：数据结构、算法、操作系统"
    )
    assert edu.school == "清华大学"
    assert edu.major == "计算机科学与技术"
    assert edu.degree == "本科"
    assert edu.start_time == "2018-09"
    assert edu.end_time == "2022-06"
    assert edu.gpa == "3.8/4.0"
    assert "数据结构" in edu.description


def test_education_creation_without_optional_fields():
    """Test creating Education without optional fields"""
    edu = Education(
        school="北京大学",
        major="软件工程",
        degree="硕士",
        start_time="2020-09"
    )
    assert edu.end_time is None
    assert edu.gpa is None
    assert edu.description is None
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_education_creation_with_all_fields -v
```
Expected: `ImportError: cannot import name 'Education' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
@dataclass
class Education:
    """教育经历数据模型"""
    school: str
    major: str
    degree: str  # "本科" | "硕士" | "博士" | "大专"
    start_time: str  # "YYYY-MM" format
    end_time: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_education_creation_with_all_fields -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add Education data model"
```

---

## Task 4: Core Data Models - WorkExperience

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for WorkExperience**

```python
# tests/test_models.py (add to existing file)
from core.models import WorkExperience


def test_work_experience_creation():
    """Test creating WorkExperience"""
    exp = WorkExperience(
        company="阿里巴巴",
        position="后端工程师",
        start_time="2022-07",
        end_time="至今",
        industry="互联网",
        company_scale="10000+",
        description="负责电商平台后端开发",
        achievements=["提升系统性能50%", "重构核心模块"]
    )
    assert exp.company == "阿里巴巴"
    assert exp.position == "后端工程师"
    assert exp.start_time == "2022-07"
    assert exp.end_time == "至今"
    assert exp.industry == "互联网"
    assert len(exp.achievements) == 2


def test_work_experience_default_values():
    """Test WorkExperience with default values"""
    exp = WorkExperience(
        company="腾讯",
        position="前端工程师",
        start_time="2021-01",
        description="负责前端页面开发"
    )
    assert exp.end_time is None
    assert exp.industry is None
    assert exp.achievements == []
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_work_experience_creation -v
```
Expected: `ImportError: cannot import name 'WorkExperience' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
from typing import List


@dataclass
class WorkExperience:
    """工作经历数据模型"""
    company: str
    position: str
    start_time: str
    end_time: Optional[str] = None
    industry: Optional[str] = None
    company_scale: Optional[str] = None
    description: str = ""
    achievements: List[str] = None

    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_work_experience_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add WorkExperience data model"
```

---

## Task 5: Core Data Models - Project

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for Project**

```python
# tests/test_models.py (add to existing file)
from core.models import Project


def test_project_creation():
    """Test creating Project"""
    project = Project(
        name="交易系统重构",
        role="核心开发",
        start_time="2023-01",
        end_time="2023-06",
        team_size=8,
        tech_stack=["Java", "Spring", "MySQL", "Redis"],
        description="重构交易系统提升性能",
        achievements=["响应时间降低60%", "吞吐量提升3倍"],
        complexity_indicators={"has_high_concurrency": True, "team_size": 8}
    )
    assert project.name == "交易系统重构"
    assert project.role == "核心开发"
    assert len(project.tech_stack) == 4
    assert project.team_size == 8
    assert project.complexity_indicators["has_high_concurrency"] is True


def test_project_with_minimal_fields():
    """Test Project with minimal fields"""
    project = Project(
        name="个人博客",
        role="独立开发",
        start_time="2023-01",
        tech_stack=["Python", "Django"],
        description="个人技术博客"
    )
    assert project.team_size is None
    assert project.achievements == []
    assert project.complexity_indicators == {}
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_project_creation -v
```
Expected: `ImportError: cannot import name 'Project' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
from typing import Dict, Any


@dataclass
class Project:
    """项目经验数据模型"""
    name: str
    role: str
    start_time: str
    end_time: Optional[str] = None
    team_size: Optional[int] = None
    tech_stack: List[str] = None
    description: str = ""
    achievements: List[str] = None
    complexity_indicators: Dict[str, Any] = None

    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []
        if self.achievements is None:
            self.achievements = []
        if self.complexity_indicators is None:
            self.complexity_indicators = {}
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_project_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add Project data model"
```

---

## Task 6: Core Data Models - Skill

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for Skill**

```python
# tests/test_models.py (add to existing file)
from core.models import Skill


def test_skill_creation():
    """Test creating Skill"""
    skill = Skill(
        name="Python",
        category="language",
        level="熟练",
        verified=True,
        market_demand="A"
    )
    assert skill.name == "Python"
    assert skill.category == "language"
    assert skill.level == "熟练"
    assert skill.verified is True
    assert skill.market_demand == "A"


def test_skill_default_values():
    """Test Skill with default values"""
    skill = Skill(name="Java", category="language")
    assert skill.level == "了解"
    assert skill.verified is False
    assert skill.market_demand == "C"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_skill_creation -v
```
Expected: `ImportError: cannot import name 'Skill' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
@dataclass
class Skill:
    """技能数据模型"""
    name: str
    category: str  # "language" | "framework" | "database" | "tool" | "other"
    level: str = "了解"  # "精通" | "熟练" | "熟悉" | "了解"
    verified: bool = False  # 是否在项目/工作经历中被验证
    market_demand: str = "C"  # "A" | "B" | "C" | "D"
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_skill_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add Skill data model"
```

---

## Task 7: Core Data Models - ParsedResume

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for ParsedResume**

```python
# tests/test_models.py (add to existing file)
from core.models import ParsedResume
from datetime import datetime


def test_parsed_resume_creation():
    """Test creating ParsedResume"""
    resume = ParsedResume(
        resume_id="test-001",
        file_name="resume.pdf",
        file_type="pdf",
        parse_time=datetime(2025, 1, 28, 10, 0, 0),
        personal_info=PersonalInfo(name="张三"),
        education=[],
        work_experience=[],
        projects=[],
        skills=[]
    )
    assert resume.resume_id == "test-001"
    assert resume.file_name == "resume.pdf"
    assert resume.file_type == "pdf"
    assert resume.personal_info.name == "张三"
    assert len(resume.education) == 0


def test_parsed_resume_with_data():
    """Test ParsedResume with actual data"""
    resume = ParsedResume(
        file_name="test.pdf",
        file_type="pdf",
        personal_info=PersonalInfo(name="李四"),
        education=[
            Education(
                school="清华大学",
                major="计算机",
                degree="本科",
                start_time="2018-09"
            )
        ],
        skills=[
            Skill(name="Python", category="language", level="熟练")
        ]
    )
    assert resume.resume_id is not None  # Auto-generated UUID
    assert len(resume.education) == 1
    assert len(resume.skills) == 1
    assert resume.education[0].school == "清华大学"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_parsed_resume_creation -v
```
Expected: `ImportError: cannot import name 'ParsedResume' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
import uuid
from datetime import datetime


@dataclass
class ParsedResume:
    """解析后的简历数据模型"""
    resume_id: str = None
    file_name: str = ""
    file_type: str = ""
    parse_time: datetime = None
    personal_info: PersonalInfo = None
    education: List[Education] = None
    work_experience: List[WorkExperience] = None
    projects: List[Project] = None
    skills: List[Skill] = None
    others: Dict[str, Any] = None

    def __post_init__(self):
        if self.resume_id is None:
            self.resume_id = str(uuid.uuid4())
        if self.parse_time is None:
            self.parse_time = datetime.now()
        if self.education is None:
            self.education = []
        if self.work_experience is None:
            self.work_experience = []
        if self.projects is None:
            self.projects = []
        if self.skills is None:
            self.skills = []
        if self.others is None:
            self.others = {}
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_parsed_resume_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add ParsedResume data model"
```

---

## Task 8: Core Data Models - AnalysisResult and ResumeAnalysisReport

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for AnalysisResult**

```python
# tests/test_models.py (add to existing file)
from core.models import AnalysisResult, ResumeAnalysisReport


def test_analysis_result_creation():
    """Test creating AnalysisResult"""
    result = AnalysisResult(
        dimension="technical",
        score=85.0,
        detail_scores={"广度": 25, "深度": 22, "相关性": 18, "热度": 20},
        insights=["技能覆盖面广", "有精通级技能"],
        highlights=["精通Python和Java"],
        weaknesses=["缺少数据库技能"],
        raw_analysis={}
    )
    assert result.dimension == "technical"
    assert result.score == 85.0
    assert len(result.insights) == 2
    assert 0 <= result.score <= 100


def test_resume_analysis_report_creation():
    """Test creating ResumeAnalysisReport"""
    report = ResumeAnalysisReport(
        resume_id="test-001",
        generate_time=datetime(2025, 1, 28),
        resume_data=None,  # Will use CleanedResume later
        technical_analysis=AnalysisResult(
            dimension="technical",
            score=80.0,
            detail_scores={},
            insights=[],
            highlights=[],
            weaknesses=[],
            raw_analysis={}
        ),
        experience_analysis=AnalysisResult(
            dimension="experience",
            score=75.0,
            detail_scores={},
            insights=[],
            highlights=[],
            weaknesses=[],
            raw_analysis={}
        ),
        project_analysis=AnalysisResult(
            dimension="project",
            score=85.0,
            detail_scores={},
            insights=[],
            highlights=[],
            weaknesses=[],
            raw_analysis={}
        ),
        soft_skill_analysis=AnalysisResult(
            dimension="soft_skill",
            score=70.0,
            detail_scores={},
            insights=[],
            highlights=[],
            weaknesses=[],
            raw_analysis={}
        ),
        overall_score=78.5,
        score_breakdown={
            "technical": 80.0,
            "experience": 75.0,
            "project": 85.0,
            "soft_skill": 70.0
        },
        optimization_suggestions=[],
        hr_summary="资深后端工程师，技术扎实，项目经验丰富",
        candidate_summary="技术能力突出，建议加强软技能表达",
        confidence=0.85
    )
    assert report.resume_id == "test-001"
    assert report.overall_score == 78.5
    assert report.technical_analysis.score == 80.0
    assert 0 <= report.confidence <= 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_analysis_result_creation -v
```
Expected: `ImportError: cannot import name 'AnalysisResult' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
@dataclass
class AnalysisResult:
    """单维度分析结果数据模型"""
    dimension: str  # "technical" | "experience" | "project" | "soft_skill"
    score: float  # 0-100
    detail_scores: Dict[str, float]  # 子项评分
    insights: List[str]  # 关键发现
    highlights: List[str]  # 亮点
    weaknesses: List[str]  # 不足
    raw_analysis: Dict[str, Any]  # 原始分析数据


@dataclass
class CleanedResume:
    """数据清洗后的简历"""
    original: ParsedResume
    cleaned_data: ParsedResume
    cleaning_report: Dict[str, Any] = None

    def __post_init__(self):
        if self.cleaning_report is None:
            self.cleaning_report = {
                "operations": [],
                "fixes": [],
                "warnings": [],
                "missing_fields": []
            }


@dataclass
class ResumeAnalysisReport:
    """完整分析报告数据模型"""
    resume_id: str
    generate_time: datetime
    resume_data: CleanedResume
    technical_analysis: AnalysisResult
    experience_analysis: AnalysisResult
    project_analysis: AnalysisResult
    soft_skill_analysis: AnalysisResult
    overall_score: float
    score_breakdown: Dict[str, float]
    optimization_suggestions: List[Dict[str, str]]
    hr_summary: str
    candidate_summary: str
    confidence: float  # 0-1，分析可信度
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_analysis_result_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add AnalysisResult and ResumeAnalysisReport models"
```

---

## Task 9: LangGraph State Definition

**Files:**
- Modify: `core/models.py`
- Modify: `tests/test_models.py`

**Step 1: Write failing test for State**

```python
# tests/test_models.py (add to existing file)
from core.models import ResumeAnalysisState


def test_state_creation():
    """Test creating ResumeAnalysisState"""
    state = ResumeAnalysisState(
        resume_file_path="path/to/resume.pdf",
        parsed_resume=None,
        cleaned_resume=None,
        technical_result=None,
        experience_result=None,
        project_result=None,
        soft_skill_result=None,
        final_report=None,
        errors=[],
        current_step="",
        retry_count=0
    )
    assert state["resume_file_path"] == "path/to/resume.pdf"
    assert state["current_step"] == ""
    assert state["retry_count"] == 0
    assert isinstance(state, dict)


def test_state_is_mutable():
    """Test that State is mutable (TypedDict)"""
    state = ResumeAnalysisState(
        resume_file_path="test.pdf"
    )
    state["current_step"] = "parsing"
    state["retry_count"] = 1
    assert state["current_step"] == "parsing"
    assert state["retry_count"] == 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_state_creation -v
```
Expected: `ImportError: cannot import name 'ResumeAnalysisState' from 'core.models'`

**Step 3: Write minimal implementation**

```python
# core/models.py (add to existing file)
from typing import TypedDict, Optional


class ResumeAnalysisState(TypedDict):
    """Agent间共享状态"""
    resume_file_path: str
    parsed_resume: Optional[ParsedResume]
    cleaned_resume: Optional[CleanedResume]
    technical_result: Optional[AnalysisResult]
    experience_result: Optional[AnalysisResult]
    project_result: Optional[AnalysisResult]
    soft_skill_result: Optional[AnalysisResult]
    final_report: Optional[ResumeAnalysisReport]
    errors: List[str]
    current_step: str
    retry_count: int
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py::test_state_creation -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: add ResumeAnalysisState TypedDict"
```

---

## Task 10: Run all model tests and verify

**Step 1: Run all tests**

```bash
pytest tests/test_models.py -v --cov=core/models --cov-report=term-missing
```

Expected: All tests PASS, coverage > 90%

**Step 2: View test summary**

```bash
pytest tests/test_models.py -v
```

Expected output:
```
tests/test_models.py::test_personal_info_creation_with_all_fields PASSED
tests/test_models.py::test_personal_info_creation_with_required_only PASSED
tests/test_models.py::test_personal_info_name_required PASSED
tests/test_models.py::test_education_creation_with_all_fields PASSED
tests/test_models.py::test_education_creation_without_optional_fields PASSED
tests/test_models.py::test_work_experience_creation PASSED
tests/test_models.py::test_work_experience_default_values PASSED
tests/test_models.py::test_project_creation PASSED
tests/test_models.py::test_project_with_minimal_fields PASSED
tests/test_models.py::test_skill_creation PASSED
tests/test_models.py::test_skill_default_values PASSED
tests/test_models.py::test_parsed_resume_creation PASSED
tests/test_models.py::test_parsed_resume_with_data PASSED
tests/test_models.py::test_analysis_result_creation PASSED
tests/test_models.py::test_resume_analysis_report_creation PASSED
tests/test_models.py::test_state_creation PASSED
tests/test_models.py::test_state_is_mutable PASSED
```

**Step 3: Commit if all pass**

```bash
git add .
git commit -m "test: verify all core data models with 100% coverage"
```

---

## Task 11: Configuration System - ScoreConfig

**Files:**
- Create: `core/config.py`
- Create: `config/scoring.yaml`
- Test: `tests/test_config.py`

**Step 1: Write failing test for ScoreConfig**

```python
# tests/test_config.py
import pytest
from core.config import ScoreConfig


def test_score_config_default_weights():
    """Test default scoring weights"""
    config = ScoreConfig()
    assert config.weights["technical"] == 0.25
    assert config.weights["experience"] == 0.20
    assert config.weights["project"] == 0.40
    assert config.weights["soft_skill"] == 0.15
    assert sum(config.weights.values()) == 1.0


def test_score_config_from_yaml():
    """Test loading ScoreConfig from YAML"""
    config = ScoreConfig.from_yaml("config/scoring.yaml")
    assert "weights" in config.__dict__
    assert config.weights["project"] == 0.40


def test_skill_demand_classification():
    """Test skill demand classification"""
    config = ScoreConfig()
    assert config.skill_demand.get("Python") in ["A", "B", "C", "D"]
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py::test_score_config_default_weights -v
```
Expected: `ImportError: cannot import name 'ScoreConfig' from 'core.config'`

**Step 3: Create YAML config file**

```yaml
# config/scoring.yaml
# 评分权重配置
weights:
  technical: 0.25   # 技术能力 25%
  experience: 0.20  # 经验背景 20%
  project: 0.40     # 项目经验 40%
  soft_skill: 0.15  # 软技能 15%

# 技能热度配置
skill_demand:
  # A类 - 热门技术
  Python: A
  Go: A
  Rust: A
  Kubernetes: A
  Docker: A
  微服务: A
  分布式: A
  大模型: A
  LLM: A

  # B类 - 主流技术
  Java: B
  JavaScript: B
  TypeScript: B
  React: B
  Vue: B
  Spring: B
  MySQL: B
  Redis: B
  Kafka: B

  # C类 - 常规技术
  "C++": C
  C#: C
  PHP: C
  Oracle: C

  # D类 - 传统技术
  Struts: D
  JSP: D
  VB: D

# 学校分级配置
school_tier:
  985:
    - 清华大学
    - 北京大学
    - 复旦大学
    - 上海交通大学
    - 浙江大学
    - 中国科学技术大学
    - 南京大学
    - 西安交通大学
    - 哈尔滨工业大学
  211:
    - 北京理工大学
    - 北京航空航天大学
    - 同济大学
    - 南开大学
    - 天津大学
    # ... more 211 schools
```

**Step 4: Write minimal implementation**

```python
# core/config.py
from dataclasses import dataclass, field
from typing import Dict
import yaml
from pathlib import Path


@dataclass
class ScoreConfig:
    """评分配置类"""
    weights: Dict[str, float] = field(default_factory=lambda: {
        "technical": 0.25,
        "experience": 0.20,
        "project": 0.40,
        "soft_skill": 0.15
    })
    skill_demand: Dict[str, str] = field(default_factory=dict)
    school_tier: Dict[str, list] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str) -> "ScoreConfig":
        """从YAML文件加载配置"""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")

        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            weights=data.get("weights", {}),
            skill_demand=data.get("skill_demand", {}),
            school_tier=data.get("school_tier", {})
        )

    def to_yaml(self, path: str) -> None:
        """保存配置到YAML文件"""
        data = {
            "weights": self.weights,
            "skill_demand": self.skill_demand,
            "school_tier": self.school_tier
        }

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def get_school_tier(self, school_name: str) -> str:
        """获取学校层次"""
        for tier, schools in self.school_tier.items():
            if any(s in school_name for s in schools):
                return tier
        return "普通"
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```
Expected: All 3 tests PASS

**Step 6: Commit**

```bash
git add core/config.py config/scoring.yaml tests/test_config.py
git commit -m "feat: add ScoreConfig with YAML support"
```

---

## Task 12: Error Handling System

**Files:**
- Create: `utils/error_handler.py`
- Test: `tests/test_error_handler.py`

**Step 1: Write failing test for custom exceptions**

```python
# tests/test_error_handler.py
import pytest
from utils.error_handler import (
    ResumeAnalyzerError,
    FileParseError,
    DataValidationError,
    LLMError,
    ScoringError
)


def test_resume_analyzer_error():
    """Test base exception"""
    with pytest.raises(ResumeAnalyzerError):
        raise ResumeAnalyzerError("Test error")


def test_file_parse_error():
    """Test FileParseError"""
    with pytest.raises(FileParseError) as exc_info:
        raise FileParseError("Cannot parse file")
    assert "Cannot parse file" in str(exc_info.value)


def test_error_inheritance():
    """Test all errors inherit from ResumeAnalyzerError"""
    assert issubclass(FileParseError, ResumeAnalyzerError)
    assert issubclass(DataValidationError, ResumeAnalyzerError)
    assert issubclass(LLMError, ResumeAnalyzerError)
    assert issubclass(ScoringError, ResumeAnalyzerError)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_error_handler.py::test_resume_analyzer_error -v
```
Expected: `ImportError`

**Step 3: Write minimal implementation**

```python
# utils/error_handler.py
"""统一错误处理器"""


class ResumeAnalyzerError(Exception):
    """简历分析器基础异常"""
    pass


class FileParseError(ResumeAnalyzerError):
    """文件解析异常"""
    pass


class DataValidationError(ResumeAnalyzerError):
    """数据验证异常"""
    pass


class LLMError(ResumeAnalyzerError):
    """LLM调用异常"""
    pass


class ScoringError(ResumeAnalyzerError):
    """评分异常"""
    pass
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_error_handler.py -v
```
Expected: All tests PASS

**Step 5: Commit**

```bash
git add utils/error_handler.py tests/test_error_handler.py
git commit -m "feat: add custom exception classes"
```

---

## Task 13: ErrorHandler Utility Class

**Files:**
- Modify: `utils/error_handler.py`
- Modify: `tests/test_error_handler.py`

**Step 1: Write failing test for ErrorHandler**

```python
# tests/test_error_handler.py (add to existing file)
from utils.error_handler import ErrorHandler
import os


def test_error_handler_handle_error():
    """Test error handling"""
    try:
        raise FileNotFoundError("File not found: test.pdf")
    except Exception as e:
        result = ErrorHandler.handle_error(e, "parsing")

    assert result["error_type"] == "FileNotFoundError"
    assert result["context"] == "parsing"
    assert "timestamp" in result
    assert "user_message" in result


def test_error_handler_with_value_error():
    """Test handling ValueError"""
    try:
        raise ValueError("Invalid data format")
    except Exception as e:
        result = ErrorHandler.handle_error(e, "validation")

    assert result["error_type"] == "ValueError"
    assert result["user_message"] == "数据格式错误"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_error_handler.py::test_error_handler_handle_error -v
```
Expected: `AttributeError: type object 'ErrorHandler' has no attribute 'handle_error'`

**Step 3: Write implementation**

```python
# utils/error_handler.py (add to existing file)
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorHandler:
    """错误处理器"""

    ERROR_MAPPING = {
        FileNotFoundError: ("文件不存在", "文件未找到"),
        ValueError: ("数据格式错误", "输入数据格式不正确"),
        KeyError: ("缺少必需字段", "数据中缺少必需的字段"),
        TypeError: ("类型错误", "数据类型不匹配"),
    }

    @classmethod
    def handle_error(
        cls,
        error: Exception,
        context: str = ""
    ) -> Dict[str, Any]:
        """统一处理错误"""
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)

        error_type = type(error)
        error_info = cls.ERROR_MAPPING.get(
            error_type,
            ("未知错误", str(error))
        )

        return {
            "error_type": error_type.__name__,
            "error_message": str(error),
            "user_message": error_info[0],
            "detail_message": error_info[1],
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_error_handler.py::test_error_handler_handle_error -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add utils/error_handler.py tests/test_error_handler.py
git commit -m "feat: add ErrorHandler utility class"
```

---

## Task 14: DataValidator Utility Class

**Files:**
- Modify: `utils/error_handler.py`
- Create: `utils/validation.py`
- Test: `tests/test_validation.py`

**Step 1: Write failing test for DataValidator**

```python
# tests/test_validation.py
import pytest
from utils.validation import DataValidator
from utils.error_handler import DataValidationError, ScoringError
import tempfile


def test_validate_file_path_success():
    """Test validating existing file"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        temp_path = f.name

    try:
        result = DataValidator.validate_file_path(temp_path)
        assert result is True
    finally:
        os.unlink(temp_path)


def test_validate_file_path_empty():
    """Test validating empty file path"""
    with pytest.raises(DataValidationError):
        DataValidator.validate_file_path("")


def test_validate_file_path_not_exists():
    """Test validating non-existent file"""
    with pytest.raises(FileNotFoundError):
        DataValidator.validate_file_path("nonexistent.pdf")


def test_validate_file_type_allowed():
    """Test validating allowed file type"""
    assert DataValidator.validate_file_type("resume.pdf", [".pdf", ".docx"]) is True


def test_validate_file_type_not_allowed():
    """Test validating disallowed file type"""
    with pytest.raises(DataValidationError):
        DataValidator.validate_file_type("resume.txt", [".pdf", ".docx"])


def test_validate_score_valid():
    """Test validating valid score"""
    assert DataValidator.validate_score(85.5, "technical") is True
    assert DataValidator.validate_score(0, "technical") is True
    assert DataValidator.validate_score(100, "technical") is True


def test_validate_score_invalid_type():
    """Test validating invalid score type"""
    with pytest.raises(ScoringError):
        DataValidator.validate_score("85", "technical")


def test_validate_score_out_of_range():
    """Test validating score out of range"""
    with pytest.raises(ScoringError):
        DataValidator.validate_score(150, "technical")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_validation.py::test_validate_file_path_success -v
```
Expected: `ImportError`

**Step 3: Write implementation**

```python
# utils/validation.py
"""数据验证器"""
import os
from utils.error_handler import DataValidationError, ScoringError


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """验证文件路径"""
        if not file_path:
            raise DataValidationError("文件路径为空")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        return True

    @staticmethod
    def validate_file_type(file_path: str, allowed_types: list) -> bool:
        """验证文件类型"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_types:
            raise DataValidationError(
                f"不支持的文件类型: {ext}，"
                f"支持的类型: {', '.join(allowed_types)}"
            )
        return True

    @staticmethod
    def validate_score(score: float, dimension: str) -> bool:
        """验证分数有效性"""
        if not isinstance(score, (int, float)):
            raise ScoringError(f"{dimension}分数必须是数字")
        if not 0 <= score <= 100:
            raise ScoringError(f"{dimension}分数必须在0-100之间")
        return True
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_validation.py -v
```
Expected: All tests PASS

**Step 5: Commit**

```bash
git add utils/validation.py tests/test_validation.py
git commit -m "feat: add DataValidator utility class"
```

---

## Phase 1 Complete Checkpoint

**Step 1: Run all tests**

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

Expected: All tests PASS, coverage > 85%

**Step 2: Verify project structure**

```bash
find . -type f -name "*.py" | grep -E "(core|utils|tests)" | sort
```

Expected output includes:
```
./core/__init__.py
./core/config.py
./core/models.py
./utils/__init__.py
./utils/error_handler.py
./utils/validation.py
./tests/__init__.py
./tests/test_config.py
./tests/test_error_handler.py
./tests/test_models.py
./tests/test_validation.py
```

**Step 3: Final commit**

```bash
git add .
git commit -m "chore: phase 1 complete - core foundation ready"
```

---

## Next Phases Summary

The following phases will follow the same TDD pattern:

### Phase 2: Parsing Tools (FileParserTool, TextExtractorTool, StructureMapperTool)
### Phase 3: Cleaning Tools (DateNormalizer, Deduplication, MissingValueHandler, TextNormalization)
### Phase 4: Analysis Tools (Technical, Experience, Project, SoftSkill analyzers)
### Phase 5: Agent Layer (BaseAgent, ParsingAgent, CleaningAgent, AnalysisAgent, etc.)
### Phase 6: Prompt Templates (All prompt classes)
### Phase 7: Frontend (Streamlit app)
### Phase 8: Integration Tests

---

## Developer Notes

### TDD Workflow Reminder
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while keeping tests green
4. **Commit**: Small, frequent commits

### Key Principles
- **DRY**: Don't Repeat Yourself - extract common patterns
- **YAGNI**: You Aren't Gonna Need It - only implement what tests require
- **KISS**: Keep It Simple, Stupid - simple solutions preferred

### Testing Best Practices
- One assert per test when possible
- Test naming: `test_<function>_<scenario>_<expected_result>()`
- Mock external dependencies (LLM, file I/O)
- Test both happy path and error cases

### Git Commit Convention
- `feat:` new feature
- `fix:` bug fix
- `test:` adding/updating tests
- `refactor:` code refactoring
- `chore:` maintenance tasks
- `docs:` documentation updates

---

**End of Phase 1 Implementation Plan**

This document contains the complete TDD-based implementation plan for Phase 1 (Foundation). Continue with `superpowers:executing-plans` for automated execution or continue manually following this pattern.
