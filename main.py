import sys
import json
from src.validator import ResumeValidator

def main():
    validator = ResumeValidator()
    try:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
        if isinstance(data, list):
            results = [validator.validate(item) for item in data]
        else:
            results = validator.validate(data)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {sys.argv[1]}"}), file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()