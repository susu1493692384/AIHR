# tools/parsing/structure_mapper.py
"""结构映射工具 - 标准化和优化LLM解析出的简历数据"""
import re
import json
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from core.models import (
    PersonalInfo, Education, WorkExperience, Project, Skill, ParsedResume
)


class StructureMapperTool:
    """结构映射工具类 - 将LLM解析的原始数据标准化为规范格式"""

    # 字段映射表（中文/不规则 → 标准英文字段名）
    FIELD_MAPPING = {
        # 个人信息相关
        "个人信息": "personal_info",
        "基本信息": "personal_info",
        "姓名": "name",
        "name": "name",
        "性别": "gender",
        "年龄": "age",
        "出生日期": "birth_date",
        "生日": "birth_date",
        "birth": "birth_date",
        "邮箱": "email",
        "email": "email",
        "电子邮件": "email",
        "邮件": "email",
        "电话": "phone",
        "手机": "phone",
        "手机号": "phone",
        "联系方式": "phone",
        "tel": "phone",
        "手机号码": "phone",
        "地址": "location",
        "住址": "location",
        "所在地": "location",
        "location": "location",

        # 教育经历相关
        "教育背景": "education",
        "教育经历": "education",
        "学历": "education",
        "学习经历": "education",
        "education": "education",
        "学校": "school",
        "school": "school",
        "university": "school",
        "大学": "school",
        "院校": "school",
        "专业": "major",
        "专业名称": "major",
        "major": "major",
        "学位": "degree",
        "degree": "degree",
        "学历层次": "degree",
        "学历学位": "degree",
        "入学时间": "start_time",
        "开始时间": "start_time",
        "开始日期": "start_time",
        "入职日期": "start_time",
        "起始日期": "start_time",
        "start_date": "start_time",
        "毕业时间": "end_time",
        "结束时间": "end_time",
        "结束日期": "end_time",
        "离职日期": "end_time",
        "毕业日期": "end_time",
        "毕业年份": "end_time",
        "end_date": "end_time",
        "gpa": "gpa",
        "GPA": "gpa",
        "绩点": "gpa",
        "描述": "description",
        "简介": "description",

        # 工作经历相关
        "工作经历": "work_experience",
        "工作经验": "work_experience",
        "工作": "work_experience",
        "职业经历": "work_experience",
        "employment": "work_experience",
        "work_experience": "work_experience",
        "公司": "company",
        "company": "company",
        "雇主": "company",
        "employer": "company",
        "单位": "company",
        "企业": "company",
        "职位": "position",
        "position": "position",
        "岗位": "position",
        "职务": "position",
        "title": "position",
        "部门": "department",
        "industry": "industry",
        "行业": "industry",
        "公司规模": "company_scale",
        "开始时间": "start_time",
        "入职时间": "start_time",
        "开始日期": "start_time",
        "入职日期": "start_time",
        "start_date": "start_time",
        "结束时间": "end_time",
        "离职时间": "end_time",
        "结束日期": "end_time",
        "离职日期": "end_time",
        "end_date": "end_time",
        "工作描述": "description",
        "职责": "description",
        "工作内容": "description",
        "职责描述": "description",
        "成就": "achievements",
        "业绩": "achievements",
        "工作成果": "achievements",

        # 项目经验相关
        "项目经验": "projects",
        "项目": "projects",
        "project": "projects",
        "项目经历": "projects",
        "项目名称": "name",
        "项目名": "name",
        "project_name": "name",  # 添加project_name映射
        "name": "name",
        "项目开始时间": "start_time",
        "项目开始日期": "start_time",
        "project_start_date": "start_time",
        "项目结束时间": "end_time",
        "项目结束日期": "end_time",
        "project_end_date": "end_time",
        "角色": "role",
        "role": "role",
        "职位": "role",
        "职责": "role",
        "团队规模": "team_size",
        "团队人数": "team_size",
        "技术栈": "tech_stack",
        "技术": "tech_stack",
        "技术列表": "tech_stack",
        "stack": "tech_stack",
        "项目描述": "description",
        "描述": "description",
        "简介": "description",
        "项目成果": "achievements",
        "项目成就": "achievements",
        "复杂度指标": "complexity_indicators",

        # 技能相关
        "技能": "skills",
        "专业技能": "skills",
        "技能特长": "skills",
        "skill": "skills",
        "技能名称": "name",
        "name": "name",
        "技能类别": "category",
        "分类": "category",
        "熟练度": "level",
        "掌握程度": "level",
        "技能水平": "level",

        # 证书相关
        "证书": "certificates",
        "资格证书": "certificates",
        "资质": "certificates",
        "certification": "certificates",
        "认证": "certificates",

        # 语言相关
        "语言": "languages",
        "语言能力": "languages",
        "外语": "languages",
        "language": "languages",
        "外语能力": "languages",

        # 自我评价
        "自我评价": "self_evaluation",
        "自我介绍": "self_evaluation",
        "个人评价": "self_evaluation",
        "summary": "self_evaluation",
        "个人简介": "self_evaluation",
        "评价": "self_evaluation",
    }

    # 学位标准化映射
    DEGREE_NORMALIZATION = {
        "博士": "博士",
        "phd": "博士",
        "ph.d": "博士",
        "硕士": "硕士",
        "master": "硕士",
        "研究生": "硕士",
        "本科": "本科",
        "bachelor": "本科",
        "b.s": "本科",
        "b.a": "本科",
        "学士": "本科",
        "大专": "大专",
        "专科": "大专",
        "associate": "大专",
        "高职": "大专",
        "高中": "高中",
        "中专": "中专",
    }

    # 技能等级标准化
    SKILL_LEVEL_MAPPING = {
        "精通": "精通",
        "expert": "精通",
        "熟练": "熟练",
        "proficient": "熟练",
        "熟悉": "熟悉",
        "familiar": "熟悉",
        "了解": "了解",
        "know": "了解",
        "入门": "了解",
        "beginner": "了解",
    }

    # 项目角色标准化映射
    PROJECT_ROLE_MAPPING = {
        # 标准角色（直接使用）
        "负责人": "负责人",
        "主导": "主导",
        "核心": "核心开发者",
        "核心开发者": "核心开发者",
        "开发": "开发者",
        "开发者": "开发者",
        "参与": "参与者",
        "参与者": "参与者",
        "协助": "参与者",

        # 英文角色
        "lead": "负责人",
        "leader": "负责人",
        "owner": "负责人",
        "principal": "主导",
        "core": "核心开发者",
        "senior": "核心开发者",
        "developer": "开发者",
        "dev": "开发者",
        "member": "参与者",
        "assistant": "参与者",
        "contributor": "参与者",
    }

    # 项目角色推断关键词（用于从职责描述中推断角色）
    PROJECT_ROLE_INFERENCE_KEYWORDS = {
        # 负责人特征词（最高优先级）
        "负责人": ["独立", "从0到1", "负责整个", "搭建系统", "构建系统", "设计架构"],
        # 主导特征词
        "主导": ["主导", "带领", "带领团队"],
        # 核心开发者特征词
        "核心开发者": ["开发", "实现", "构建", "训练", "优化", "完成", "编写", "负责"],
        # 参与者特征词
        "参与者": ["协助", "参与", "采集", "标注", "处理", "维护", "测试"],
    }

    @staticmethod
    def normalize_parsed_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化LLM解析出的原始数据

        Args:
            parsed_data: LLM解析出的原始字典数据

        Returns:
            标准化后的数据
        """
        if not parsed_data:
            return {}

        # 应用字段映射
        mapped_data = StructureMapperTool._apply_field_mapping(parsed_data)

        # 数据类型规范化
        normalized_data = StructureMapperTool._normalize_data_types(mapped_data)

        # 数据验证和修复
        validated_data = StructureMapperTool._validate_and_fix(normalized_data)

        return validated_data

    @staticmethod
    def _apply_field_mapping(obj: Any) -> Any:
        """
        递归应用字段映射规则

        Args:
            obj: 任意类型的对象（字典、列表或基本类型）

        Returns:
            映射后的对象
        """
        if isinstance(obj, dict):
            mapped = {}
            for key, value in obj.items():
                # 去除字段名两端的空格并应用映射规则
                clean_key = key.strip() if isinstance(key, str) else key
                mapped_key = StructureMapperTool.FIELD_MAPPING.get(clean_key, clean_key)
                # 递归处理嵌套结构
                mapped[mapped_key] = StructureMapperTool._apply_field_mapping(value)
            return mapped
        elif isinstance(obj, list):
            return [StructureMapperTool._apply_field_mapping(item) for item in obj]
        else:
            return obj

    @staticmethod
    def _normalize_data_types(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        规范化数据类型

        处理：
        - 日期格式标准化 (YYYY-MM)
        - 枚举值标准化
        - 数组字段确保为列表
        - 字符串去除多余空格

        Args:
            data: 字段映射后的数据

        Returns:
            数据类型规范化后的数据
        """
        if not isinstance(data, dict):
            return data

        normalized = {}

        for key, value in data.items():
            if key == "personal_info" and isinstance(value, dict):
                # 处理个人信息
                normalized[key] = StructureMapperTool._normalize_personal_info(value)

            elif key == "education" and isinstance(value, list):
                # 处理教育经历
                normalized[key] = [
                    StructureMapperTool._normalize_education(edu) for edu in value
                ]

            elif key == "work_experience" and isinstance(value, list):
                # 处理工作经历
                normalized[key] = [
                    StructureMapperTool._normalize_work_exp(work) for work in value
                ]

            elif key == "projects" and isinstance(value, list):
                # 处理项目经验
                normalized[key] = [
                    StructureMapperTool._normalize_project(proj) for proj in value
                ]

            elif key == "skills" and isinstance(value, list):
                # 处理技能
                normalized[key] = [
                    StructureMapperTool._normalize_skill(skill) for skill in value
                ]

            else:
                # 其他字段直接保留（去除字符串首尾空格）
                normalized[key] = StructureMapperTool._clean_string(value)

        return normalized

    @staticmethod
    def _normalize_personal_info(info: Dict[str, Any]) -> Dict[str, Any]:
        """规范化个人信息"""
        normalized = {}

        for key, value in info.items():
            if value is None:
                continue

            if key in ["name", "location"]:
                normalized[key] = str(value).strip() if value else None

            elif key == "phone":
                normalized[key] = StructureMapperTool._normalize_phone(value)

            elif key == "email":
                normalized[key] = StructureMapperTool._normalize_email(value)

            elif key == "birth_date":
                normalized[key] = StructureMapperTool._normalize_date(value)

            elif key == "gender":
                normalized[key] = StructureMapperTool._normalize_gender(value)

            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_education(edu: Dict[str, Any]) -> Dict[str, Any]:
        """规范化教育经历"""
        normalized = {}

        for key, value in edu.items():
            if value is None:
                normalized[key] = None
                continue

            if key in ["school", "major", "description"]:
                normalized[key] = str(value).strip() if value else ""

            elif key == "degree":
                normalized[key] = StructureMapperTool._normalize_degree(value)

            elif key in ["start_time", "end_time"]:
                normalized[key] = StructureMapperTool._normalize_date(value)

            elif key == "gpa":
                normalized[key] = StructureMapperTool._normalize_gpa(value)

            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_work_exp(work: Dict[str, Any]) -> Dict[str, Any]:
        """规范化工作经历"""
        normalized = {}

        for key, value in work.items():
            if value is None:
                normalized[key] = None
                continue

            if key in ["company", "position", "industry", "description"]:
                normalized[key] = str(value).strip() if value else ""

            elif key in ["start_time", "end_time"]:
                normalized[key] = StructureMapperTool._normalize_date(value)

            elif key == "company_scale":
                normalized[key] = StructureMapperTool._normalize_company_scale(value)

            elif key == "achievements":
                normalized[key] = StructureMapperTool._normalize_list_field(value)

            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_project(proj: Dict[str, Any]) -> Dict[str, Any]:
        """规范化项目经验"""
        normalized = {}
        original_role = proj.get("role", "")
        original_description = proj.get("description", "")
        original_achievements = proj.get("achievements", [])

        for key, value in proj.items():
            if value is None:
                normalized[key] = None
                continue

            if key == "name":
                normalized[key] = str(value).strip() if value else ""

            elif key == "role":
                # 标准化项目角色
                normalized[key] = StructureMapperTool._normalize_project_role(
                    original_role,
                    original_description
                )

            elif key == "description":
                # 构建完整的项目描述
                desc_value = str(value).strip() if value else ""
                role_text = str(original_role).strip() if original_role else ""
                achievements = original_achievements if original_achievements else []

                # 构建最终描述
                final_parts = []

                # 1. 判断role是否是职责描述
                is_role_description = (
                    any(punct in role_text for punct in [",", "，", ".", "。", "；", ";"])
                    or
                    (len(role_text) > 15 and any(verb in role_text for verb in ["负责", "构建", "搭建", "实现", "开发", "独立", "主导", "参与", "协助"]))
                )

                # 2. 添加role描述（如果是职责描述）
                if is_role_description:
                    final_parts.append(role_text)

                # 3. 添加主描述
                if desc_value:
                    final_parts.append(desc_value)

                # 4. 添加成果到描述中（保持完整性）
                if achievements and isinstance(achievements, list):
                    achievement_texts = []
                    for ach in achievements:
                        if isinstance(ach, str):
                            achievement_texts.append(ach.strip())
                        elif isinstance(ach, dict):
                            # 如果是字典，提取文本内容
                            achievement_texts.append(str(ach).strip())

                    if achievement_texts:
                        # 将成果作为段落添加到描述中
                        if final_parts:
                            # 最后添加成果部分
                            final_parts.append("项目成果：" + "；".join(achievement_texts))
                        else:
                            final_parts.extend(achievement_texts)

                # 合并所有部分
                if final_parts:
                    normalized[key] = " ".join(final_parts)
                else:
                    normalized[key] = ""

            elif key in ["start_time", "end_time"]:
                normalized[key] = StructureMapperTool._normalize_date(value)

            elif key == "team_size":
                normalized[key] = StructureMapperTool._normalize_team_size(value)

            elif key == "tech_stack":
                normalized[key] = StructureMapperTool._normalize_tech_stack(value)

            elif key in ["achievements", "complexity_indicators"]:
                normalized[key] = StructureMapperTool._normalize_list_field(value)

            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_skill(skill: Any) -> Dict[str, Any]:
        """规范化技能"""
        # 如果是字符串，转换为字典
        if isinstance(skill, str):
            return {"name": skill.strip(), "category": "other", "level": "了解"}

        if not isinstance(skill, dict):
            return {"name": "未知", "category": "other", "level": "了解"}

        normalized = {}

        for key, value in skill.items():
            if value is None:
                normalized[key] = None
                continue

            if key == "name":
                normalized[key] = str(value).strip()

            elif key == "level":
                normalized[key] = StructureMapperTool.SKILL_LEVEL_MAPPING.get(
                    str(value).strip().lower(),
                    "了解"
                )

            else:
                normalized[key] = value

        # 确保必需字段存在
        if "name" not in normalized or not normalized["name"]:
            return None
        if "level" not in normalized:
            normalized["level"] = "了解"

        return normalized

    # ==================== 辅助方法 ====================

    @staticmethod
    def _clean_string(value: Any) -> Any:
        """清理字符串（去除首尾空格）"""
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, list):
            return [StructureMapperTool._clean_string(v) for v in value]
        elif isinstance(value, dict):
            return {k: StructureMapperTool._clean_string(v) for k, v in value.items()}
        return value

    @staticmethod
    def _normalize_phone(phone: Any) -> Optional[str]:
        """规范化手机号（去除非数字字符）"""
        if not phone:
            return None
        cleaned = re.sub(r'[^\d]', '', str(phone))
        return cleaned if cleaned else None

    @staticmethod
    def _normalize_email(email: Any) -> Optional[str]:
        """规范化邮箱（转小写，去除空格）"""
        if not email:
            return None
        return str(email).strip().lower()

    @staticmethod
    def _normalize_date(date_val: Any) -> Optional[str]:
        """
        规范化日期为 YYYY-MM 格式

        支持的输入格式：
        - 2020-01
        - 2020年1月
        - 2020.01
        - 2020/01
        - 2020
        """
        if not date_val:
            return None

        date_str = str(date_val).strip()

        # 已经是标准格式
        if re.match(r'^\d{4}-\d{2}$', date_str):
            return date_str

        # 提取年月信息
        year_match = re.search(r'(\d{4})', date_str)
        month_match = re.search(r'(\d{1,2})[月月.\-/]', date_str)

        if not year_match:
            return None

        year = year_match.group(1)
        month = month_match.group(1).zfill(2) if month_match else "01"

        return f"{year}-{month}"

    @staticmethod
    def _normalize_degree(degree: Any) -> str:
        """规范化学位"""
        if not degree:
            return ""
        degree_str = str(degree).strip().lower()
        return StructureMapperTool.DEGREE_NORMALIZATION.get(degree_str, str(degree))

    @staticmethod
    def _normalize_gender(gender: Any) -> Optional[str]:
        """规范化性别"""
        if not gender:
            return None
        gender_str = str(gender).strip()
        if gender_str in ["男", "male", "m", "M"]:
            return "男"
        elif gender_str in ["女", "female", "f", "F"]:
            return "女"
        return gender_str

    @staticmethod
    def _normalize_gpa(gpa: Any) -> Optional[str]:
        """规范化GPA"""
        if not gpa:
            return None
        gpa_str = str(gpa).strip()
        # 验证GPA格式
        if re.match(r'^\d+\.?\d*$', gpa_str):
            return gpa_str
        return None

    @staticmethod
    def _normalize_company_scale(scale: Any) -> Optional[str]:
        """规范化公司规模"""
        if not scale:
            return None
        return str(scale).strip()

    @staticmethod
    def _normalize_team_size(size: Any) -> Optional[int]:
        """规范化团队规模"""
        if not size:
            return None
        try:
            return int(str(size).strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _normalize_project_role(role: Any, description: Any = None) -> str:
        """
        规范化项目角色

        判断规则：
        1. 如果role包含标点符号（逗号、句号等），说明是描述，需要推断
        2. 如果role长度>15且包含动词关键词，说明是描述，需要推断
        3. 否则尝试映射到标准角色

        Args:
            role: 原始role字段
            description: 原始description字段（可选）

        Returns:
            标准化的角色名称
        """
        if not role:
            return "开发者"

        role_text = str(role).strip()

        # 判断是否是职责描述（而非角色名称）
        is_description = (
            # 包含标点符号，说明是完整句子
            any(punct in role_text for punct in [",", "，", ".", "。", "；", ";"])
            or
            # 长度>=8且包含常见动词，说明是职责描述
            (len(role_text) >= 8 and any(verb in role_text for verb in ["负责", "构建", "搭建", "实现", "开发", "独立", "主导", "参与", "协助"]))
        )

        if is_description:
            # 从职责描述中推断角色
            return StructureMapperTool._infer_role_from_description(role_text)

        # 尝试映射到标准角色
        if role_text in StructureMapperTool.PROJECT_ROLE_MAPPING:
            return StructureMapperTool.PROJECT_ROLE_MAPPING[role_text]

        # 模糊匹配
        role_lower = role_text.lower()
        for standard, variants in [
            ("负责人", ["lead", "leader", "owner"]),
            ("主导", ["principal"]),
            ("核心开发者", ["core", "senior", "核心"]),
            ("开发者", ["developer", "dev", "开发"]),
            ("参与者", ["member", "assistant", "参与", "协助"])
        ]:
            if any(variant in role_lower for variant in variants):
                return standard

        return "开发者"  # 默认

    @staticmethod
    def _infer_role_from_description(text: str) -> str:
        """
        从职责描述中推断项目角色

        Args:
            text: 职责描述文本

        Returns:
            推断出的角色名称
        """
        text_lower = text.lower()

        # 按优先级检查关键词
        # 1. 负责人特征（最高优先级）
        for keyword in StructureMapperTool.PROJECT_ROLE_INFERENCE_KEYWORDS["负责人"]:
            if keyword.lower() in text_lower:
                return "负责人"

        # 2. 主导特征
        for keyword in StructureMapperTool.PROJECT_ROLE_INFERENCE_KEYWORDS["主导"]:
            if keyword.lower() in text_lower:
                return "主导"

        # 3. 参与者特征（低优先级）
        for keyword in StructureMapperTool.PROJECT_ROLE_INFERENCE_KEYWORDS["参与者"]:
            if keyword.lower() in text_lower:
                return "参与者"

        # 4. 核心开发者特征（默认）
        for keyword in StructureMapperTool.PROJECT_ROLE_INFERENCE_KEYWORDS["核心开发者"]:
            if keyword.lower() in text_lower:
                return "核心开发者"

        # 默认返回开发者
        return "开发者"

    @staticmethod
    def _normalize_tech_stack(stack: Any) -> List[str]:
        """规范化技术栈（确保返回字符串列表）"""
        if not stack:
            return []

        if isinstance(stack, str):
            # 支持多种分隔符：逗号、顿号、分号、斜杠
            items = re.split(r'[,，、;/;|]', stack)
            return [item.strip() for item in items if item.strip()]

        if isinstance(stack, list):
            return [str(item).strip() for item in stack if item]

        return []

    @staticmethod
    def _normalize_list_field(field: Any) -> List[Any]:
        """规范化列表字段"""
        if not field:
            return []
        if isinstance(field, list):
            return field
        if isinstance(field, str):
            return [field.strip()]
        return [field]

    @staticmethod
    def _validate_and_fix(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        数据验证和修复

        - 确保必需字段存在
        - 修复缺失的数组字段
        - 验证数据类型
        """
        if not isinstance(data, dict):
            return {}

        # 确保数组字段存在且为列表
        array_fields = ["education", "work_experience", "projects", "skills"]
        for field in array_fields:
            if field not in data:
                data[field] = []
            elif not isinstance(data[field], list):
                data[field] = []

        # 过滤掉技能列表中的None值
        if "skills" in data and isinstance(data["skills"], list):
            data["skills"] = [s for s in data["skills"] if s is not None]

        # 确保personal_info存在
        if "personal_info" not in data:
            data["personal_info"] = {}
        elif not isinstance(data["personal_info"], dict):
            data["personal_info"] = {}

        return data

    @staticmethod
    def get_mapping_stats(original: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取映射统计信息

        Args:
            original: 原始数据
            normalized: 标准化后的数据

        Returns:
            统计信息字典
        """
        return {
            "fields_mapped": len(normalized),
            "array_fields_count": sum(1 for v in normalized.values() if isinstance(v, list)),
            "nested_fields": sum(1 for v in normalized.values() if isinstance(v, dict)),
            "top_level_fields": list(normalized.keys())
        }
