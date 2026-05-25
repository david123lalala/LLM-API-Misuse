import os
import javalang
import json

# List of common crypto-related classes
crypto_apis = []

def uses_crypto_api(java_code):
    try:
        tree = javalang.parse.parse(java_code)
    except javalang.parser.JavaSyntaxError:
        return False

    for _, node in tree.filter(javalang.tree.Import):
        if any(api in node.path for api in crypto_apis):
            return True
    for _, node in tree.filter(javalang.tree.MethodInvocation):
        if any(api in node.member for api in crypto_apis):
            return True
    for _, node in tree.filter(javalang.tree.FieldDeclaration):
        if any(api in node.type.name for api in crypto_apis):
            return True
    for _, node in tree.filter(javalang.tree.ClassCreator):
        if any(api in node.type.name for api in crypto_apis):
            return True
    
    return False

def analyze_folder(folder_path):
    all_java_files = 0
    crypto_files = {}
    non_crypto_files = {}
    crypto_file_paths = []  # List to store paths of crypto API files
    non_crypto_to_crypto_paths = []  # Detailed paths for non-crypto files calling crypto API files
    crypto_to_non_crypto_paths = []  # Detailed paths for crypto files calling non-crypto files

    # Traverse directory and classify files
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".java") and "test" not in file_name.lower():
                all_java_files += 1
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding="utf-8") as file:
                    java_code = file.read()
                    if uses_crypto_api(java_code):
                        crypto_files[file_name] = file_path
                        crypto_file_paths.append(file_path)
                    else:
                        non_crypto_files[file_name] = file_path

    for file_name, file_path in non_crypto_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            tree = javalang.parse.parse(code)
            calls_crypto = False
            for _, invocation in tree.filter(javalang.tree.MethodInvocation):
                if any(os.path.basename(crypto_file).split('.')[0] in invocation.member for crypto_file in crypto_file_paths):
                    calls_crypto = True
                    break
            if calls_crypto and file_path not in crypto_file_paths:
                non_crypto_to_crypto_paths.append(file_path)
        except javalang.parser.JavaSyntaxError:
            print(f"Syntax error in {file_name}, skipping.")

    for file_name, file_path in crypto_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            tree = javalang.parse.parse(code)
            calls_non_crypto = False
            for _, invocation in tree.filter(javalang.tree.MethodInvocation):
                if any(os.path.basename(non_crypto_file).split('.')[0] in invocation.member for non_crypto_file in non_crypto_files.values()):
                    calls_non_crypto = True
                    break
            if calls_non_crypto and file_path not in crypto_file_paths:
                crypto_to_non_crypto_paths.append(file_path)
        except javalang.parser.JavaSyntaxError:
            print(f"Syntax error in {file_name}, skipping.")

    return {
        "all_count": all_java_files,
        "crypto_count": len(crypto_file_paths),
        "non_crypto_to_crypto_count": len(non_crypto_to_crypto_paths),
        "crypto_to_non_crypto_count": len(crypto_to_non_crypto_paths),
        "crypto_file_paths": crypto_file_paths,
        "non_crypto_to_crypto_paths": non_crypto_to_crypto_paths,
        "crypto_to_non_crypto_paths": crypto_to_non_crypto_paths
    }

def save_results_to_json(results, folder_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{folder_name}_analysis_results.json")
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_path}")

# Usage
folder_path_list = []

output_dir=''

for folder_path in folder_path_list:
    folder_name = os.path.basename(folder_path)
    print('*********** Analyzing:', folder_path)
    results = analyze_folder(folder_path)
    save_results_to_json(results, folder_name, output_dir)

