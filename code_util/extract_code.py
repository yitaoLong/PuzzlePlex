import os
import json
import re


def extract_python_code(content: str) -> str:
    """Extracts the first Python code block from the given string."""
    match = re.search(r'```python(.*?)```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return ''


def process_json_file(file_path: str):
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
            return

    if not isinstance(data, list):
        print(f"Expected a list in {file_path}, but got {type(data)}")
        return

    modified = False
    for idx, item in enumerate(data):
        if isinstance(item, dict) and item.get('code', '') == '':
            try:
                content = item['llm_history'][0][-1]['content']
                code = extract_python_code(content)
                if code:
                    item['code'] = code
                    modified = True
                    print(f"Extracted code from {file_path} (item {item['index']})")
                else:
                    print(f"No Python code found in {file_path} (item {item['index']})")
            except (KeyError, IndexError, TypeError) as e:
                print(f"Error accessing llm_history content in {file_path} (item {item['index']}): {e}")
    
    if modified:
        with open(file_path, 'w') as f:
            try:
                json.dump(data, f, indent=4)
                print(f"Modified {file_path} and saved changes.")
            except Exception as e:
                print(f"Error writing to file {file_path}: {e}")


def process_folder(folder_path: str):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)


if __name__ == '__main__':
    # Specify the folder path containing the code files
    folder_path = '../result_code'
    if os.path.isdir(folder_path):
        process_folder(folder_path)
    else:
        print("Invalid folder path.")
