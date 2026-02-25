from .utils import (
    validate_email, validate_phone, is_null_or_empty,
    extract_phone_from_object, extract_email_from_object
)

def normalize_key(key):
    return (
        key.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

def key_matches(key, patterns):
    normalized_key = normalize_key(key)

    for pattern in patterns:
        pattern_norm = normalize_key(pattern)
        if normalized_key == pattern_norm:
            return True
        if normalized_key.startswith(pattern_norm + "_"):
            return True
        if normalized_key.endswith("_" + pattern_norm):
            return True
    return False

def find_field(data, possible_names):
    if isinstance(data, dict):
        for key, value in data.items():
            if key_matches(key, possible_names):
                return value
        for value in data.values():
            result = find_field(value, possible_names)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_field(item, possible_names)
            if result is not None:
                return result
    return None

def find_all_links(data):
    links = []
    def search(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    if any(domain in value.lower() for domain in [
                        "http", "www.", ".com", ".io", ".dev",
                        "github", "linkedin"
                    ]):
                        links.append((key, value))
                else:
                    search(value)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str):
                    if any(domain in item.lower() for domain in [
                        "http", "www.", ".com", ".io", ".dev",
                        "github", "linkedin"
                    ]):
                        links.append(("list_item", item))
                else:
                    search(item)
    search(data)
    return links

def detect_all_sections(data):
    section_patterns = {
         "experience": [
        "experience", "experiences",
        "work", "work_history", "workhistory",
        "employment", "employment_history",
        "jobs", "career", "career_history",
        "professional_experience", "internship",
        "internships", "work_experience",
        "workexperience", "job_history"
    ],
    "education": [
        "education", "academics", "academic",
        "academic_record", "academic_records",
        "academic_details", "qualification",
        "qualifications", "degrees",
        "degree", "schooling",
        "education_history", "academic_background"
    ],
    "projects": [
        "projects", "project",
        "project_experience", "projectexperience",
        "portfolio", "personal_projects",
        "academic_projects", "works",
        "case_studies"
    ],
    "certifications": [
        "certifications", "certification",
        "certificates", "certificate",
        "certs", "credentials",
        "licenses", "license",
        "professional_certifications"
    ],
    "skills": [
        "skills", "skillset", "technical_skills",
        "technologies", "tools", "competencies",
        "expertise", "core_competencies",
        "tech_stack"
    ],
    "languages": [
        "languages", "language",
        "spoken_languages"
    ],
    "achievements": [
        "achievements", "awards",
        "honors", "accomplishments",
        "recognition", "milestones"
    ],
    "publications": [
        "publications", "papers",
        "research", "research_work",
        "journals", "articles"
    ],
    "hobbies": [
        "hobbies", "interests",
        "extra_curricular",
        "extracurricular"
    ],
    "volunteering": [
        "volunteering", "volunteer",
        "community", "social_work",
        "ngo_work"
    ],
    "social_links": [
        "social_links", "social",
        "links", "profiles",
        "urls", "online_presence",
        "online_profiles",
        "contact_links"
    ],
    "references": [
        "references", "referees"
    ],
    "summary": [
        "summary", "objective",
        "about", "bio",
        "profile_summary",
        "professional_summary",
        "career_objective"
    ]
    }
    detected = {}
    for section, patterns in section_patterns.items():
        value = find_field(data, patterns)
        if value is not None:
            if isinstance(value, (dict, list)) and len(value) == 0:
                continue
            detected[section] = value
    return detected

def extract_basic_info(data):
    info = {
        "candidate_id": "unknown",
        "name": "unknown",
        "email": "unknown",
        "phone": "unknown",
        "email_valid": False,
        "phone_valid": False
    }
    id_names = ["candidate_id", "id", "userId", "user_id", "candidateId", "applicant_id"]
    found_id = find_field(data, id_names)
    if found_id is not None and not is_null_or_empty(found_id):
        info["candidate_id"] = str(found_id)
    name_names = ["name", "full_name", "fullName", "candidate_name", "applicant_name"]
    found_name = find_field(data, name_names)
    if found_name and not is_null_or_empty(found_name):
        info["name"] = str(found_name)
    contact_obj = find_field(data, ["contact", "contacts", "basics", "personal_info", "personal"])
    if contact_obj and isinstance(contact_obj, dict):
        extracted_email = extract_email_from_object(contact_obj)
        if extracted_email != "unknown":
            info["email"] = extracted_email
            info["email_valid"] = validate_email(extracted_email)
        extracted_phone = extract_phone_from_object(contact_obj)
        if extracted_phone != "unknown":
            info["phone"] = extracted_phone
            info["phone_valid"] = validate_phone(extracted_phone)
        if info["name"] == "unknown":
            for n in name_names:
                if n in contact_obj and not is_null_or_empty(contact_obj[n]):
                    info["name"] = str(contact_obj[n])
                    break
    if info["email"] == "unknown":
        email_names = ["email", "email_id", "emailId", "mail", "emails", "e-mail"]
        found_email = find_field(data, email_names)
        if found_email:
            if isinstance(found_email, list) and found_email:
                for e in found_email:
                    if isinstance(e, str) and validate_email(e):
                        info["email"] = e
                        info["email_valid"] = True
                        break
                if info["email"] == "unknown" and found_email:
                    info["email"] = str(found_email[0])
                    info["email_valid"] = validate_email(str(found_email[0]))
            elif isinstance(found_email, str):
                info["email"] = found_email
                info["email_valid"] = validate_email(found_email)
    if info["phone"] == "unknown":
        phone_names = ["phone", "mobile", "phone_number", "telephone", "tel", "contact_number"]
        found_phone = find_field(data, phone_names)

        if found_phone:
            if isinstance(found_phone, list) and found_phone:
                for p in found_phone:
                    if isinstance(p, (str, int)) and validate_phone(str(p)):
                        info["phone"] = str(p)
                        info["phone_valid"] = True
                        break
            elif isinstance(found_phone, (str, int, float)):
                info["phone"] = str(found_phone)
                info["phone_valid"] = validate_phone(str(found_phone))

    if info["name"] == "unknown":
        first = find_field(data, ["first_name", "firstname"])
        last = find_field(data, ["last_name", "lastname"])
        if first and last and not is_null_or_empty(first) and not is_null_or_empty(last):
            info["name"] = f"{first} {last}"
    return info
