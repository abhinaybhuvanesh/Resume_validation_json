import json
import sys

def parse_input(source=None):
    if isinstance(source, dict):
        return source
    if isinstance(source, str):
        try:
            with open(source, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {str(e)}")
    try:
        if not sys.stdin.isatty():
            return json.load(sys.stdin)
    except Exception as e:
        raise ValueError(f"Error reading JSON from stdin: {str(e)}")
    raise ValueError("No valid JSON input provided")

def normalize_batch(input_data):
    if isinstance(input_data, list):
        return input_data
    if isinstance(input_data, dict):
        return [input_data]
    raise ValueError("Invalid JSON format. Expected object or list.")