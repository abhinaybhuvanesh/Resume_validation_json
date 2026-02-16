import sys
import json
from src.validator import ResumeValidator

def main():
    validator = ResumeValidator()
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            results = [validator.validate(item) for item in data]
            print(json.dumps(results, indent=2))
        else:
            print(json.dumps(validator.validate(data), indent=2))
    else:
        data = json.load(sys.stdin)
        if isinstance(data, list):
            results = [validator.validate(item) for item in data]
            print(json.dumps(results, indent=2))
        else:
            print(json.dumps(validator.validate(data), indent=2))

if __name__ == "__main__":
    main()