from .utils import validate_url

def validate_all_links(data):
    issues = []
    
    direct = ["linkedin", "github", "leetcode", "portfolio"]
    for f in direct:
        if f in data and data[f] and isinstance(data[f], str) and data[f] != "null":
            if not validate_url(data[f]):
                issues.append(f"Invalid {f}: {data[f]}")
    
    projects = data.get("projects", [])
    for idx, p in enumerate(projects, 1):
        if "github" in p and p["github"] and p["github"] != "null":
            if not validate_url(p["github"]):
                issues.append(f"Proj {idx}: Invalid GitHub: {p['github']}")
    
    return issues