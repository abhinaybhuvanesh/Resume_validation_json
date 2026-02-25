from .utils import (
    validate_date, calculate_days, validate_url, validate_email,
    validate_phone, validate_percentage, validate_cgpa, is_null_or_empty
)
from .detector import find_field, find_all_links

def get_field(item, possible_names):
    if isinstance(item, dict):
        for key, value in item.items():
            for name in possible_names:
                if key.lower() == name.lower():
                    return value
        for value in item.values():
            result = get_field(value, possible_names)
            if result is not None:
                return result
    elif isinstance(item, list):
        for element in item:
            result = get_field(element, possible_names)
            if result is not None:
                return result
    return None

def extract_text(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        parts = []
        for value in obj.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(str(x) for x in value if x)
        return " ".join(parts)
    if isinstance(obj, list):
        return " ".join(str(x) for x in obj if x)
    return ""

def validate_experience(exp_list):
    if not exp_list:
        return {"status": "NOT_FOUND", "entries": []}
    if isinstance(exp_list, dict):
        exp_list = [v for v in exp_list.values() if isinstance(v, dict)]
    if not isinstance(exp_list, list):
        return {
            "status": "FAIL",
            "entries": [{
                "entry_number": 1,
                "status": "FAIL",
                "issues": ["Invalid format - expected list"]
            }]
        }
    entries = []
    all_passed = True
    for idx, exp in enumerate(exp_list, 1):
        entry_issues = []
        if is_null_or_empty(exp) or not isinstance(exp, dict):
            entry_issues.append("Invalid or empty experience entry")
            all_passed = False
        else:
            title = get_field(exp, [
                "title", "position", "role",
                "job_title", "designation",
                "profile", "jobRole"
            ])
            company = get_field(exp, [
                "company", "employer",
                "organization", "firm",
                "company_name", "org"
            ])
            start = get_field(exp, [
                "startDate", "start_date",
                "from", "start",
                "joining_date"
            ])
            end = get_field(exp, [
                "endDate", "end_date",
                "to", "end",
                "leaving_date"
            ])
            start_str = str(start) if start else None
            end_str = str(end) if end else None
            if start_str and not validate_date(start_str):
                entry_issues.append(f"Invalid start date format: {start_str}")
                all_passed = False
            if end_str and end_str.lower() not in [
                "present", "current", "ongoing", "now"
            ]:
                if not validate_date(end_str):
                    entry_issues.append(f"Invalid end date format: {end_str}")
                    all_passed = False
                elif start_str and validate_date(start_str):
                    if calculate_days(start_str, end_str) < 1:
                        entry_issues.append("End date before start date")
                        all_passed = False
            desc = get_field(exp, [
                "summary", "description",
                "details", "about"
            ])
            if not desc:
                highlights = get_field(exp, [
                    "highlights", "responsibilities",
                    "duties", "points", "tasks"
                ])
                if highlights:
                    desc = extract_text(highlights)
            if not title and not company and not desc:
                entry_issues.append("Insufficient experience details")
                all_passed = False
            elif desc and isinstance(desc, str) and len(desc.strip()) < 5:
                entry_issues.append("Description too short")
                all_passed = False
        entries.append({
            "entry_number": idx,
            "status": "PASS" if not entry_issues else "FAIL",
            "issues": entry_issues
        })
    return {
        "status": "PASS" if all_passed else "FAIL",
        "entries": entries
    }

def validate_education(edu_data):
    if not edu_data:
        return {"status": "NOT_FOUND", "entries": []}
    if isinstance(edu_data, dict):
        edu_list = []
        for value in edu_data.values():
            if isinstance(value, dict):
                edu_list.append(value)
            elif isinstance(value, list):
                edu_list.extend([v for v in value if isinstance(v, dict)])
        edu_data = edu_list
    if not isinstance(edu_data, list):
        return {
            "status": "FAIL",
            "entries": [{
                "entry_number": 1,
                "status": "FAIL",
                "issues": ["Invalid format - expected list"]
            }]
        }
    if not edu_data:
        return {"status": "NOT_FOUND", "entries": []}
    entries = []
    all_passed = True
    for idx, edu in enumerate(edu_data, 1):
        entry_issues = []
        if is_null_or_empty(edu) or not isinstance(edu, dict):
            entry_issues.append("Invalid or empty education entry")
            all_passed = False
        else:
            degree = get_field(edu, [
                "degree", "qualification",
                "degree_name", "course",
                "program", "field_of_study"
            ])
            institution = get_field(edu, [
                "institution", "school",
                "college", "university",
                "institution_name", "institute",
                "academy"
            ])
            grade = get_field(edu, [
                "grade", "gpa", "cgpa",
                "percentage", "score",
                "marks", "result"
            ])
            if grade and not is_null_or_empty(grade):
                grade_str = str(grade).strip().lower()
                try:
                    if "%" in grade_str:
                        if not validate_percentage(grade_str):
                            entry_issues.append(f"Invalid percentage: {grade}")
                            all_passed = False
                    elif "cgpa" in grade_str or "gpa" in grade_str or "/" in grade_str:
                        if not validate_cgpa(grade_str):
                            entry_issues.append(f"Invalid CGPA: {grade}")
                            all_passed = False
                    else:
                        num = float(grade_str)
                        if num > 10:
                            if not (0 <= num <= 100):
                                entry_issues.append(f"Invalid grade value: {grade}")
                                all_passed = False
                        else:
                            if not (0 <= num <= 10):
                                entry_issues.append(f"Invalid grade value: {grade}")
                                all_passed = False

                except (ValueError, TypeError):
                    pass
            start = get_field(edu, [
                "startDate", "start_date",
                "from", "start",
                "admission_date"
            ])
            end = get_field(edu, [
                "endDate", "end_date",
                "to", "end",
                "graduation_date"
            ])
            duration = get_field(edu, [
                "duration", "academic_duration",
                "period"
            ])
            start_str = str(start) if start else None
            end_str = str(end) if end else None
            if start_str and not validate_date(start_str):
                entry_issues.append(f"Invalid start date format: {start}")
                all_passed = False

            if end_str and end_str.lower() not in [
                "present", "current", "ongoing", "now"
            ]:
                if not validate_date(end_str):
                    entry_issues.append(f"Invalid end date format: {end}")
                    all_passed = False
                elif start_str and validate_date(start_str):
                    if calculate_days(start_str, end_str) < 1:
                        entry_issues.append("End date before start date")
                        all_passed = False
            if not start and not end and duration:
                pass
            if not degree and not institution:
                entry_issues.append("Insufficient education details")
                all_passed = False
        entries.append({
            "entry_number": idx,
            "status": "PASS" if not entry_issues else "FAIL",
            "issues": entry_issues
        })
    return {
        "status": "PASS" if all_passed else "FAIL",
        "entries": entries
    }

def validate_projects(proj_list):
    if not proj_list:
        return {"status": "NOT_FOUND", "entries": []}
    if isinstance(proj_list, dict):
        proj_list = [v for v in proj_list.values() if isinstance(v, dict)]
    if not isinstance(proj_list, list):
        return {
            "status": "FAIL",
            "entries": [{
                "entry_number": 1,
                "status": "FAIL",
                "issues": ["Invalid format - expected list"]
            }]
        }
    entries = []
    all_passed = True
    for idx, proj in enumerate(proj_list, 1):
        entry_issues = []
        if is_null_or_empty(proj):
            entry_issues.append("Entry is empty or null")
            all_passed = False
        elif not isinstance(proj, dict):
            entry_issues.append("Invalid format - expected object")
            all_passed = False
        else:
            name = get_field(proj, [
                "name", "title", "project_name",
                "project_title", "project", "projectName"
            ])
            if is_null_or_empty(name):
                entry_issues.append("Missing or null name")
                all_passed = False
            points = get_field(proj, ["points", "highlights", "bullets"])
            desc = ""
            if isinstance(points, dict):
                desc = " ".join(
                    str(v) for v in points.values()
                    if isinstance(v, str)
                )
            elif isinstance(points, list):
                desc = " ".join(
                    str(v) for v in points
                    if isinstance(v, str)
                )
            if not desc:
                desc = get_field(proj, [
                    "description", "summary", "details",
                    "about", "project_summary"
                ])
                if isinstance(desc, list):
                    desc = " ".join(str(x) for x in desc if x)
            if is_null_or_empty(desc):
                entry_issues.append("Missing description")
                all_passed = False
            elif isinstance(desc, str) and len(desc.strip()) < 10:
                entry_issues.append("Description too short (min 10 chars)")
                all_passed = False
            tech = get_field(proj, [
                "technologies", "tech", "tech_stack",
                "tools", "stack", "built_with",
                "techstack", "techStack"
            ])
            combined_text = ""
            if isinstance(points, dict):
                combined_text += " ".join(
                    str(v) for v in points.values()
                    if isinstance(v, str)
                )
            elif isinstance(points, list):
                combined_text += " ".join(
                    str(v) for v in points
                    if isinstance(v, str)
                )
            if isinstance(desc, str):
                combined_text += " " + desc
            tech_keywords = [
                "python", "java", "c++", "c#", "javascript",
                "react", "node", "mongodb", "mysql",
                "django", "flask", "spring", "html",
                "css", "machine learning", "ai",
                "deep learning", "nlp"
            ]
            has_keyword = any(
                keyword in combined_text.lower()
                for keyword in tech_keywords
            )
            link = get_field(proj, [
                "link", "github", "url",
                "github_link", "repo",
                "repository", "repo_link",
                "github_url"
            ])
            if isinstance(link, dict):
                nested_link = get_field(link, [
                    "github_url", "url", "link"
                ])
                link = nested_link
            link_valid = True
            if link and not is_null_or_empty(link):
                if not isinstance(link, str):
                    entry_issues.append(f"Invalid link format: {link}")
                    link_valid = False
                    all_passed = False
                elif not validate_url(str(link)):
                    entry_issues.append(f"Invalid URL format: {link}")
                    link_valid = False
                    all_passed = False
            else:
                link_valid = False
            if not tech and not has_keyword and not link_valid:
                entry_issues.append("Missing technologies")
                all_passed = False
        entries.append({
            "entry_number": idx,
            "status": "PASS" if not entry_issues else "FAIL",
            "issues": entry_issues
        })
    return {
        "status": "PASS" if all_passed else "FAIL",
        "entries": entries
    }

def validate_certifications(cert_list):
    if not cert_list:
        return {"status": "NOT_FOUND", "entries": []}
    if isinstance(cert_list, dict):
        temp = []
        for value in cert_list.values():
            if isinstance(value, dict):
                temp.append(value)
            elif isinstance(value, list):
                temp.extend(value)
            elif isinstance(value, str):
                temp.append({"name": value})
        cert_list = temp
    if isinstance(cert_list, str):
        cert_list = [{"name": cert_list}]
    if not isinstance(cert_list, list):
        return {
            "status": "FAIL",
            "entries": [{
                "entry_number": 1,
                "status": "FAIL",
                "issues": ["Invalid format - expected list"]
            }]
        }
    entries = []
    all_passed = True
    for idx, cert in enumerate(cert_list, 1):
        entry_issues = []
        if isinstance(cert, str):
            cert = {"name": cert}
        if is_null_or_empty(cert) or not isinstance(cert, dict):
            entry_issues.append("Invalid or empty certification entry")
            all_passed = False
        else:
            name = get_field(cert, [
                "name", "certificate",
                "title", "certificate_name",
                "cert_name", "credential"
            ])
            issuer = get_field(cert, [
                "issuer", "organization",
                "issued_by", "provider",
                "authority", "platform"
            ])
            url = get_field(cert, [
                "verification_url",
                "credential_url",
                "certificate_url",
                "url", "link"
            ])
            if not name and not issuer:
                entry_issues.append("Insufficient certification details")
                all_passed = False
            if url and not is_null_or_empty(url):
                if not isinstance(url, str):
                    entry_issues.append(f"Invalid URL format: {url}")
                    all_passed = False
                elif not validate_url(str(url)):
                    entry_issues.append(f"Invalid verification URL: {url}")
                    all_passed = False
        entries.append({
            "entry_number": idx,
            "status": "PASS" if not entry_issues else "FAIL",
            "issues": entry_issues
        })
    return {
        "status": "PASS" if all_passed else "FAIL",
        "entries": entries
    }

def validate_links(data):
    issues = []
    seen_urls = set()
    def normalize_url(url):
        if not isinstance(url, str):
            return None
        url = url.strip()
        if not url:
            return None
        if not url.startswith(("http://", "https://")):
            if "." in url:
                url = "https://" + url
        return url
    all_links = find_all_links(data)
    for field, url in all_links:
        url = normalize_url(url)
        if not url:
            continue
        if url not in seen_urls:
            seen_urls.add(url)
            if not validate_url(url):
                issues.append(f"Invalid URL in '{field}': {url}")
    specific_fields = [
        "linkedin", "github", "portfolio",
        "website", "youtube", "twitter",
        "leetcode", "codeforces",
        "codechef", "hackerrank",
        "stackoverflow", "medium",
        "blog"
    ]
    for field in specific_fields:
        value = find_field(data, [
            field,
            field + "_profile",
            field + "_url",
            field + "_link",
            field + "Url",
            field + "Link"
        ])
        if isinstance(value, list):
            values = value
        else:
            values = [value]
        for val in values:
            url = normalize_url(val)
            if not url:
                continue
            if url not in seen_urls:
                seen_urls.add(url)

                if not validate_url(url):
                    issues.append(f"Invalid {field} URL: {url}")
    return issues

def validate_basic_info(info):
    issues = []
    email = info.get("email")
    if email and email != "unknown":
        if isinstance(email, list):
            valid_found = False
            for e in email:
                if isinstance(e, str) and validate_email(e):
                    valid_found = True
                    break
            if not valid_found:
                issues.append(f"Invalid email format: {email}")
        elif isinstance(email, str):
            if not validate_email(email):
                issues.append(f"Invalid email format: {email}")

        else:
            issues.append(f"Invalid email format: {email}")
    phone = info.get("phone")
    if phone and phone != "unknown":
        if isinstance(phone, list):
            valid_found = False
            for p in phone:
                if isinstance(p, (str, int)) and validate_phone(str(p)):
                    valid_found = True
                    break
            if not valid_found:
                issues.append(f"Invalid phone number format: {phone}")
        elif isinstance(phone, (str, int)):
            if not validate_phone(str(phone)):
                issues.append(f"Invalid phone number format: {phone}")

        else:
            issues.append(f"Invalid phone number format: {phone}")
    name = info.get("name")
    if name and name != "unknown":
        if not isinstance(name, str) or len(name.strip()) < 2:
            issues.append("Invalid name format")
    return issues
