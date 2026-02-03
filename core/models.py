# core/models.py
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, TypedDict
import uuid
from datetime import datetime


@dataclass
class PersonalInfo:
    """个人信息数据模型"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None


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

    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []
        if self.achievements is None:
            self.achievements = []


@dataclass
class Skill:
    """技能数据模型"""
    name: str
    level: str = "了解"  # "精通" | "熟练" | "熟悉" | "了解"
    verified: bool = False  # 是否在项目/工作经历中被验证


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
