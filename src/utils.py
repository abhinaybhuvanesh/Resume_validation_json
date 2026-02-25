from datetime import datetime
import re

def validate_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return False
    date_str = date_str.strip()
    if date_str.lower() in ("null", "none", ""):
        return False
    formats = [
        "%Y-%m-%d", "%Y-%m", "%Y",
        "%d/%m/%Y", "%m/%d/%Y",
        "%d-%m-%Y", "%m-%d-%Y",
        "%Y/%m/%d",
        "%b %Y", "%B %Y",
        "%d %b %Y", "%d %B %Y",
        "%b %d, %Y", "%B %d, %Y",
        "%Y.%m.%d", "%d.%m.%Y"
    ]
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except (ValueError, TypeError):
            continue
    return False

def parse_date(date_str):
    if not date_str:
        return None
    date_str = str(date_str).strip()
    if date_str.lower() in ("null", "none", ""):
        return None
    formats = [
        "%Y-%m-%d", "%Y-%m", "%Y",
        "%d/%m/%Y", "%m/%d/%Y",
        "%d-%m-%Y", "%m-%d-%Y",
        "%Y/%m/%d",
        "%b %Y", "%B %Y",
        "%d %b %Y", "%d %B %Y",
        "%b %d, %Y", "%B %d, %Y",
        "%Y.%m.%d", "%d.%m.%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def calculate_days(start, end):
    s = parse_date(start)
    e = parse_date(end)
    if s and e:
        return (e - s).days
    return 0

def validate_url(url):
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if url.lower() in ("null", "none", ""):
        return False
    pattern = re.compile(
        r'^(https?://)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z]{2,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
        re.IGNORECASE
    )
    return bool(re.match(pattern, url))

def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if email.lower() in ("null", "none", ""):
        return False
    pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(re.match(pattern, email))

def validate_phone(phone):
    if not phone:
        return False
    phone = str(phone).strip()
    if phone.lower() in ("null", "none", ""):
        return False
    cleaned = re.sub(r'\D', '', phone)
    if not cleaned.isdigit():
        return False
    return 10 <= len(cleaned) <= 13

def validate_percentage(value):
    if not value:
        return False
    value = str(value).strip()
    match = re.search(r'^\s*(\d+\.?\d*)\s*%?\s*$', value)
    if match:
        try:
            num = float(match.group(1))
            return 0 <= num <= 100
        except:
            return False
    return False

def validate_cgpa(value):
    if not value:
        return False
    value = str(value).strip()
    frac_match = re.search(r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)', value)
    if frac_match:
        try:
            num = float(frac_match.group(1))
            denom = float(frac_match.group(2))
            if denom == 10:
                return 0 <= num <= 10
            elif denom == 4:
                return 0 <= num <= 4
            else:
                return 0 <= num <= denom
        except:
            return False
    num_match = re.search(r'^\s*(\d+\.?\d*)\s*$', value)
    if num_match:
        try:
            num = float(num_match.group(1))
            return 0 <= num <= 10
        except:
            return False
    return False

def is_null_or_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        if value.strip().lower() in ("null", "none", ""):
            return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False

def extract_email_from_object(obj):
    if isinstance(obj, dict):
        email_fields = ["email", "emails", "mail", "e-mail", "emailId", "email_id","gmail"]
        for field in email_fields:
            if field in obj:
                val = obj[field]
                if isinstance(val, str) and validate_email(val):
                    return val
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and validate_email(item):
                            return item
        for val in obj.values():
            result = extract_email_from_object(val)
            if result != "unknown":
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = extract_email_from_object(item)
            if result != "unknown":
                return result
    return "unknown"

def extract_phone_from_object(obj):
    if isinstance(obj, dict):
        phone_fields = ["phone", "phone_number", "mobile", "contact", "telephone", "tel","mobile_number","phone_no"]
        for field in phone_fields:
            if field in obj:
                val = obj[field]
                if isinstance(val, str) and validate_phone(val):
                    return val
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and validate_phone(item):
                            return item
        for val in obj.values():
            result = extract_phone_from_object(val)
            if result != "unknown":
                return result
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str) and validate_phone(item):
                return item

            result = extract_phone_from_object(item)
            if result != "unknown":
                return result
    return "unknown"