# tools/cleaning/data_deduplicator.py
"""数据去重工具 - 智能识别和合并重复数据"""
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
from datetime import datetime
import copy


class DataDeduplicator:
    """数据去重工具类"""

    @staticmethod
    def deduplicate_resume(resume_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        对简历数据进行智能去重

        Args:
            resume_data: 简历数据字典

        Returns:
            (去重后的数据, 详细的去重报告)
        """
        if not resume_data or not isinstance(resume_data, dict):
            return resume_data, {"error": "无效的简历数据"}

        # 初始化去重报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_items_processed": 0,
                "total_duplicates_removed": 0,
                "items_merged": 0,
                "categories_processed": []
            },
            "details": {
                "skills": {"removed": [], "merged": [], "kept": []},
                "projects": {"removed": [], "merged": [], "kept": []},
                "work_experience": {"removed": [], "merged": [], "kept": []},
                "certificates": {"removed": [], "kept": []}
            }
        }

        total_processed = 0
        total_removed = 0
        total_merged = 0

        # 1. 去重技能
        if "skills" in resume_data and isinstance(resume_data["skills"], list):
            original_count = len(resume_data["skills"])
            skills, skills_report = DataDeduplicator._deduplicate_skills(
                resume_data["skills"]
            )
            resume_data["skills"] = skills

            processed = original_count - len(skills)
            removed = len(skills_report["removed"])
            merged = len(skills_report["merged"])

            total_processed += processed
            total_removed += removed
            total_merged += merged

            report["details"]["skills"] = skills_report
            report["summary"]["categories_processed"].append("skills")

        # 2. 去重项目
        if "projects" in resume_data and isinstance(resume_data["projects"], list):
            original_count = len(resume_data["projects"])
            projects, projects_report = DataDeduplicator._deduplicate_projects(
                resume_data["projects"]
            )
            resume_data["projects"] = projects

            processed = original_count - len(projects)
            removed = len(projects_report["removed"])
            merged = len(projects_report["merged"])

            total_processed += processed
            total_removed += removed
            total_merged += merged

            report["details"]["projects"] = projects_report
            report["summary"]["categories_processed"].append("projects")

        # 3. 去重工作经历
        if "work_experience" in resume_data and isinstance(resume_data["work_experience"], list):
            original_count = len(resume_data["work_experience"])
            work_exp, work_report = DataDeduplicator._deduplicate_work_experience(
                resume_data["work_experience"]
            )
            resume_data["work_experience"] = work_exp

            processed = original_count - len(work_exp)
            removed = len(work_report["removed"])
            merged = len(work_report["merged"])

            total_processed += processed
            total_removed += removed
            total_merged += merged

            report["details"]["work_experience"] = work_report
            report["summary"]["categories_processed"].append("work_experience")

        # 4. 去重证书
        if "certificates" in resume_data and isinstance(resume_data["certificates"], list):
            original_count = len(resume_data["certificates"])
            certificates, certs_report = DataDeduplicator._deduplicate_certificates(
                resume_data["certificates"]
            )
            resume_data["certificates"] = certificates

            processed = original_count - len(certificates)
            removed = len(certs_report["removed"])

            total_processed += processed
            total_removed += removed

            report["details"]["certificates"] = certs_report
            report["summary"]["categories_processed"].append("certificates")

        # 更新汇总信息
        report["summary"]["total_items_processed"] = total_processed
        report["summary"]["total_duplicates_removed"] = total_removed
        report["summary"]["items_merged"] = total_merged

        return resume_data, report

    @staticmethod
    def _deduplicate_skills(skills: List[Dict]) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        智能去重技能

        策略：
        1. 完全相同：删除重复
        2. 名称相似但等级不同：保留等级更高的
        3. 名称相似度>90%：视为重复
        """
        report = {
            "removed": [],  # 被删除的项
            "merged": [],   # 被合并的项（保留更好的版本）
            "kept": []      # 被保留的项
        }

        if not skills:
            return skills, report

        unique_skills = []
        removed_skills = []

        for skill in skills:
            if not isinstance(skill, dict) or not skill.get("name"):
                continue

            skill_name = skill["name"].strip()
            if not skill_name:
                continue

            # 查找相似的技能
            duplicate_index = None
            max_similarity = 0
            action = None  # "remove" 或 "merge"

            for i, existing in enumerate(unique_skills):
                existing_name = existing.get("name", "").strip()
                if not existing_name:
                    continue

                # 计算名称相似度
                similarity = SequenceMatcher(
                    None,
                    skill_name.lower(),
                    existing_name.lower()
                ).ratio()

                if similarity > 0.9:  # 90%相似度阈值
                    if similarity > max_similarity:
                        max_similarity = similarity
                        duplicate_index = i

                        # 判断操作类型
                        if skill_name.lower() == existing_name.lower():
                            # 名称完全相同，检查其他字段是否有差异
                            if DataDeduplicator._skills_have_different_info(existing, skill):
                                # 有差异，需要合并
                                action = "merge"
                            else:
                                # 完全相同，删除
                                action = "remove"
                        else:
                            # 相似但不完全相同，尝试合并
                            action = "merge"

            if duplicate_index is not None:
                existing_skill = unique_skills[duplicate_index]

                if action == "remove":
                    # 完全重复，记录并跳过
                    report["removed"].append({
                        "item": skill,
                        "reason": f"与'{existing_skill['name']}'完全重复",
                        "similarity": max_similarity
                    })
                    removed_skills.append(skill)

                elif action == "merge":
                    # 相似但可能信息不同，智能合并
                    merged_skill = DataDeduplicator._merge_skills(existing_skill, skill)

                    # 记录合并信息
                    report["merged"].append({
                        "kept": merged_skill,
                        "removed": skill,
                        "original_existing": existing_skill,
                        "reason": f"与'{existing_skill['name']}'相似 ({max_similarity:.1%})，已合并信息",
                        "similarity": max_similarity,
                        "changes": DataDeduplicator._get_skill_changes(existing_skill, skill, merged_skill)
                    })

                    unique_skills[duplicate_index] = merged_skill
                    removed_skills.append(skill)
            else:
                # 没有重复，保留
                unique_skills.append(skill)
                report["kept"].append({
                    "item": skill,
                    "reason": "唯一项"
                })

        return unique_skills, report

    @staticmethod
    def _skills_have_different_info(skill1: Dict, skill2: Dict) -> bool:
        """检查两个技能是否有不同的信息"""
        # 比较关键字段
        for key in ["level", "category", "verified"]:
            val1 = skill1.get(key)
            val2 = skill2.get(key)

            # 如果一个有值另一个没有，或者值不同，则有差异
            if val1 != val2:
                # 注意：如果两个都是None或空，不算差异
                if not (not val1 and not val2):
                    return True

        return False

    @staticmethod
    def _merge_skills(skill1: Dict, skill2: Dict) -> Dict:
        """
        合并两个技能，保留更完整/更高级的信息

        优先级：
        1. 保留非空的字段
        2. level: expert(精通) > proficient(熟练) > familiar(熟悉) > beginner(了解)
        3. category: 如果不同，保留更具体的
        """
        merged = copy.deepcopy(skill1)

        # 等级优先级（支持中英文）
        level_priority = {
            # 中文
            "精通": 4, "熟练": 3, "熟悉": 2, "了解": 1,
            # 英文
            "expert": 4, "proficient": 3, "familiar": 2, "beginner": 1,
            # 映射英文到中文
            "master": 4, "advanced": 3, "intermediate": 2, "basic": 1
        }

        # 合并level（保留更高的）
        level1 = skill1.get("level", "了解")
        level2 = skill2.get("level", "了解")
        if level_priority.get(level2, 0) > level_priority.get(level1, 0):
            merged["level"] = level2

        # 合并category（如果skill2的更具体）
        category1 = skill1.get("category", "other")
        category2 = skill2.get("category", "other")
        if category2 != "other" and category1 == "other":
            merged["category"] = category2

        # 合并其他字段（保留非空的）
        for key in ["verified"]:
            if key in skill2 and skill2[key] is not None:
                if key not in merged or merged[key] is None:
                    merged[key] = skill2[key]

        return merged

    @staticmethod
    def _get_skill_changes(original1: Dict, original2: Dict, merged: Dict) -> List[str]:
        """获取技能合并的变化"""
        changes = []

        if original1.get("level") != merged.get("level"):
            changes.append(f"等级: {original1.get('level')} → {merged.get('level')}")

        if original1.get("category") != merged.get("category"):
            changes.append(f"类别: {original1.get('category')} → {merged.get('category')}")

        return changes

    @staticmethod
    def _deduplicate_projects(projects: List[Dict]) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        智能去重项目

        策略：
        1. 项目名完全相同 + 时间段重叠 → 重复
        2. 项目名相似度>95% → 可能重复（警告但保留）
        """
        report = {
            "removed": [],
            "merged": [],
            "kept": []
        }

        if not projects:
            return projects, report

        unique_projects = []

        for project in projects:
            if not isinstance(project, dict) or not project.get("name"):
                continue

            project_name = project["name"].strip()
            if not project_name:
                continue

            # 查找重复项目
            duplicate_index = None
            max_similarity = 0
            action = "keep"

            for i, existing in enumerate(unique_projects):
                existing_name = existing.get("name", "").strip()
                if not existing_name:
                    continue

                # 计算项目名相似度
                similarity = SequenceMatcher(
                    None,
                    project_name.lower(),
                    existing_name.lower()
                ).ratio()

                if similarity == 1.0:
                    # 项目名完全相同，检查时间段
                    action = "remove"
                    duplicate_index = i
                    max_similarity = similarity
                    break

                elif similarity > 0.95:
                    # 高度相似但不同，标记为可能重复但仍保留
                    report["kept"].append({
                        "item": project,
                        "reason": f"项目名与'{existing_name}'高度相似 ({similarity:.1%})，但已保留",
                        "warning": "可能是重复项目，请人工确认"
                    })
                    break

            if duplicate_index is not None and action == "remove":
                existing_project = unique_projects[duplicate_index]
                report["removed"].append({
                    "item": project,
                    "reason": f"与项目'{existing_project['name']}'重复",
                    "existing_project": existing_project
                })
            elif duplicate_index is None:
                # 没有重复
                unique_projects.append(project)
                if not any(
                    k.get("item") is project
                    for k in report["kept"]
                ):
                    report["kept"].append({
                        "item": project,
                        "reason": "唯一项目"
                    })

        return unique_projects, report

    @staticmethod
    def _deduplicate_work_experience(work_list: List[Dict]) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        智能去重工作经历

        策略：
        1. 公司+职位+时间完全相同 → 重复
        2. 同一公司同一职位时间段重叠 → 合并
        """
        report = {
            "removed": [],
            "merged": [],
            "kept": []
        }

        if not work_list:
            return work_list, report

        unique_work = []

        for work in work_list:
            if not isinstance(work, dict):
                continue

            company = work.get("company", "").strip() if work.get("company") else ""
            position = work.get("position", "").strip() if work.get("position") else ""

            if not company:
                # 没有公司信息，直接保留
                unique_work.append(work)
                report["kept"].append({
                    "item": work,
                    "reason": "无公司信息，无法判断重复"
                })
                continue

            # 查找重复
            duplicate_index = None

            for i, existing in enumerate(unique_work):
                existing_company = existing.get("company", "").strip()
                existing_position = existing.get("position", "").strip()

                if company == existing_company:
                    if position and existing_position:
                        # 有职位信息，比较职位
                        if position == existing_position:
                            duplicate_index = i
                            break
                    else:
                        # 没有职位信息，仅按公司判断
                        duplicate_index = i
                        break

            if duplicate_index is not None:
                existing_work = unique_work[duplicate_index]
                report["removed"].append({
                    "item": work,
                    "reason": f"与工作经历重复",
                    "existing": {
                        "company": existing_work.get("company"),
                        "position": existing_work.get("position")
                    }
                })
            else:
                unique_work.append(work)
                report["kept"].append({
                    "item": work,
                    "reason": "唯一工作经历"
                })

        return unique_work, report

    @staticmethod
    def _deduplicate_certificates(certificates: List[Dict]) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        去重证书

        策略：
        证书名完全相同 → 重复
        """
        report = {
            "removed": [],
            "kept": []
        }

        if not certificates:
            return certificates, report

        unique_certs = []
        seen_cert_names = {}  # name -> certificate

        for cert in certificates:
            cert_name = ""

            if isinstance(cert, dict):
                cert_name = cert.get("name", "").strip()
            elif isinstance(cert, str):
                cert_name = cert.strip()

            if not cert_name:
                continue

            cert_key = cert_name.lower()

            if cert_key in seen_cert_names:
                # 发现重复
                existing = seen_cert_names[cert_key]
                report["removed"].append({
                    "item": cert,
                    "reason": f"与证书'{cert_name}'重复",
                    "existing": existing
                })
            else:
                unique_certs.append(cert)
                seen_cert_names[cert_key] = cert
                report["kept"].append({
                    "item": cert,
                    "reason": "唯一证书"
                })

        return unique_certs, report

    @staticmethod
    def format_report_for_display(report: Dict[str, Any]) -> str:
        """
        格式化去重报告用于显示

        Returns:
            格式化的字符串报告
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📊 数据去重报告")
        lines.append("=" * 60)
        lines.append("")

        # 汇总信息
        summary = report.get("summary", {})
        lines.append("📈 汇总统计:")
        lines.append(f"  • 处理的项目数: {summary.get('categories_processed', [])}")
        lines.append(f"  • 总处理项数: {summary.get('total_items_processed', 0)}")
        lines.append(f"  • 删除重复项: {summary.get('total_duplicates_removed', 0)}")
        lines.append(f"  • 合并项数: {summary.get('items_merged', 0)}")
        lines.append("")

        # 详细信息
        details = report.get("details", {})

        for category in ["skills", "projects", "work_experience", "certificates"]:
            if category not in details:
                continue

            category_detail = details[category]
            category_name = {
                "skills": "🔧 技能",
                "projects": "📁 项目",
                "work_experience": "💼 工作经历",
                "certificates": "📜 证书"
            }.get(category, category)

            removed = category_detail.get("removed", [])
            merged = category_detail.get("merged", [])
            kept = category_detail.get("kept", [])

            if not removed and not merged:
                continue

            lines.append(f"{category_name}")
            lines.append("-" * 40)

            if removed:
                lines.append(f"  ❌ 删除 {len(removed)} 个重复项:")
                for i, item in enumerate(removed[:5], 1):  # 最多显示5个
                    reason = item.get("reason", "未知原因")
                    if isinstance(item.get("item"), dict):
                        name = item["item"].get("name", "未知")
                    else:
                        name = str(item.get("item", "未知"))
                    lines.append(f"    {i}. {name}")
                    lines.append(f"       原因: {reason}")

                if len(removed) > 5:
                    lines.append(f"    ... 还有 {len(removed) - 5} 项")
                lines.append("")

            if merged:
                lines.append(f"  🔀 合并 {len(merged)} 项:")
                for i, item in enumerate(merged[:3], 1):  # 最多显示3个
                    kept_item = item.get("kept", {})
                    removed_item = item.get("removed", {})
                    reason = item.get("reason", "未知原因")

                    kept_name = kept_item.get("name", "未知") if isinstance(kept_item, dict) else "未知"
                    lines.append(f"    {i}. {kept_name}")
                    lines.append(f"       {reason}")

                    changes = item.get("changes", [])
                    if changes:
                        lines.append(f"       变化: {', '.join(changes)}")

                if len(merged) > 3:
                    lines.append(f"    ... 还有 {len(merged) - 3} 项")
                lines.append("")

            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
