from .utils import validate_date, calculate_days, validate_url
from .structure_checker import find_field 

def get_field(item, possible_names, default=None):
    if isinstance(item, dict):
        for name in possible_names:
            if name in item:
                return item[name]
    return default

def extract_text(points):
    if isinstance(points, dict):
        parts = []
        for v in points.values():
            if isinstance(v, str):
                parts.append(v)
        return " ".join(parts)
    return ""

def validate_experience(exp_list):
    if not exp_list:
        return ["No experience section found"]
    
    issues = []
    for idx, exp in enumerate(exp_list, 1):
        title = get_field(exp, ["title", "job_title", "position", "role"])
        if not title:
            issues.append(f"Exp {idx}: Missing title")
        
        company = get_field(exp, ["company", "employer", "organization"])
        if not company:
            issues.append(f"Exp {idx}: Missing company")
        
        start = get_field(exp, ["start_date", "startDate", "from"])
        if not start:
            issues.append(f"Exp {idx}: Missing start date")
        elif not validate_date(str(start)):
            issues.append(f"Exp {idx}: Invalid start date")
        
        end = get_field(exp, ["end_date", "endDate", "to"])
        if end and str(end).lower() not in ["present", "current", "now", "null"]:
            if not validate_date(str(end)):
                issues.append(f"Exp {idx}: Invalid end date")
            elif start and validate_date(str(start)):
                days = calculate_days(str(start), str(end))
                if days < 1:
                    issues.append(f"Exp {idx}: End before start")
        
        desc = get_field(exp, ["description", "desc", "details"])
        if not desc or len(str(desc).strip()) < 10:
            issues.append(f"Exp {idx}: Missing/short description")
    
    return issues

def validate_projects(proj_list):
    if not proj_list:
        return ["No projects section found"]
    
    issues = []
    for idx, proj in enumerate(proj_list, 1):
        name = get_field(proj, ["name", "title", "project_name"])
        if not name:
            issues.append(f"Proj {idx}: Missing name")
        
        points = proj.get("points", {})
        desc = extract_text(points)
        if not desc and "description" not in proj:
            issues.append(f"Proj {idx}: Missing description")
        
        tech_found = False
        if isinstance(points, dict):
            for v in points.values():
                if isinstance(v, str) and ("Tech stack:" in v or "technologies" in v.lower()):
                    tech_found = True
                    break
        
        techs = get_field(proj, ["technologies", "tech_stack", "tech"])
        if not tech_found and not techs:
            issues.append(f"Proj {idx}: Missing technologies")
        
        github = get_field(proj, ["github", "github_url", "repo"])
        if github and not validate_url(str(github)):
            issues.append(f"Proj {idx}: Invalid GitHub URL")
    
    return issues

def validate_certifications(cert_list):
    if not cert_list:
        return ["No certifications section found"]
    
    issues = []
    for idx, cert in enumerate(cert_list, 1):
        name = get_field(cert, ["name", "cert_name", "title"])
        if not name:
            issues.append(f"Cert {idx}: Missing name")
        
        issuer = get_field(cert, ["issuer", "issued_by", "organization"])
        if not issuer:
            issues.append(f"Cert {idx}: Missing issuer")
        
        url = get_field(cert, ["verification_url", "url", "link"])
        if url and not validate_url(str(url)):
            issues.append(f"Cert {idx}: Invalid URL")
    
    return issues

def validate_links(data):
    issues = []
    
    link_fields = ["linkedin", "github", "leetcode", "portfolio", "codeforces", "codechef"]
    for field in link_fields:
        val = data.get(field)
        if val and isinstance(val, str) and val != "null" and val.strip():
            if not validate_url(val):
                issues.append(f"Invalid {field}: {val}")
    
    projects = data.get("projects", [])
    for idx, proj in enumerate(projects, 1):
        github = proj.get("github")
        if github and isinstance(github, str) and github.strip() and github != "null":
            if not validate_url(github):
                issues.append(f"Proj {idx}: Invalid GitHub: {github}")
    
    return issues