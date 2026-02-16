from .structure_checker import check_structure, find_field
from .rules import validate_experience, validate_projects, validate_certifications, validate_links

class ResumeValidator:
    def __init__(self):
        pass

    def find_section(self, data, names):
        result = find_field(data, names)
        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result] if result else []
    
    def validate(self, input_json):
        struct = check_structure(input_json)
        info = struct["extracted_info"]
        data = struct["original_data"]
        exp = self.find_section(data, ["experience", "experiences", "work", "employment"])
        proj = self.find_section(data, ["projects", "project", "portfolio"])
        cert = self.find_section(data, ["certifications", "certification", "certs"])
        
        sections = {}
        
        exp_issues = validate_experience(exp)
        sections["experience"] = {
            "status": "PASS" if not exp_issues else ("NOT_FOUND" if "No experience" in str(exp_issues) else "FAIL"),
            "issues": exp_issues
        }
        proj_issues = validate_projects(proj)
        sections["projects"] = {
            "status": "PASS" if not proj_issues else "FAIL",
            "issues": proj_issues
        }
        cert_issues = validate_certifications(cert)
        sections["certifications"] = {
            "status": "PASS" if not cert_issues else ("NOT_FOUND" if "No certifications" in str(cert_issues) else "FAIL"),
            "issues": cert_issues
        }     
        link_issues = validate_links(data)
        sections["links"] = {
            "status": "PASS" if not link_issues else "FAIL",
            "issues": link_issues
        }       
        return {
            "candidate_id": info["candidate_id"],
            "name": info["name"],
            "email": info["email"],
            "validation_status": "PROCESSED",
            "sections": sections
        }