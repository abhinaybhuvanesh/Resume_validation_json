from datetime import datetime
import re

def validate_date(date_str):
    try:
        datetime.strptime(str(date_str), "%Y-%m-%d")
        return True
    except:
        return False

def calculate_days(start_date, end_date):
    try:
        start = datetime.strptime(str(start_date), "%Y-%m-%d")
        end = datetime.strptime(str(end_date), "%Y-%m-%d")
        return (end - start).days
    except:
        return 0

def validate_url(url):
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if url == "null" or not url:
        return False
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', re.IGNORECASE)
    return bool(re.match(pattern, url))