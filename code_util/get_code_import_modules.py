import sys
import io
import ast
import importlib
import traceback
from contextlib import redirect_stdout, redirect_stderr
import os
import json


def get_imported_modules(code_str):
    try:
        tree = ast.parse(code_str)
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    modules.add(n.name.split('.')[0])  # Handle cases like 'numpy.linalg'
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules.add(node.module.split('.')[0])
        return modules
    except Exception as e:
        return set()


def check_missing_modules(modules):
    missing = []
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            missing.append(str(e))
    return missing


def run_and_check_code(code_str):
    # Static analysis: Check for missing modules
    imported_modules = get_imported_modules(code_str)
    missing_modules = check_missing_modules(imported_modules)
    module_error = []

    # Log statically detected missing modules
    if missing_modules:
        module_error.extend(missing_modules)
    
    # Redirect stdout and stderr to capture output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Create a clean environment for execution
    local_vars = {}
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Execute the code
            exec(code_str, {}, local_vars)
        
        # If no errors, return success
        output = stdout_capture.getvalue()
        return module_error
    
    except ModuleNotFoundError as e:
        module_error.append(str(e))
        return module_error
    
    except Exception as e:
        return module_error
    
    finally:
        # Clean up
        stdout_capture.close()
        stderr_capture.close()


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

    import_error = []
    for idx, item in enumerate(data):
        if isinstance(item, dict):
            code = item['code']
            ie = run_and_check_code(code)
            if ie:
                import_error.extend(ie)

    return import_error


def process_folder(folder_path: str):
    import_errors = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                import_error = process_json_file(file_path)
                import_errors.extend(import_error)

    import_errors = list(set(import_errors))

    with open('./import_errors.txt', 'w') as f:
        for error in import_errors:
            f.write(f"{error}\n")


if __name__ == '__main__':
    # Specify the folder path containing the code files
    folder_path = '../result_code'
    if os.path.isdir(folder_path):
        process_folder(folder_path)
    else:
        print("Invalid folder path.")