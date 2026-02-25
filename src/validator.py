from .detector import detect_all_sections, extract_basic_info
from .rules import (
    validate_experience,
    validate_education,
    validate_projects,
    validate_certifications,
    validate_links,
    validate_basic_info
)
from .utils import is_null_or_empty
class ResumeValidator:
    def __init__(self):
        pass
    def validate(self, input_json):
        if not isinstance(input_json, dict):
            return {
                "candidate_id": "unknown",
                "name": "unknown",
                "email": "unknown",
                "phone": "unknown",
                "validation_status": "ERROR",
                "error": "Input must be a JSON object",
                "validated_sections": {},
                "detected_sections": []
            }
        try:
            all_sections = detect_all_sections(input_json)
            basic_info = extract_basic_info(input_json)
        except Exception as e:
            return {
                "candidate_id": "unknown",
                "name": "unknown",
                "email": "unknown",
                "phone": "unknown",
                "validation_status": "ERROR",
                "error": f"Detection error: {str(e)}",
                "validated_sections": {},
                "detected_sections": []
            }
        validated = {}
        detected_list = []
        validation_map = {
            "experience": validate_experience,
            "education": validate_education,
            "projects": validate_projects,
            "certifications": validate_certifications
        }
        for section, validator_fn in validation_map.items():
            if section in all_sections:
                section_data = all_sections.get(section)
                if is_null_or_empty(section_data):
                    validated[section] = {
                        "status": "FAIL",
                        "entries": [],
                        "section_issues": [f"{section.capitalize()} section is empty"]
                    }
                else:
                    try:
                        result = validator_fn(section_data)
                        validated[section] = result
                    except Exception as e:
                        validated[section] = {
                            "status": "ERROR",
                            "entries": [],
                            "section_issues": [f"Validation error: {str(e)}"]
                        }

            else:
                validated[section] = {
                    "status": "NOT_FOUND",
                    "entries": []
                }
        try:
            link_issues = validate_links(input_json)
        except Exception as e:
            link_issues = [f"Link validation error: {str(e)}"]

        validated["links"] = {
            "status": "PASS" if not link_issues else "FAIL",
            "issues": link_issues
        }
        try:
            basic_issues = validate_basic_info(basic_info)
        except Exception as e:
            basic_issues = [f"Basic info validation error: {str(e)}"]

        validated["basic_info"] = {
            "status": "PASS" if not basic_issues else "FAIL",
            "issues": basic_issues
        }
        for section in all_sections:
            if section not in validation_map:
                detected_list.append(section)
        fail_count = 0
        total_core = len(validation_map)
        for sec in validation_map:
            if validated[sec]["status"] == "FAIL":
                fail_count += 1
        if fail_count == 0:
            overall_status = "STRUCTURED"
        elif fail_count < total_core:
            overall_status = "PARTIALLY_STRUCTURED"
        else:
            overall_status = "NOT_STRUCTURED"
        return {
            "candidate_id": basic_info.get("candidate_id", "unknown"),
            "name": basic_info.get("name", "unknown"),
            "email": basic_info.get("email", "unknown"),
            "phone": basic_info.get("phone", "unknown"),
            "validation_status": overall_status,
            "validated_sections": validated,
            "detected_sections": detected_list
        }