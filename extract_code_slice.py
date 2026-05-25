import os
import json
import javalang

# Define the crypto APIs to check for
CRYPTO_APIS = []

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()
    try:
        return javalang.parse.parse(java_code)
    except javalang.parser.JavaSyntaxError:
        print(f"Syntax error in {file_path}, skipping.")
        return None

def extract_method_code(class_node, method_name):
    for member in class_node.body:
        if isinstance(member, javalang.tree.MethodDeclaration) and member.name == method_name:
            return str(member)  # Convert the method node to string representation
    return None

def extract_code_snippets(classes_info, slice_data):
    snippets = {}
    for method in slice_data:
        class_name, method_name = method.split('.')
        if class_name not in snippets:
            snippets[class_name] = {}
        method_code = extract_method_code(classes_info[class_name], method_name)
        if method_code:
            snippets[class_name][method_name] = method_code
    return snippets

def filter_crypto_apis(java_code):
    found_apis = []
    for api in CRYPTO_APIS:
        if api in java_code:
            found_apis.append(api)
    return found_apis

def create_output_json(output_json_path):
    """Create the output JSON file if it doesn't exist."""
    if not os.path.exists(output_json_path):
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump([], json_file)  # Initialize with an empty list
    print(f"Output JSON file created at: {output_json_path}")

def analyze_files(json_input_path, output_json_path):
    create_output_json(output_json_path)  
    analysis_data_list = load_json(json_input_path)
    results = []

    for analysis_data in analysis_data_list:
        file_path = analysis_data["file_path"]
        
        # Parse the Java file
        classes_info = parse_java_file(file_path)
        if classes_info is None:
            continue
        
        # Extract classes information
        classes_info_dict = {}
        for _, class_node in classes_info.filter(javalang.tree.ClassDeclaration):
            class_name = class_node.name
            classes_info_dict[class_name] = class_node

        slice_A_snippets = extract_code_snippets(classes_info_dict, analysis_data["slice_A"])
        
        static_variables = analysis_data["static_variables"]
        function_calls = analysis_data["function_calls"]

        with open(file_path, 'r', encoding='utf-8') as file:
            java_code = file.read()
        found_crypto_apis = filter_crypto_apis(java_code)

        results.append({
            "file_path": file_path,
            "slice_A_snippets": slice_A_snippets,
            "static_variables": static_variables,
            "function_calls": function_calls,
            'crypto_API': found_crypto_apis
        })

    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_json_path}")





input_path_list = []

output_path_list = []

for input_path, output_path in zip(input_path_list, output_path_list):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Input file does not exist: {input_path}")
        continue

    try:
        analyze_files(input_path, output_path)
    except Exception as e:
        print(f"Error analyzing {input_path}: {e}")
