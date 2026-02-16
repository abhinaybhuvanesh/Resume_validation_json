def find_field(data, possible_names):
    if isinstance(data, dict):
        for name in possible_names:
            if name in data:
                return data[name]
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

def extract_info(data):
    info = {"candidate_id": "unknown", "name": "unknown", "email": "unknown"}
    
    id_names = ["candidate_id", "candidateId", "id", "user_id", "userId"]
    name_names = ["name", "full_name", "fullName", "candidate_name", "username"]
    email_names = ["email", "email_id", "emailId", "mail", "emails"]
    
    found_id = find_field(data, id_names)
    if found_id:
        info["candidate_id"] = str(found_id)
    
    found_name = find_field(data, name_names)
    if found_name:
        info["name"] = str(found_name)
    
    found_email = find_field(data, email_names)
    if isinstance(found_email, list) and len(found_email) > 0:
        info["email"] = str(found_email[0])
    elif isinstance(found_email, str):
        info["email"] = found_email
    
    return info

def check_structure(data):
    return {"valid": True, "extracted_info": extract_info(data), "original_data": data}